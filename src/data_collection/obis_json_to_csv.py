"""Convert a complete, verified OBIS Area 230 JSON run to CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


ROOT = Path(__file__).resolve().parents[2]
JSON_ROOT = ROOT / "data" / "raw" / "obis" / "json"
CSV_ROOT = ROOT / "data" / "raw" / "obis" / "csv"
EXPECTED_FORMAT = "obis-area-230-json-download-v1"
DATA_ACCESS_URL = "https://obis.org/data/access/"
DATA_ACCESS_FIELDS = {
    "id",
    "dataset_id",
    "decimalLongitude",
    "decimalLatitude",
    "date_start",
    "date_mid",
    "date_end",
    "date_year",
    "scientificName",
    "originalScientificName",
    "minimumDepthInMeters",
    "maximumDepthInMeters",
    "coordinateUncertaintyInMeters",
    "flags",
    "dropped",
    "absence",
    "shoredistance",
    "bathymetry",
    "sst",
    "sss",
    "marine",
    "brackish",
    "freshwater",
    "terrestrial",
    "taxonRank",
    "AphiaID",
    "redlist_category",
    "superdomain",
    "domain",
    "kingdom",
    "subkingdom",
    "infrakingdom",
    "phylum",
    "phylum (division)",
    "subphylum (subdivision)",
    "subphylum",
    "infraphylum",
    "parvphylum",
    "gigaclass",
    "megaclass",
    "superclass",
    "class",
    "subclass",
    "infraclass",
    "subterclass",
    "superorder",
    "order",
    "suborder",
    "infraorder",
    "parvorder",
    "superfamily",
    "family",
    "subfamily",
    "supertribe",
    "tribe",
    "subtribe",
    "genus",
    "subgenus",
    "section",
    "subsection",
    "series",
    "species",
    "subspecies",
    "natio",
    "variety",
    "subvariety",
    "forma",
    "subforma",
}
COLUMN_ALIASES = {"AphiaID": "aphiaID"}


class ConversionError(Exception):
    """Raised when source JSON cannot be proven complete before conversion."""


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_atomic(path: Path, value: object) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
    temporary.replace(path)


def resolve_run(run_path: Path | None) -> tuple[Path, dict[str, object]]:
    if run_path is not None:
        resolved = run_path.resolve()
        if not resolved.is_relative_to(JSON_ROOT.resolve()):
            raise ConversionError("JSON run must be inside data/raw/obis/json")
        candidates = [resolved]
    else:
        candidates = sorted(
            (path for path in JSON_ROOT.glob("area-230-*") if path.is_dir()),
            reverse=True,
        )

    for candidate in candidates:
        path = candidate / "manifest.json"
        if not path.is_file():
            continue
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if manifest.get("format") == EXPECTED_FORMAT and manifest.get("status") == "complete":
            return candidate, manifest
    raise ConversionError("No complete Area 230 JSON run was found")


def check_manifest(
    run_dir: Path, manifest: dict[str, object]
) -> tuple[list[str], int, list[str]]:
    query = manifest.get("query")
    if not isinstance(query, dict):
        raise ConversionError("JSON manifest has no query metadata")
    if (
        str(query.get("areaid")) != "230"
        or query.get("absence") != "include"
        or query.get("dropped") != "include"
        or query.get("record_limit") is not None
        or query.get("taxon_filter") is not None
        or query.get("date_filter") is not None
        or query.get("depth_filter") is not None
    ):
        raise ConversionError("JSON manifest does not describe the unrestricted Area 230 query")

    expected = manifest.get("expected_records")
    pages = manifest.get("pages")
    if not isinstance(expected, int) or isinstance(expected, bool) or not isinstance(pages, list):
        raise ConversionError("JSON manifest has invalid totals or page records")
    if (
        manifest.get("records_downloaded") != expected
        or manifest.get("unique_record_ids") != expected
        or manifest.get("duplicate_record_ids") != 0
    ):
        raise ConversionError("JSON manifest completeness totals do not agree")

    field_names: set[str] = set()
    record_count = 0
    seen_ids: set[str] = set()
    previous_last: str | None = None
    for number, entry in enumerate(pages, start=1):
        if not isinstance(entry, dict):
            raise ConversionError(f"Invalid page entry {number}")
        name = entry.get("file")
        if not isinstance(name, str) or Path(name).name != name:
            raise ConversionError(f"Unsafe page path in entry {number}")
        page_path = run_dir / name
        raw = page_path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry.get("sha256"):
            raise ConversionError(f"JSON page checksum mismatch: {name}")
        page = json.loads(raw)
        batch = page.get("results") if isinstance(page, dict) else None
        if not isinstance(batch, list) or len(batch) != entry.get("record_count"):
            raise ConversionError(f"JSON page record count mismatch: {name}")
        expected_after = previous_last if number > 1 else "-1"
        if entry.get("after") != expected_after:
            raise ConversionError(f"JSON cursor sequence mismatch: {name}")

        for record in batch:
            if not isinstance(record, dict):
                raise ConversionError(f"Non-object occurrence in {name}")
            record_id = record.get("id")
            if record_id is None or str(record_id) == "":
                raise ConversionError(f"Occurrence without an OBIS ID in {name}")
            normalized_id = str(record_id)
            if normalized_id in seen_ids:
                raise ConversionError(f"Repeated OBIS ID found in source pages: {normalized_id}")
            seen_ids.add(normalized_id)
            field_names.update(record.keys())

        if batch:
            first_id = str(batch[0]["id"])
            previous_last = str(batch[-1]["id"])
        else:
            first_id = None
            previous_last = None
        if first_id != entry.get("first_id") or previous_last != entry.get("last_id"):
            raise ConversionError(f"JSON page ID boundary mismatch: {name}")
        record_count += len(batch)

    if record_count != expected or len(seen_ids) != expected:
        raise ConversionError(
            f"Source pages contain {record_count} records and {len(seen_ids)} unique IDs; "
            f"the API reported {expected}"
        )
    if not pages and expected != 0:
        raise ConversionError("The manifest has no pages for a non-empty Area 230 result")
    fields_not_returned = sorted(DATA_ACCESS_FIELDS - field_names)
    field_names.update(DATA_ACCESS_FIELDS)
    for source_field in COLUMN_ALIASES.values():
        if source_field not in field_names:
            raise ConversionError(
                f"Access-page column alias source field is absent from API data: {source_field}"
            )
    return sorted(field_names), record_count, fields_not_returned


def csv_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def csv_value(record: dict[str, object], field: str) -> object:
    if field in record:
        return record[field]
    alias = COLUMN_ALIASES.get(field)
    return record.get(alias) if alias is not None else None


def iter_records(run_dir: Path, manifest: dict[str, object]) -> Iterator[dict[str, object]]:
    for entry in manifest["pages"]:
        page = json.loads((run_dir / entry["file"]).read_text(encoding="utf-8"))
        yield from page["results"]


def convert(
    run_dir: Path,
    manifest: dict[str, object],
    replace_existing: bool = False,
) -> dict[str, object]:
    fields, expected_count, fields_not_returned = check_manifest(run_dir, manifest)
    if not fields and expected_count:
        raise ConversionError("No occurrence fields were found in the downloaded JSON")

    CSV_ROOT.mkdir(parents=True, exist_ok=True)
    run_id = str(manifest["run_id"])
    output_path = CSV_ROOT / f"area-230-{run_id}.csv"
    receipt_path = CSV_ROOT / f"area-230-{run_id}.manifest.json"
    if output_path.exists() or receipt_path.exists():
        if not replace_existing or not output_path.is_file() or not receipt_path.is_file():
            raise ConversionError(
                f"CSV output already exists for run {run_id}; pass --replace-existing only to refresh this run's verified output"
            )
        existing_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if (
            existing_receipt.get("status") != "complete"
            or existing_receipt.get("source_json_run")
            != run_dir.relative_to(ROOT).as_posix()
        ):
            raise ConversionError(
                "Existing CSV receipt does not match this complete JSON run; refusing to replace it"
            )
    temporary_path = output_path.with_suffix(".csv.part")

    with temporary_path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=fields,
            extrasaction="raise",
            lineterminator="\n",
        )
        writer.writeheader()
        written = 0
        for record in iter_records(run_dir, manifest):
            writer.writerow({field: csv_cell(csv_value(record, field)) for field in fields})
            written += 1
        stream.flush()

    if written != expected_count:
        temporary_path.unlink(missing_ok=True)
        raise ConversionError(f"Wrote {written} CSV records; expected {expected_count}")

    # Verify every row and column against the retained raw JSON before publishing.
    with temporary_path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != fields:
            temporary_path.unlink(missing_ok=True)
            raise ConversionError("CSV header verification failed")
        checked = 0
        for source_record, csv_record in zip(iter_records(run_dir, manifest), reader):
            expected_row = {field: csv_cell(csv_value(source_record, field)) for field in fields}
            if csv_record != expected_row:
                temporary_path.unlink(missing_ok=True)
                raise ConversionError(f"CSV value verification failed at row {checked + 1}")
            checked += 1
        if checked != expected_count or next(reader, None) is not None:
            temporary_path.unlink(missing_ok=True)
            raise ConversionError("CSV row count verification failed")

    receipt = {
        "format": "obis-area-230-csv-v1",
        "status": "complete",
        "publisher": "Ocean Biodiversity Information System",
        "source_json_run": run_dir.relative_to(ROOT).as_posix(),
        "source_manifest_sha256": sha256_file(run_dir / "manifest.json"),
        "converted_at_utc": now_utc(),
        "query": manifest["query"],
        "records": expected_count,
        "unique_record_ids": manifest["unique_record_ids"],
        "columns": fields,
        "column_count": len(fields),
        "obis_data_access_fields": sorted(DATA_ACCESS_FIELDS),
        "access_fields_not_returned_as_api_keys": fields_not_returned,
        "column_aliases": COLUMN_ALIASES,
        "schema_reference": DATA_ACCESS_URL,
        "csv": output_path.relative_to(ROOT).as_posix(),
        "csv_bytes": temporary_path.stat().st_size,
        "csv_sha256": sha256_file(temporary_path),
        "conversion": {
            "all top-level fields across every JSON record included": True,
            "all OBIS Data Access schema columns included": True,
            "records filtered or deduplicated": False,
            "nested arrays and objects": "compact UTF-8 JSON strings",
            "AphiaID capitalization": "documented AphiaID column mirrors API aphiaID; original API column is retained",
            "null values": "empty CSV cells; unchanged in retained source JSON",
            "encoding": "UTF-8",
        },
    }
    temporary_path.replace(output_path)
    if replace_existing:
        write_json_atomic(receipt_path, receipt)
    else:
        with receipt_path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(receipt, stream, ensure_ascii=False, indent=2)
            stream.write("\n")

    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-run",
        type=Path,
        help="specific complete JSON run directory; default is the newest complete run",
    )
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="replace an existing verified CSV/receipt pair only when it refers to the same JSON run",
    )
    args = parser.parse_args()
    try:
        run_dir, manifest = resolve_run(args.json_run)
        receipt = convert(run_dir, manifest, replace_existing=args.replace_existing)
        print(json.dumps(receipt, indent=2))
        return 0
    except (ConversionError, OSError, ValueError, csv.Error) as error:
        print(f"OBIS Area 230 CSV conversion failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
