"""Clean the OBIS Area 230 occurrence CSV without changing source values."""

import csv
import hashlib
import json
import math
import os
import re
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW_OBIS_ROOT = (ROOT / "data" / "raw" / "obis").resolve()
SOURCE_MANIFEST_PATH = ROOT / "data" / "interim" / "obis" / "cleaning" / "source_validation_manifest.json"
OUTPUT_DIRECTORY = ROOT / "data" / "interim" / "obis" / "cleaning"
OUTPUT_PATH = OUTPUT_DIRECTORY / "occurrences_cleaned.csv"
COLUMN_REPORT_PATH = OUTPUT_DIRECTORY / "column_completeness.json"
CLEANING_SUMMARY_PATH = OUTPUT_DIRECTORY / "cleaning_summary.json"

MIN_COLUMN_COMPLETENESS = 0.10

PROTECTED_COLUMNS = {
    "id", "occurrenceID", "dataset_id", "datasetName",
    "scientificName", "originalScientificName", "species", "speciesid",
    "AphiaID", "aphiaID", "scientificNameID", "taxonRank",
    "occurrenceStatus", "absence", "basisOfRecord",
    "decimalLatitude", "decimalLongitude", "coordinateUncertaintyInMeters",
    "eventDate", "date_year", "date_start", "date_end", "date_mid",
    "bathymetry", "shoredistance", "sst", "sss",
    "flags", "dropped", "marine",
    "license", "eventID", "samplingProtocol", "samplingEffort",
    "occurrenceRemarks", "habitat", "locality",
}

# These exact values occur in fields where they cannot represent valid data.
# Other text such as "unknown" is retained because it may be an explicit value.
MISSING_SENTINELS = {
    "day": {"null"},
    "islandGroup": {"null"},
    "lifeStage": {"na"},
    "modified": {"null"},
    "month": {"null"},
    "originalScientificName": {"na"},
    "specificEpithet": {"na"},
    "verbatimElevation": {"null"},
    "year": {"null"},
}

TAXON_ID_FIELDS = (
    "scientificName", "originalScientificName", "species", "speciesid",
    "AphiaID", "aphiaID", "scientificNameID", "taxonID",
    "genus", "genusid", "family", "familyid", "order", "orderid",
    "class", "classid", "phylum", "phylumid", "kingdom", "kingdomid",
)
DATE_FIELDS = ("eventDate", "date_year", "date_start", "date_end", "date_mid")
OPTIONAL_REPORT_FIELDS = (
    "species", "speciesid", "taxonRank", *DATE_FIELDS,
    "coordinateUncertaintyInMeters", "samplingEffort", "samplingProtocol",
    "habitat", "license",
)
REVIEW_FLAGS = {"ON_LAND", "NO_DEPTH", "NO_MATCH", "NO_ACCEPTED_NAME", "DEPTH_EXCEEDS_BATH"}
EXCLUSION_REASONS = (
    "OBIS dropped status",
    "invalid coordinates",
    "no usable taxonomic identification",
    "confirmed exact duplicate",
)


def is_missing_sentinel(value: str | None, field: str) -> bool:
    if value is None:
        return False
    return value.strip().casefold() in MISSING_SENTINELS.get(field, set())


def has_value(value: str | None, field: str = "") -> bool:
    return value is not None and bool(value.strip()) and not is_missing_sentinel(value, field)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repeat_summary(values: list[object]) -> tuple[int, int, int]:
    counts = Counter(values)
    repeated = [count for count in counts.values() if count > 1]
    return len(repeated), sum(repeated), sum(count - 1 for count in repeated)


def coordinate_problem(row: list[str], indexes: dict[str, int]) -> str | None:
    latitude = row[indexes["decimalLatitude"]].strip() if "decimalLatitude" in indexes else ""
    longitude = row[indexes["decimalLongitude"]].strip() if "decimalLongitude" in indexes else ""
    if not has_value(latitude, "decimalLatitude") or not has_value(longitude, "decimalLongitude"):
        return "missing latitude or longitude"
    try:
        latitude_value = float(latitude)
        longitude_value = float(longitude)
    except ValueError:
        return "non-numeric coordinates"
    if not math.isfinite(latitude_value) or not math.isfinite(longitude_value):
        return "non-finite coordinates"
    if not -90 <= latitude_value <= 90 or not -180 <= longitude_value <= 180:
        return "coordinates outside legal ranges"
    return None


