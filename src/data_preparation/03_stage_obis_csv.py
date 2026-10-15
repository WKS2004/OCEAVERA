"""Validate an OBIS raw CSV and record its provenance without copying the data."""

import argparse
import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW_OBIS_ROOT = (ROOT / "data" / "raw" / "obis").resolve()
MANIFEST_PATH = ROOT / "data" / "interim" / "obis" / "cleaning" / "source_validation_manifest.json"
MANIFEST_FORMAT = "oceavera-obis-interim-source-validation-v2"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_csv(path: Path) -> tuple[int, int]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        header = next(reader, None)
        if not header:
            raise ValueError("The OBIS CSV has no header.")
        columns = len(header)
        rows = 0
        for row_number, row in enumerate(reader, start=2):
            if len(row) != columns:
                raise ValueError(
                    f"CSV row {row_number} has {len(row)} fields; expected {columns}."
                )
            rows += 1
    return rows, columns


def write_manifest(manifest: dict[str, object]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{MANIFEST_PATH.name}.",
            suffix=".tmp",
            dir=MANIFEST_PATH.parent,
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            json.dump(manifest, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, MANIFEST_PATH)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def validate(source_value: str) -> dict[str, object]:
    supplied = Path(source_value)
    source = (supplied if supplied.is_absolute() else ROOT / supplied).resolve()
    if not source.is_relative_to(RAW_OBIS_ROOT) or not source.is_file():
        raise ValueError("Input must be a CSV file inside data/raw/obis/.")
    if source.suffix.lower() != ".csv":
        raise ValueError("Input must have a .csv extension.")

    before = source.stat()
    rows, columns = inspect_csv(source)
    digest = sha256(source)
    after = source.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("The raw CSV changed during validation.")

    manifest = {
        "format": MANIFEST_FORMAT,
        "source": {
            "path": source.relative_to(ROOT).as_posix(),
            "sha256": digest,
            "bytes": after.st_size,
            "row_count": rows,
            "column_count": columns,
        },
        "operation": "CSV structure and source fingerprint recorded; raw data was not copied or changed",
    }
    write_manifest(manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a selected OBIS raw CSV and record its provenance."
    )
    parser.add_argument(
        "--obis-csv",
        required=True,
        help="CSV path inside data/raw/obis/",
    )
    args = parser.parse_args()
    result = validate(args.obis_csv)
    source = result["source"]
    print(f"Validated source: {source['path']}")
    print(f"Shape: {source['row_count']:,} rows x {source['column_count']:,} columns")
    print(f"SHA-256: {source['sha256']}")
    print(f"Manifest: {MANIFEST_PATH.relative_to(ROOT).as_posix()}")
    print("Raw CSV was not copied or changed.")


if __name__ == "__main__":
    main()
