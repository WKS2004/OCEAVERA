"""Download every OBIS Area 230 occurrence page as unchanged JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://api.obis.org/v3/occurrence"
AREA_ID = "230"
PAGE_SIZE = 1000
TIMEOUT_SECONDS = 60
MAX_ATTEMPTS = 3
CHUNK_SIZE = 64 * 1024
ROOT = Path(__file__).resolve().parents[2]
JSON_ROOT = ROOT / "data" / "raw" / "obis" / "json"
QUERY = {
    "areaid": AREA_ID,
    "absence": "include",
    "dropped": "include",
}


class DownloadError(Exception):
    """Raised when a complete, verifiable API export cannot be made."""


class PageRequestError(DownloadError):
    """Request failure carrying the measured response-body bytes by attempt."""

    def __init__(self, message: str, attempts: list[dict[str, object]]) -> None:
        super().__init__(message)
        self.attempts = attempts


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def format_bytes(byte_count: int) -> str:
    amount = float(byte_count)
    for unit in ("bytes", "KiB", "MiB", "GiB", "TiB"):
        if amount < 1024 or unit == "TiB":
            if unit == "bytes":
                return f"{byte_count:,} bytes"
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{byte_count:,} bytes"


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    minutes, remaining_seconds = divmod(int(seconds), 60)
    return f"{minutes:,} min {remaining_seconds:02d} sec"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_json_atomic(path: Path, value: object) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
    temporary.replace(path)


def write_bytes_atomic(path: Path, value: bytes) -> None:
    temporary = path.with_name(path.name + ".part")
    with temporary.open("wb") as stream:
        stream.write(value)
        stream.flush()
    temporary.replace(path)


def fetch_page(
    parameters: dict[str, str], page_number: int
) -> tuple[bytes, list[dict[str, object]]]:
    """Fetch one page sequentially and record response-body bytes per try."""
    url = f"{API_URL}?{urlencode(parameters)}"
    attempts: list[dict[str, object]] = []

    for attempt_number in range(1, MAX_ATTEMPTS + 1):
        received = 0
        status: int | None = None
        try:
            request = Request(
                url,
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "identity",
                    "User-Agent": "OCEAVERA OBIS Area 230 data intake",
                },
            )
            chunks: list[bytes] = []
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                status = response.status
                while True:
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    received += len(chunk)
                    chunks.append(chunk)
            attempts.append({
                "page": page_number,
                "attempt": attempt_number,
                "http_status": status,
                "response_body_bytes": received,
            })
            return b"".join(chunks), attempts
        except HTTPError as error:
            status = error.code
            try:
                received += len(error.read())
            except OSError:
                pass
            retryable = error.code == 429 or error.code >= 500
            detail = f"HTTP {error.code}"
        except (URLError, TimeoutError, OSError) as error:
            retryable = True
            detail = f"{type(error).__name__}: {error}"

        attempts.append({
            "page": page_number,
            "attempt": attempt_number,
            "http_status": status,
            "response_body_bytes": received,
            "error": detail,
        })
        if not retryable or attempt_number == MAX_ATTEMPTS:
            raise PageRequestError(
                f"Area 230 API page {page_number} failed: {detail}", attempts
            )
        delay = 2 ** (attempt_number - 1)
        print(
            f"[WARN] Page {page_number:,} request failed ({detail}). "
            f"Retrying in {delay} seconds "
            f"(attempt {attempt_number}/{MAX_ATTEMPTS}).",
            file=sys.stderr,
            flush=True,
        )
        time.sleep(delay)

    raise PageRequestError(f"Area 230 API page {page_number} failed", attempts)


def new_manifest(run_id: str) -> dict[str, object]:
    return {
        "format": "obis-area-230-json-download-v1",
        "run_id": run_id,
        "status": "in_progress",
        "publisher": "Ocean Biodiversity Information System",
        "endpoint": API_URL,
        "query": {
            **QUERY,
            "page_size": PAGE_SIZE,
            "fields_parameter": "omitted; retain every field returned by the API",
            "record_limit": None,
            "taxon_filter": None,
            "date_filter": None,
            "depth_filter": None,
        },
        "started_at_utc": now_utc(),
        "completed_at_utc": None,
        "expected_records": None,
        "records_downloaded": 0,
        "unique_record_ids": 0,
        "duplicate_record_ids": 0,
        "response_body_bytes": 0,
        "request_attempts": [],
        "pages": [],
        "failed_response_bodies": [],
    }


def manifest_path(run_dir: Path) -> Path:
    return run_dir / "manifest.json"


def save_manifest(run_dir: Path, manifest: dict[str, object]) -> None:
    manifest["updated_at_utc"] = now_utc()
    attempts = manifest["request_attempts"]
    manifest["response_body_bytes"] = sum(
        int(item.get("response_body_bytes", 0)) for item in attempts
    )
    write_json_atomic(manifest_path(run_dir), manifest)


def validate_run_path(run_dir: Path) -> Path:
    root = JSON_ROOT.resolve()
    resolved = run_dir.resolve()
    if not resolved.is_relative_to(root):
        raise DownloadError("Resume directory must be inside data/raw/obis/json")
    if not resolved.is_dir():
        raise DownloadError(f"Resume directory does not exist: {resolved}")
    return resolved


def load_resume(run_dir: Path) -> tuple[dict[str, object], set[str]]:
    run_dir = validate_run_path(run_dir)
    path = manifest_path(run_dir)
    if not path.is_file():
        raise DownloadError("Resume directory has no manifest.json")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("format") != "obis-area-230-json-download-v1":
        raise DownloadError("Unsupported Area 230 manifest format")
    query = manifest.get("query")
    if not isinstance(query, dict) or query.get("areaid") != AREA_ID:
        raise DownloadError("Resume manifest does not describe Area 230")
    if query.get("absence") != "include" or query.get("dropped") != "include":
        raise DownloadError("Resume manifest omits absence or dropped records")
    if manifest.get("status") == "complete":
        raise DownloadError("This run is already complete; it will not be downloaded again")

    seen: set[str] = set()
    record_count = 0
    duplicate_count = 0
    pages = manifest.get("pages")
    if not isinstance(pages, list):
        raise DownloadError("Resume manifest has an invalid page list")
    for page_number, entry in enumerate(pages, start=1):
        name = entry.get("file")
        if not isinstance(name, str) or Path(name).name != name:
            raise DownloadError("Resume manifest contains an unsafe page path")
        page_path = run_dir / name
        raw = page_path.read_bytes()
        if sha256_bytes(raw) != entry.get("sha256"):
            raise DownloadError(f"Page checksum mismatch: {name}")
        page = json.loads(raw)
        batch = page.get("results")
        if not isinstance(batch, list) or len(batch) != entry.get("record_count"):
            raise DownloadError(f"Page record count mismatch: {name}")
        if page_number > 1 and entry.get("after") != pages[page_number - 2].get(
            "last_id"
        ):
            raise DownloadError(f"Page cursor chain mismatch: {name}")
        record_count += len(batch)
        for record in batch:
            if (
                not isinstance(record, dict)
                or record.get("id") is None
                or str(record.get("id")) == ""
            ):
                raise DownloadError(f"Page has a record without an OBIS ID: {name}")
            record_id = str(record["id"])
            if record_id in seen:
                duplicate_count += 1
            seen.add(record_id)
        if batch and str(batch[-1].get("id")) != entry.get("last_id"):
            raise DownloadError(f"Page cursor does not match its last record: {name}")

    if record_count != manifest.get("records_downloaded"):
        raise DownloadError("Resume manifest total does not match its page files")
    manifest["unique_record_ids"] = len(seen)
    manifest["duplicate_record_ids"] = duplicate_count
    return manifest, seen


def write_invalid_response(
    run_dir: Path, page_number: int, body: bytes, manifest: dict[str, object]
) -> None:
    name = f"invalid-response-page-{page_number:05d}-{len(manifest['failed_response_bodies']) + 1:02d}.json"
    write_bytes_atomic(run_dir / name, body)
    manifest["failed_response_bodies"].append({
        "file": name,
        "response_body_bytes": len(body),
        "sha256": sha256_bytes(body),
    })
    save_manifest(run_dir, manifest)


def download(run_dir: Path, manifest: dict[str, object], seen: set[str]) -> int:
    pages = manifest["pages"]
    attempts_log = manifest["request_attempts"]
    expected_total = manifest.get("expected_records")
    record_count = int(manifest["records_downloaded"])
    duplicate_count = int(manifest["duplicate_record_ids"])

    while expected_total is None or record_count < int(expected_total):
        page_number = len(pages) + 1
        after = str(pages[-1]["last_id"]) if pages else "-1"
        parameters = {
            **QUERY,
            "size": str(PAGE_SIZE),
            "after": after,
        }
        if pages:
            parameters["total"] = "false"

        page_file = run_dir / f"page-{page_number:05d}.json"
        recovered_page = page_file.exists()
        if recovered_page:
            # A crash can occur after the response and its request-byte log are
            # saved but before the page is added to the manifest. Reuse that
            # verified response instead of spending network data a second time.
            body = page_file.read_bytes()
            prior_success = any(
                item.get("page") == page_number
                and isinstance(item.get("http_status"), int)
                and 200 <= item["http_status"] < 300
                and item.get("response_body_bytes") == len(body)
                for item in attempts_log
            )
            if not prior_success:
                raise DownloadError(
                    f"Untracked page file exists and will not be overwritten or trusted: {page_file.name}"
                )
        else:
            try:
                body, attempts = fetch_page(parameters, page_number)
            except PageRequestError as error:
                attempts_log.extend(error.attempts)
                save_manifest(run_dir, manifest)
                raise
            attempts_log.extend(attempts)
            save_manifest(run_dir, manifest)

        page = None
        try:
            page = json.loads(body)
        except json.JSONDecodeError:
            write_invalid_response(run_dir, page_number, body, manifest)
            raise DownloadError(f"API page {page_number} was not valid JSON")
        if not isinstance(page, dict) or not isinstance(page.get("results"), list):
            write_invalid_response(run_dir, page_number, body, manifest)
            raise DownloadError(f"API page {page_number} has no results array")

        batch = page["results"]
        if not pages:
            total = page.get("total")
            if type(total) is not int or total < 0:
                write_invalid_response(run_dir, page_number, body, manifest)
                raise DownloadError("The first API page did not report a valid total")
            expected_total = total
            manifest["expected_records"] = total
        elif isinstance(page.get("total"), int) and page["total"] != expected_total:
            write_invalid_response(run_dir, page_number, body, manifest)
            raise DownloadError("The API total changed during pagination")

        if not batch and record_count != expected_total:
            write_invalid_response(run_dir, page_number, body, manifest)
            raise DownloadError("The API returned an empty page before its reported total")
        if record_count + len(batch) > int(expected_total):
            write_invalid_response(run_dir, page_number, body, manifest)
            raise DownloadError("The API returned more records than its reported total")

        record_ids: list[str] = []
        for record in batch:
            if (
                not isinstance(record, dict)
                or record.get("id") is None
                or str(record.get("id")) == ""
            ):
                write_invalid_response(run_dir, page_number, body, manifest)
                raise DownloadError(f"API page {page_number} contains a record without an ID")
            record_ids.append(str(record["id"]))

        first_id = record_ids[0] if record_ids else None
        last_id = record_ids[-1] if record_ids else None
        entry = {
            "file": page_file.name,
            "after": after,
            "record_count": len(batch),
            "first_id": first_id,
            "last_id": last_id,
            "response_body_bytes": len(body),
            "sha256": sha256_bytes(body),
        }
        if not recovered_page:
            write_bytes_atomic(page_file, body)
        pages.append(entry)
        record_count += len(batch)
        for record_id in record_ids:
            if record_id in seen:
                duplicate_count += 1
            seen.add(record_id)
        manifest["records_downloaded"] = record_count
        manifest["unique_record_ids"] = len(seen)
        manifest["duplicate_record_ids"] = duplicate_count
        save_manifest(run_dir, manifest)

        total_records = int(expected_total)
        total_pages = max(1, (total_records + PAGE_SIZE - 1) // PAGE_SIZE)
        percent_complete = (
            100.0 if total_records == 0 else record_count / total_records * 100
        )
        stored_bytes = sum(int(item["response_body_bytes"]) for item in pages)
        print(
            f"[PROGRESS] Page {page_number:,}/{total_pages:,} | "
            f"{record_count:,}/{total_records:,} records "
            f"({percent_complete:.1f}%) | "
            f"{format_bytes(stored_bytes)} of raw JSON saved.",
            flush=True,
        )
        if batch:
            after = str(batch[-1]["id"])
        elif record_count == expected_total:
            break

    if record_count != expected_total:
        raise DownloadError(
            f"Downloaded {record_count} records; API reported {expected_total}"
        )
    if len(seen) != expected_total or duplicate_count:
        raise DownloadError(
            f"Completeness check found {duplicate_count} repeated IDs and "
            f"{len(seen)} unique IDs for {expected_total} API records; raw pages retained"
        )

    manifest["status"] = "complete"
    manifest["completed_at_utc"] = now_utc()
    save_manifest(run_dir, manifest)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download every OBIS occurrence returned for Area 230.",
        epilog=(
            "Examples:\n"
            "  python src/data_collection/obis_occurrences.py\n"
            "  python src/data_collection/obis_occurrences.py --resume "
            "data/raw/obis/json/<run-directory>"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--resume",
        type=Path,
        help="resume an incomplete Area 230 JSON run directory under data/raw/obis/json",
    )
    args = parser.parse_args()
    started_at = time.perf_counter()

    try:
        JSON_ROOT.mkdir(parents=True, exist_ok=True)
        if args.resume:
            run_dir = validate_run_path(args.resume)
            manifest, seen = load_resume(run_dir)
            manifest["status"] = "in_progress"
            manifest.pop("error", None)
            save_manifest(run_dir, manifest)
        else:
            run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            run_dir = JSON_ROOT / f"area-230-{run_id}"
            run_dir.mkdir(parents=True, exist_ok=False)
            manifest = new_manifest(run_id)
            seen = set()
            save_manifest(run_dir, manifest)

        run_path = run_dir.relative_to(ROOT).as_posix()
        print("OCEAVERA | OBIS Area 230 occurrence download")
        print("Scope: all taxa; absence and dropped records included; no record filters.")
        print(f"Run mode: {'resume' if args.resume else 'new download'}")
        print(f"Raw JSON folder: {run_path}")
        if manifest.get("expected_records") is not None:
            print(
                f"API total: {int(manifest['expected_records']):,} records; "
                f"already saved: {int(manifest['records_downloaded']):,}."
            )
        else:
            print("Checking the live API total while retrieving the first page.")
        print()

        download(run_dir, manifest, seen)
        stored_bytes = sum(
            int(item["response_body_bytes"]) for item in manifest["pages"]
        )
        print("\n[OK] Download completed and verified.")
        print(f"  Records: {int(manifest['records_downloaded']):,}")
        print(f"  Unique record IDs: {int(manifest['unique_record_ids']):,}")
        print(f"  Duplicate record IDs: {int(manifest['duplicate_record_ids']):,}")
        print(f"  Pages saved: {len(manifest['pages']):,}")
        print(f"  Raw JSON size: {format_bytes(stored_bytes)}")
        print(f"  Run folder: {run_path}")
        print(
            f"  Manifest: "
            f"{manifest_path(run_dir).relative_to(ROOT).as_posix()}"
        )
        print(f"  Elapsed: {format_duration(time.perf_counter() - started_at)}")
        print("\nNext step - convert this run to CSV:")
        print(
            "  python src/data_collection/obis_json_to_csv.py "
            f"--json-run {run_path}"
        )
        return 0
    except KeyboardInterrupt:
        if "run_dir" in locals() and "manifest" in locals():
            manifest["status"] = "interrupted"
            manifest["error"] = "Interrupted; completed JSON pages remain available to resume"
            save_manifest(run_dir, manifest)
            run_path = run_dir.relative_to(ROOT).as_posix()
            print(
                "\n[WARN] Download interrupted. Completed JSON pages are preserved.",
                file=sys.stderr,
            )
            print(f"  Run folder: {run_path}", file=sys.stderr)
            print(
                "  Resume with: python src/data_collection/obis_occurrences.py "
                f"--resume {run_path}",
                file=sys.stderr,
            )
        else:
            print("\n[WARN] Download interrupted before a run was created.", file=sys.stderr)
        return 130
    except (DownloadError, HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
        if "run_dir" in locals() and "manifest" in locals():
            manifest["status"] = "failed"
            manifest["error"] = f"{type(error).__name__}: {error}"
            save_manifest(run_dir, manifest)
        print(f"\n[ERROR] OBIS Area 230 download did not complete: {error}", file=sys.stderr)
        if "run_dir" in locals():
            print(
                f"  Run folder: {run_dir.relative_to(ROOT).as_posix()}",
                file=sys.stderr,
            )
        if (
            "run_dir" in locals()
            and "manifest" in locals()
            and manifest.get("status") != "complete"
        ):
            print("  Completed raw pages are preserved.", file=sys.stderr)
            print(
                "  Resume with: python src/data_collection/obis_occurrences.py "
                f"--resume {run_dir.relative_to(ROOT).as_posix()}",
                file=sys.stderr,
            )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