def taxon_is_identified(row: list[str], indexes: dict[str, int]) -> bool:
    return any(
        name in indexes and has_value(row[indexes[name]], name)
        for name in TAXON_ID_FIELDS
    )


def flag_counts(rows: list[list[str]], indexes: dict[str, int]) -> Counter[str]:
    counts: Counter[str] = Counter({flag: 0 for flag in REVIEW_FLAGS})
    if "flags" not in indexes:
        return counts
    for row in rows:
        tokens = set(re.findall(r"[A-Z_]+", row[indexes["flags"]].upper()))
        counts.update(tokens & REVIEW_FLAGS)
    return counts


def status_counts(rows: list[list[str]], indexes: dict[str, int], field: str) -> Counter[str]:
    if field not in indexes:
        return Counter()
    return Counter(row[indexes[field]].strip().casefold() or "blank" for row in rows)


def verify_source_validation() -> dict[str, object]:
    manifest = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("format") != "oceavera-obis-interim-source-validation-v2":
        raise ValueError("The source-validation manifest has an unexpected format.")
    source = manifest.get("source", {})
    raw_path = (ROOT / source.get("path", "")).resolve()
    if not raw_path.is_relative_to(RAW_OBIS_ROOT) or not raw_path.is_file():
        raise ValueError("The raw source path in the source-validation manifest is unavailable.")
    source_hash = file_sha256(raw_path)
    if source_hash != source.get("sha256"):
        raise ValueError("The raw OBIS CSV does not match its source-validation manifest hash.")
    if raw_path.stat().st_size != source.get("bytes"):
        raise ValueError("The raw OBIS CSV size does not match its source-validation manifest.")

    return {
        "manifest_path": SOURCE_MANIFEST_PATH.relative_to(ROOT).as_posix(),
        "raw_path": source["path"],
        "raw_sha256": source_hash,
        "source_rows": source.get("row_count"),
        "source_columns": source.get("column_count"),
        "source_bytes": source.get("bytes"),
    }


def optional_missingness(rows: list[list[str]], indexes: dict[str, int]) -> dict[str, object]:
    total = len(rows)
    by_field = {}
    for field in OPTIONAL_REPORT_FIELDS:
        if field not in indexes:
            continue
        missing = sum(not has_value(row[indexes[field]], field) for row in rows)
        by_field[field] = {
            "missing_records": missing,
            "percent_missing": round(100 * missing / total, 2) if total else 0.0,
        }

    available_dates = [field for field in DATE_FIELDS if field in indexes]
    missing_all_dates = sum(
        not any(has_value(row[indexes[field]], field) for field in available_dates)
        for row in rows
    )
    species_fields = [field for field in ("species", "speciesid") if field in indexes]
    missing_species_fields = sum(
        not any(has_value(row[indexes[field]], field) for field in species_fields)
        for row in rows
    )
    return {
        "fields": by_field,
        "all_observation_date_fields_missing": {
            "missing_records": missing_all_dates,
            "percent_missing": round(100 * missing_all_dates / total, 2) if total else 0.0,
        },
        "both_species_and_speciesid_missing": {
            "missing_records": missing_species_fields,
            "percent_missing": round(100 * missing_species_fields / total, 2) if total else 0.0,
        },
    }


def write_temporary_file(target: Path, write_content) -> Path:
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="") as stream:
            write_content(stream)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
    return temporary_path


