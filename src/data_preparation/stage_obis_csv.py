"""Validate a selected OBIS raw CSV and copy it to a stable interim phase path.

The copy preserves every source byte, row and field. This utility performs
structural validation only; it does not apply scientific cleaning rules.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RAW_OBIS_ROOT = (ROOT / "data" / "raw" / "obis").resolve()
INTERIM_DIR = ROOT / "data" / "interim" / "obis" / "source_validation"
OUTPUT_PATH = INTERIM_DIR / "occurrences.csv"
MANIFEST_PATH = INTERIM_DIR / "manifest.json"
MANIFEST_FORMAT = "oceavera-obis-interim-source-validation-v1"


class StageError(Exception):
    """Raised when the selected OBIS CSV cannot be safely staged."""


def resolve_raw_csv(value: str) -> Path:
    """Resolve a selected CSV and require it to be inside data/raw/obis."""
    supplied = Path(value)
    candidate = supplied if supplied.is_absolute() else ROOT / supplied
    resolved = candidate.resolve()
    if not resolved.is_relative_to(RAW_OBIS_ROOT):
        raise StageError("The input CSV must be inside the repository's data/raw/obis directory")
    if not resolved.is_file():
        raise StageError(f"Input CSV does not exist or is not a file: {value}")
    if resolved.suffix.lower() != ".csv":
        raise StageError(f"Input must have a .csv extension: {value}")
    return resolved


def inspect_csv(path: Path) -> dict[str, int]:
    """Count records and columns while rejecting malformed row widths."""
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.reader(stream, strict=True)
            header = next(reader, None)
            if not header:
                raise StageError(f"CSV is empty: {path.name}")
            columns = len(header)
            rows = 0
            for rows, record in enumerate(reader, start=1):
                if len(record) != columns:
                    raise StageError(
                        f"Malformed CSV row {rows + 1} in {path.name}: "
                        f"expected {columns} columns, found {len(record)}"
                    )
    except (UnicodeDecodeError, csv.Error) as error:
        raise StageError(f"Cannot parse CSV {path.name}: {error}") from error
    return {"row_count": rows, "column_count": columns}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_verified(source: Path, destination: Path, source_hash: str) -> tuple[str, int]:
    """Copy bytes through a temporary file, verifying before atomic replace."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    byte_count = 0
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f"{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            with source.open("rb") as source_stream:
                for chunk in iter(lambda: source_stream.read(1024 * 1024), b""):
                    temporary.write(chunk)
                    digest.update(chunk)
                    byte_count += len(chunk)
            temporary.flush()
            os.fsync(temporary.fileno())

        copied_hash = digest.hexdigest()
        if copied_hash != source_hash:
            raise StageError(f"Input changed while it was being copied: {source.name}")
        if sha256_file(temporary_path) != source_hash:
            raise StageError(f"Staged copy checksum mismatch: {destination.name}")
        temporary_path.replace(destination)
        temporary_path = None
        return copied_hash, byte_count
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def read_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        return {"format": MANIFEST_FORMAT}
    try:
        value = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise StageError(f"Cannot read OBIS interim manifest: {error}") from error
    if not isinstance(value, dict) or value.get("format") != MANIFEST_FORMAT:
        raise StageError("OBIS interim manifest has an unexpected format")
    return value


def write_manifest(value: dict[str, Any]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f"{MANIFEST_PATH.name}.",
            suffix=".tmp",
            dir=MANIFEST_PATH.parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(value, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        temporary_path.replace(MANIFEST_PATH)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def stage(source: Path) -> dict[str, Any]:
    profile = inspect_csv(source)
    source_hash = sha256_file(source)
    manifest = read_manifest()
    output_hash, byte_count = copy_verified(source, OUTPUT_PATH, source_hash)
    output_profile = inspect_csv(OUTPUT_PATH)
    if output_profile != profile:
        raise StageError("Staged CSV structure does not match the selected raw file")
    if output_hash != source_hash:
        raise StageError("Staged CSV checksum does not match the selected raw file")

    manifest["source"] = {
        "path": source.relative_to(ROOT).as_posix(),
        "sha256": source_hash,
    }
    manifest["output"] = {
        "path": OUTPUT_PATH.relative_to(ROOT).as_posix(),
        "sha256": output_hash,
        "bytes": byte_count,
        **profile,
    }
    manifest["operation"] = "structural validation and byte-for-byte copy; no row or field changes"
    write_manifest(manifest)
    return manifest["output"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the selected OBIS raw CSV and stage an unchanged copy at "
            "a stable, timestamp-free interim phase path"
        )
    )
    parser.add_argument(
        "--obis-csv",
        required=True,
        help="selected OBIS CSV path inside data/raw/obis/",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = stage(resolve_raw_csv(args.obis_csv))
    except (OSError, StageError) as error:
        parser.error(str(error))

    print(
        f"OBIS: {result['row_count']} rows, {result['column_count']} columns; "
        f"{result['path']}"
    )
    print(f"Manifest: {MANIFEST_PATH.relative_to(ROOT).as_posix()}")
    print("No cleaning, filtering, or row removal was performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