def clean_occurrences() -> dict[str, object]:
    source_info = verify_source_validation()
    source_path = ROOT / source_info["raw_path"]
    with source_path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source, strict=True)
        header = next(reader, None)
        if not header:
            raise ValueError("The OBIS source CSV has no header.")
        if len(header) != len(set(header)):
            raise ValueError("The OBIS source CSV contains duplicate column names.")

        rows = []
        usable_counts = [0] * len(header)
        sentinel_counts = [0] * len(header)
        for row_number, row in enumerate(reader, start=2):
            if len(row) != len(header):
                raise ValueError(f"OBIS source row {row_number} has an unexpected number of fields.")
            rows.append(row)
            for index, value in enumerate(row):
                if is_missing_sentinel(value, header[index]):
                    sentinel_counts[index] += 1
                if has_value(value, header[index]):
                    usable_counts[index] += 1

    row_count = len(rows)
    if row_count == 0:
        raise ValueError("The OBIS source CSV has no data rows.")
    if (row_count, len(header)) != (source_info["source_rows"], source_info["source_columns"]):
        raise ValueError("The raw OBIS CSV dimensions do not match its source-validation manifest.")
    if file_sha256(source_path) != source_info["raw_sha256"]:
        raise ValueError("The raw OBIS CSV changed while it was being cleaned.")

    indexes = {name: index for index, name in enumerate(header)}
    column_statistics = []
    retained_indexes = []
    removed_columns = []
    protected_below_threshold = []

    for index, name in enumerate(header):
        populated = usable_counts[index]
        missing = row_count - populated
        sentinel_missing = sentinel_counts[index]
        percentage = 100 * populated / row_count
        meets_threshold = populated / row_count >= MIN_COLUMN_COMPLETENESS
        protected = name in PROTECTED_COLUMNS
        keep = protected or meets_threshold
        if protected and not meets_threshold:
            reason = "protected below threshold"
        elif protected:
            reason = "protected and meets threshold"
        elif meets_threshold:
            reason = "completeness threshold"
        else:
            reason = "removed below threshold"
        column_statistics.append((
            name, populated, missing, sentinel_missing, percentage,
            100 * missing / row_count, protected, keep, reason,
        ))
        if keep:
            retained_indexes.append(index)
        else:
            removed_columns.append((name, populated, percentage))
        if protected and not meets_threshold:
            protected_below_threshold.append(name)

    retained_columns = [header[index] for index in retained_indexes]
    missing_protected = sorted(PROTECTED_COLUMNS - set(header))
    original_duplicates = repeat_summary([tuple(row) for row in rows])
    reduced_duplicates = repeat_summary([
        tuple(row[index] for index in retained_indexes) for row in rows
    ])
    occurrence_id_repeats = repeat_summary([
        row[indexes["occurrenceID"]].strip()
        for row in rows
        if "occurrenceID" in indexes and has_value(row[indexes["occurrenceID"]], "occurrenceID")
    ])
    species_date_combinations = []
    for row in rows:
        fields = ("species", "decimalLatitude", "decimalLongitude", "eventDate")
        if all(name in indexes and has_value(row[indexes[name]], name) for name in fields):
            species_date_combinations.append(tuple(row[indexes[name]].strip() for name in fields))
    species_location_date_repeats = repeat_summary(species_date_combinations)

    excluded = Counter()
    coordinate_reasons = Counter()
    cleaned_rows = []
    seen_original_rows = set()

    for row in rows:
        if "dropped" in indexes and row[indexes["dropped"]].strip().casefold() == "true":
            excluded["OBIS dropped status"] += 1
            continue

        problem = coordinate_problem(row, indexes)
        if problem:
            excluded["invalid coordinates"] += 1
            coordinate_reasons[problem] += 1
            continue

        if not taxon_is_identified(row, indexes):
            excluded["no usable taxonomic identification"] += 1
            continue

        original_record = tuple(row)
        if original_record in seen_original_rows:
            excluded["confirmed exact duplicate"] += 1
            continue
        seen_original_rows.add(original_record)
        cleaned_rows.append(row)

    cleaned_occurrence_id_repeats = repeat_summary([
        row[indexes["occurrenceID"]].strip()
        for row in cleaned_rows
        if "occurrenceID" in indexes and has_value(row[indexes["occurrenceID"]], "occurrenceID")
    ])
    cleaned_species_date_combinations = []
    for row in cleaned_rows:
        fields = ("species", "decimalLatitude", "decimalLongitude", "eventDate")
        if all(name in indexes and has_value(row[indexes[name]], name) for name in fields):
            cleaned_species_date_combinations.append(tuple(row[indexes[name]].strip() for name in fields))

    return {
        "header": header,
        "row_count": row_count,
        "source_info": source_info,
        "retained_columns": retained_columns,
        "retained_indexes": retained_indexes,
        "removed_columns": removed_columns,
        "protected_below_threshold": protected_below_threshold,
        "missing_protected": missing_protected,
        "column_statistics": column_statistics,
        "original_duplicates": original_duplicates,
        "reduced_duplicates": reduced_duplicates,
        "occurrence_id_repeats": occurrence_id_repeats,
        "cleaned_occurrence_id_repeats": cleaned_occurrence_id_repeats,
        "species_location_date_repeats": species_location_date_repeats,
        "cleaned_species_location_date_repeats": repeat_summary(cleaned_species_date_combinations),
        "excluded": excluded,
        "coordinate_reasons": coordinate_reasons,
        "cleaned_rows": cleaned_rows,
        "optional_missingness": optional_missingness(cleaned_rows, indexes),
        "indexes": indexes,
    }


def cleaning_run_summary(result: dict[str, object], output_hashes: dict[str, str]) -> dict[str, object]:
    exclusion_counts = {reason: result["excluded"][reason] for reason in EXCLUSION_REASONS}
    exclusion_counts["total"] = sum(exclusion_counts.values())
    return {
        "format": "oceavera-obis-cleaning-run-v1",
        "source": result["source_info"],
        "criteria": {
            "minimum_column_completeness": MIN_COLUMN_COMPLETENESS,
            "missing_value_sentinels": {
                field: sorted(values) for field, values in sorted(MISSING_SENTINELS.items())
            },
            "protected_columns": sorted(PROTECTED_COLUMNS),
            "taxonomy_eligibility_fields": list(TAXON_ID_FIELDS),
            "row_eligibility": [
                "Exclude records explicitly marked dropped=true by OBIS.",
                "Require finite latitude and longitude within legal coordinate ranges.",
                "Require at least one usable retained taxonomic name or identifier at any rank, including taxonID.",
                "Remove only exact duplicates across all original source columns after the other eligibility checks.",
                "Do not exclude records for missing dates, species/speciesid, taxonRank, coordinate uncertainty, or other optional data.",
            ],
        },
        "columns": {
            "source_count": len(result["header"]),
            "retained_count": len(result["retained_columns"]),
            "removed_count": len(result["removed_columns"]),
            "protected_missing_from_source": result["missing_protected"],
            "protected_below_threshold": result["protected_below_threshold"],
            "sentinel_missing_counts": [
                {"column": values[0], "records": values[3]}
                for values in result["column_statistics"] if values[3]
            ],
            "removed_columns": [
                {"column": name, "usable_records": count, "percent_populated": round(pct, 2)}
                for name, count, pct in result["removed_columns"]
            ],
        },
        "rows": {
            "source_count": result["row_count"],
            "retained_count": len(result["cleaned_rows"]),
            "exclusion_counts": exclusion_counts,
            "coordinate_exclusion_details": dict(sorted(result["coordinate_reasons"].items())),
            "optional_data_missingness": result["optional_missingness"],
        },
        "duplicate_diagnostics": {
            "exact_source_rows_groups_total_extra": list(result["original_duplicates"]),
            "exact_rows_after_column_reduction_groups_total_extra": list(result["reduced_duplicates"]),
            "repeated_occurrenceID_source_groups_total_extra": list(result["occurrence_id_repeats"]),
            "repeated_occurrenceID_output_groups_total_extra": list(result["cleaned_occurrence_id_repeats"]),
            "repeated_species_coordinate_date_source_groups_total_extra": list(result["species_location_date_repeats"]),
            "repeated_species_coordinate_date_output_groups_total_extra": list(
                result["cleaned_species_location_date_repeats"]
            ),
        },
        "preserved_values": {
            "marine": dict(sorted(status_counts(result["cleaned_rows"], result["indexes"], "marine").items())),
            "absence": dict(sorted(status_counts(result["cleaned_rows"], result["indexes"], "absence").items())),
            "quality_flags": dict(sorted(flag_counts(result["cleaned_rows"], result["indexes"]).items())),
        },
        "outputs": {
            "cleaned_csv": {
                "path": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "rows": len(result["cleaned_rows"]),
                "columns": len(result["retained_columns"]),
                "sha256": output_hashes[OUTPUT_PATH.name],
            },
            "column_completeness_json": {
                "path": COLUMN_REPORT_PATH.relative_to(ROOT).as_posix(),
                "rows": len(result["column_statistics"]),
                "columns": 9,
                "sha256": output_hashes[COLUMN_REPORT_PATH.name],
            },
        },
    }


def save_outputs(result: dict[str, object]) -> dict[str, object]:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    temporary_paths = []
    try:
        def write_column_report(stream):
            report = {
                "format": "oceavera-obis-column-completeness-v1",
                "source_rows": result["row_count"],
                "minimum_completeness": MIN_COLUMN_COMPLETENESS,
                "columns": [
                    {
                        "column": values[0],
                        "usable_records": values[1],
                        "missing_records": values[2],
                        "missing_sentinel_records": values[3],
                        "percent_populated": round(values[4], 2),
                        "percent_missing": round(values[5], 2),
                        "protected": values[6],
                        "retained": values[7],
                        "retention_reason": values[8],
                    }
                    for values in result["column_statistics"]
                ],
            }
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")

        def write_cleaned_csv(stream):
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(result["retained_columns"])
            for row in result["cleaned_rows"]:
                writer.writerow([row[index] for index in result["retained_indexes"]])

        column_temp = write_temporary_file(COLUMN_REPORT_PATH, write_column_report)
        temporary_paths.append(column_temp)
        cleaned_temp = write_temporary_file(OUTPUT_PATH, write_cleaned_csv)
        temporary_paths.append(cleaned_temp)
        output_hashes = {
            COLUMN_REPORT_PATH.name: file_sha256(column_temp),
            OUTPUT_PATH.name: file_sha256(cleaned_temp),
        }
        run_summary = cleaning_run_summary(result, output_hashes)
        summary_temp = write_temporary_file(
            CLEANING_SUMMARY_PATH,
            lambda stream: (
                json.dump(run_summary, stream, indent=2, sort_keys=True),
                stream.write("\n"),
            ),
        )
        temporary_paths.append(summary_temp)

        # Each final file is replaced atomically; the summary is the final run marker.
        for temporary_path, target in (
            (cleaned_temp, OUTPUT_PATH),
            (column_temp, COLUMN_REPORT_PATH),
            (summary_temp, CLEANING_SUMMARY_PATH),
        ):
            os.replace(temporary_path, target)
            temporary_paths.remove(temporary_path)
        return run_summary
    finally:
        for temporary_path in temporary_paths:
            temporary_path.unlink(missing_ok=True)


def main() -> None:
    result = clean_occurrences()
    run_summary = save_outputs(result)
    retained_rows = len(result["cleaned_rows"])
    retained_columns = len(result["retained_columns"])
    excluded = run_summary["rows"]["exclusion_counts"]

    print(f"Source shape: {result['row_count']:,} rows x {len(result['header']):,} columns")
    print(
        f"Column cleaning: {retained_columns:,} retained, {len(result['removed_columns']):,} removed "
        f"at {MIN_COLUMN_COMPLETENESS:.0%} usable completeness"
    )
    print(
        "Protected below threshold: "
        + (", ".join(result["protected_below_threshold"]) or "none")
    )
    print("Rows excluded by first applicable rule:")
    for reason in EXCLUSION_REASONS:
        print(f"  {reason}: {excluded[reason]:,}")
    print(f"Final shape: {retained_rows:,} rows x {retained_columns:,} columns")
    print("Optional-data missingness: " + json.dumps(result["optional_missingness"], sort_keys=True))
    print("Output hashes: " + json.dumps(run_summary["outputs"], sort_keys=True))
    print(f"Cleaned CSV: {OUTPUT_PATH.relative_to(ROOT).as_posix()}")
    print(f"Column report: {COLUMN_REPORT_PATH.relative_to(ROOT).as_posix()}")
    print(f"Run summary: {CLEANING_SUMMARY_PATH.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
