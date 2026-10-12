"""Validate the current Bio-ORACLE NetCDF stage without duplicating the dataset.

The reader intentionally supports NetCDF classic and 64-bit-offset files using
only the Python standard library. It scans the existing interim products,
streams detailed per-product findings to a temporary spool, and promotes the
validated source-validation directory to cleaning by rename. NetCDF payloads
remain unchanged. Issues that cannot be resolved from source metadata are
recorded for review instead of being guessed or repaired.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import os
import re
import struct
import sys
import tempfile
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, BinaryIO, Iterable


ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = (ROOT / "data" / "raw" / "bio_oracle").resolve()
INTERIM_ROOT = (ROOT / "data" / "interim" / "bio_oracle").resolve()
SOURCE_STAGE = INTERIM_ROOT / "source_validation"
CLEANING_STAGE = INTERIM_ROOT / "cleaning"
MANIFEST_FORMAT = "oceavera-bio-oracle-cleaning-manifest-v2"
CLEANING_RULE_VERSION = "2026-10-12.3"
CLEANING_SUMMARY_FORMAT = "oceavera-bio-oracle-cleaning-summary-v2"
NETCDF_SIGNATURES = {b"CDF\x01": "classic", b"CDF\x02": "64-bit-offset"}
REFERENCE = {
    "netcdf_files": 356,
    "variable_instances": 2392,
    "distinct_environmental_variables": 139,
    "baseline_products": 55,
    "future_scenario_products": 300,
    "terrain_products": 1,
    "latitude_length": 178,
    "longitude_length": 165,
    "grid_spacing_degrees": 0.05,
    "marine_cells": 24503,
    "baseline_time_labels": [2000, 2010],
    "future_time_labels": [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090],
    "terrain_time_label": 1970,
}

NC_DIMENSION = 10
NC_VARIABLE = 11
NC_ATTRIBUTE = 12
TYPE_INFO: dict[int, tuple[str, str, int]] = {
    1: ("byte", "b", 1),
    2: ("char", "c", 1),
    3: ("short", "h", 2),
    4: ("int", "i", 4),
    5: ("float", "f", 4),
    6: ("double", "d", 8),
}
DEFAULT_FILL: dict[int, int | float | str] = {
    1: -127,
    2: "\x00",
    3: -32767,
    4: -2147483647,
    5: 9.969209968386869e36,
    6: 9.969209968386869e36,
}


class NetCDFError(ValueError):
    """Raised when a classic NetCDF payload is structurally invalid."""


def read_exact(stream: BinaryIO, count: int, label: str) -> bytes:
    value = stream.read(count)
    if len(value) != count:
        raise NetCDFError(f"Truncated NetCDF while reading {label}.")
    return value


def read_u32(stream: BinaryIO, label: str) -> int:
    return struct.unpack(">I", read_exact(stream, 4, label))[0]


def read_name(stream: BinaryIO, label: str) -> str:
    length = read_u32(stream, f"{label} name length")
    if length > 1_048_576:
        raise NetCDFError(f"Unreasonably long {label} name ({length} bytes).")
    raw = read_exact(stream, length, f"{label} name")
    padding = (-length) % 4
    if padding:
        read_exact(stream, padding, f"{label} name padding")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise NetCDFError(f"Invalid UTF-8 in {label} name.") from error


def read_typed_values(stream: BinaryIO, type_code: int, count: int, label: str) -> Any:
    if type_code not in TYPE_INFO:
        raise NetCDFError(f"Unsupported NetCDF classic type {type_code} in {label}.")
    type_name, code, item_size = TYPE_INFO[type_code]
    byte_count = count * item_size
    if byte_count > 64 * 1024 * 1024:
        raise NetCDFError(f"Unreasonably large NetCDF attribute {label}.")
    raw = read_exact(stream, byte_count, label)
    padding = (-byte_count) % 4
    if padding:
        read_exact(stream, padding, f"{label} padding")
    if type_name == "char":
        try:
            value = raw.decode("utf-8").rstrip("\x00")
        except UnicodeDecodeError:
            value = raw.decode("utf-8", errors="replace").rstrip("\x00")
        return value
    if count == 0:
        return []
    values = [entry[0] for entry in struct.iter_unpack(f">{code}", raw)]
    return values[0] if count == 1 else values


def read_attribute_list(stream: BinaryIO, label: str) -> dict[str, Any]:
    tag = read_u32(stream, f"{label} tag")
    count = read_u32(stream, f"{label} count")
    if tag == 0 and count == 0:
        return {}
    if tag != NC_ATTRIBUTE:
        raise NetCDFError(f"Invalid {label} tag {tag}.")
    if count > 100_000:
        raise NetCDFError(f"Unreasonably many attributes in {label}.")
    attributes: dict[str, Any] = {}
    for _ in range(count):
        name = read_name(stream, "attribute")
        type_code = read_u32(stream, f"{name} type")
        value_count = read_u32(stream, f"{name} value count")
        if name in attributes:
            raise NetCDFError(f"Duplicate attribute name {name!r} in {label}.")
        attributes[name] = read_typed_values(stream, type_code, value_count, name)
    return attributes


def read_list_header(stream: BinaryIO, expected_tag: int, label: str) -> int:
    tag = read_u32(stream, f"{label} tag")
    count = read_u32(stream, f"{label} count")
    if tag == 0 and count == 0:
        return 0
    if tag != expected_tag:
        raise NetCDFError(f"Invalid {label} tag {tag}; expected {expected_tag}.")
    if count > 1_000_000:
        raise NetCDFError(f"Unreasonably many entries in {label}.")
    return count


def parse_header(source: str, data: bytes | None = None) -> dict[str, Any]:
    """Parse the complete NetCDF classic header and validate array extents."""
    source_path = Path(source)
    if not source_path.is_absolute():
        source_path = ROOT / source_path
    if data is not None:
        stream: BinaryIO = io.BytesIO(data)
    else:
        stream = source_path.open("rb")
    with stream:
        signature = read_exact(stream, 4, "file signature")
        if signature not in NETCDF_SIGNATURES:
            if signature == b"CDF\x05":
                raise NetCDFError("CDF-5 is not supported by the dependency-free reader.")
            if signature[:2] == b"\x89H":
                raise NetCDFError("HDF5/NetCDF-4 is not supported by the dependency-free reader.")
            raise NetCDFError(f"Unrecognized NetCDF signature {signature!r}.")
        version = NETCDF_SIGNATURES[signature]
        record_count = read_u32(stream, "record count")

        dimension_count = read_list_header(stream, NC_DIMENSION, "dimension list")
        dimensions: list[dict[str, Any]] = []
        for _ in range(dimension_count):
            name = read_name(stream, "dimension")
            length = read_u32(stream, f"{name} dimension length")
            dimensions.append({"name": name, "length": length})
        if len({item["name"] for item in dimensions}) != len(dimensions):
            raise NetCDFError("Duplicate dimension names.")
        unlimited_ids = [index for index, item in enumerate(dimensions) if item["length"] == 0]
        if len(unlimited_ids) > 1:
            raise NetCDFError("NetCDF classic permits only one unlimited dimension.")
        unlimited_id = unlimited_ids[0] if unlimited_ids else None
        if record_count == 0xFFFFFFFF:
            raise NetCDFError("NetCDF record count is the streaming sentinel, not a finalized value.")
        for item in dimensions:
            if item["length"] == 0 and unlimited_id is None:
                raise NetCDFError("Invalid zero-length dimension.")
            if item["length"] == 0:
                item["length"] = record_count

        global_attributes = read_attribute_list(stream, "global attributes")
        variable_count = read_list_header(stream, NC_VARIABLE, "variable list")
        variables: list[dict[str, Any]] = []
        for _ in range(variable_count):
            name = read_name(stream, "variable")
            rank = read_u32(stream, f"{name} rank")
            if rank > 1024:
                raise NetCDFError(f"Unreasonably high rank for variable {name!r}.")
            dimension_ids = [read_u32(stream, f"{name} dimension id") for _ in range(rank)]
            if any(index >= len(dimensions) for index in dimension_ids):
                raise NetCDFError(f"Variable {name!r} references an unknown dimension.")
            attributes = read_attribute_list(stream, f"{name} attributes")
            type_code = read_u32(stream, f"{name} type")
            if type_code not in TYPE_INFO:
                raise NetCDFError(f"Unsupported NetCDF classic type {type_code} for {name!r}.")
            vsize = read_u32(stream, f"{name} stored size")
            if version == "64-bit-offset":
                begin = struct.unpack(">Q", read_exact(stream, 8, f"{name} begin offset"))[0]
            else:
                begin = read_u32(stream, f"{name} begin offset")
            shape = [dimensions[index]["length"] for index in dimension_ids]
            variables.append({
                "name": name,
                "dimension_ids": dimension_ids,
                "dimensions": [dimensions[index]["name"] for index in dimension_ids],
                "shape": shape,
                "attributes": attributes,
                "type_code": type_code,
                "type_name": TYPE_INFO[type_code][0],
                "vsize": vsize,
                "begin": begin,
            })
        if len({item["name"] for item in variables}) != len(variables):
            raise NetCDFError("Duplicate variable names.")
        by_name = {item["name"]: item for item in variables}
        for dimension in dimensions:
            coordinate = by_name.get(dimension["name"])
            if coordinate is not None and coordinate["dimensions"] != [dimension["name"]]:
                raise NetCDFError(f"Coordinate variable {dimension['name']!r} has inconsistent dimensions.")
        file_size = len(data) if data is not None else source_path.stat().st_size

    record_variables = [
        item for item in variables
        if unlimited_id is not None and item["dimension_ids"] and item["dimension_ids"][0] == unlimited_id
    ]
    record_stride = sum(item["vsize"] for item in record_variables)
    ranges: list[tuple[int, int, str]] = []
    for variable in variables:
        _, _, item_size = TYPE_INFO[variable["type_code"]]
        is_record = bool(variable["dimension_ids"] and unlimited_id is not None and variable["dimension_ids"][0] == unlimited_id)
        if is_record:
            per_record_count = math.prod(variable["shape"][1:])
            data_bytes = per_record_count * item_size
            expected_vsize = (data_bytes + 3) & ~3
            end = variable["begin"] if record_count == 0 else variable["begin"] + (record_count - 1) * record_stride + data_bytes
        else:
            element_count = math.prod(variable["shape"]) if variable["shape"] else 1
            data_bytes = element_count * item_size
            expected_vsize = (data_bytes + 3) & ~3
            end = variable["begin"] + data_bytes
        if variable["vsize"] not in {expected_vsize, 0xFFFFFFFF}:
            raise NetCDFError(
                f"Variable {variable['name']!r} stored size {variable['vsize']} disagrees with shape ({expected_vsize})."
            )
        if end > file_size:
            raise NetCDFError(f"Variable {variable['name']!r} extends beyond end of file.")
        variable["record_variable"] = is_record
        variable["data_bytes"] = data_bytes
        if data_bytes:
            ranges.append((variable["begin"], end, variable["name"]))
    fixed_ranges = sorted(
        (start, end, name) for start, end, name in ranges
        if not next(item for item in variables if item["name"] == name)["record_variable"]
    )
    for previous, current in zip(fixed_ranges, fixed_ranges[1:]):
        if current[0] < previous[1]:
            raise NetCDFError(f"Fixed data regions overlap: {previous[2]!r} and {current[2]!r}.")

    return {
        "format": version,
        "signature": signature.hex(),
        "record_count": record_count,
        "unlimited_dimension_id": unlimited_id,
        "record_stride": record_stride,
        "dimensions": dimensions,
        "global_attributes": global_attributes,
        "variables": variables,
        "file_size": file_size,
    }


def variable_segments(header: dict[str, Any], variable: dict[str, Any]) -> Iterable[tuple[int, int, int]]:
    """Yield (file offset, byte count, flattened element start) segments."""
    _, _, item_size = TYPE_INFO[variable["type_code"]]
    if variable["record_variable"]:
        per_record_count = math.prod(variable["shape"][1:])
        per_record_bytes = per_record_count * item_size
        for record in range(header["record_count"]):
            yield (
                variable["begin"] + record * header["record_stride"],
                per_record_bytes,
                record * per_record_count,
            )
    else:
        element_count = math.prod(variable["shape"]) if variable["shape"] else 1
        yield variable["begin"], element_count * item_size, 0


def attr_values(value: Any) -> list[Any]:
    return value if isinstance(value, list) else [value]


def compare_marker(value: float | int, marker: Any) -> bool:
    try:
        numeric_marker = float(marker)
    except (TypeError, ValueError):
        return False
    if math.isnan(numeric_marker):
        return isinstance(value, float) and math.isnan(value)
    return value == numeric_marker


def is_coordinate(variable: dict[str, Any]) -> bool:
    attributes = variable["attributes"]
    name = variable["name"].casefold()
    standard_name = str(attributes.get("standard_name", "")).casefold()
    axis = str(attributes.get("axis", "")).upper()
    units = str(attributes.get("units", "")).casefold()
    return (
        variable["dimensions"] == [variable["name"]]
        or name in {"lat", "latitude", "lon", "longitude", "time", "depth", "altitude"}
        or standard_name in {"latitude", "longitude", "time", "depth", "height", "altitude"}
        or axis in {"X", "Y", "Z", "T"}
        or "degrees_north" in units
        or "degrees_east" in units
    )


def is_spatial(variable: dict[str, Any], lat_dim: str | None, lon_dim: str | None) -> bool:
    dimensions = {name.casefold() for name in variable["dimensions"]}
    return (
        lat_dim is not None and lon_dim is not None
        and lat_dim.casefold() in dimensions and lon_dim.casefold() in dimensions
    )


def serialize(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, float) and not math.isfinite(value):
        return "NaN" if math.isnan(value) else ("Infinity" if value > 0 else "-Infinity")
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    return value


def stat_counter() -> dict[str, Any]:
    return {
        "total_elements": 0,
        "valid_finite_elements": 0,
        "declared_fill_elements": 0,
        "declared_missing_elements": 0,
        "nan_elements": 0,
        "positive_infinity_elements": 0,
        "negative_infinity_elements": 0,
        "valid_minimum": None,
        "valid_maximum": None,
    }


def update_stats(stats: dict[str, Any], value: float | int, is_fill: bool, is_missing: bool, scale: float, offset: float) -> None:
    stats["total_elements"] += 1
    if is_fill:
        stats["declared_fill_elements"] += 1
    elif is_missing:
        stats["declared_missing_elements"] += 1
    if isinstance(value, float) and math.isnan(value):
        stats["nan_elements"] += 1
        return
    if isinstance(value, float) and math.isinf(value):
        key = "positive_infinity_elements" if value > 0 else "negative_infinity_elements"
        stats[key] += 1
        return
    if is_fill or is_missing:
        return
    decoded = float(value) * scale + offset
    if not math.isfinite(decoded):
        return
    stats["valid_finite_elements"] += 1
    if stats["valid_minimum"] is None or decoded < stats["valid_minimum"]:
        stats["valid_minimum"] = decoded
    if stats["valid_maximum"] is None or decoded > stats["valid_maximum"]:
        stats["valid_maximum"] = decoded


def parse_time_origin(value: str) -> datetime | None:
    text = value.strip().replace(" UTC", "+00:00").replace("Z", "+00:00")
    if "T" not in text and " " not in text:
        text += "T00:00:00+00:00"
    elif " " in text and "T" not in text:
        text = text.replace(" ", "T", 1)
    try:
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def decode_time_labels(values: list[Any], attributes: dict[str, Any]) -> tuple[list[Any], str | None]:
    calendar = str(attributes.get("calendar", "standard")).casefold()
    units = str(attributes.get("units", ""))
    match = re.fullmatch(r"\s*(seconds?|minutes?|hours?|days?)\s+since\s+(.+?)\s*", units, re.I)
    if not match:
        if all(isinstance(value, (int, float)) and math.isfinite(value) and float(value).is_integer() for value in values):
            return [int(value) for value in values], "time units do not encode an offset from an origin"
        return [serialize(value) for value in values], "time labels could not be decoded from their units"
    origin = parse_time_origin(match.group(2))
    if origin is None:
        return [serialize(value) for value in values], "time origin could not be decoded"
    if calendar not in {"standard", "gregorian", "proleptic_gregorian", "julian"}:
        return [serialize(value) for value in values], f"calendar {calendar!r} is retained as numeric offsets"
    seconds = {"second": 1, "seconds": 1, "minute": 60, "minutes": 60,
               "hour": 3600, "hours": 3600, "day": 86400, "days": 86400}
    factor = seconds[match.group(1).casefold()]
    labels = []
    for value in values:
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            return [serialize(item) for item in values], "time coordinate contains a non-finite value"
        labels.append((origin + timedelta(seconds=float(value) * factor)).isoformat().replace("+00:00", "Z"))
    return labels, None


def coordinate_diagnostics(values: list[Any]) -> dict[str, Any]:
    numeric = [float(value) for value in values if isinstance(value, (int, float)) and math.isfinite(value)]
    unique = len(set(numeric)) == len(numeric)
    increasing = all(right > left for left, right in zip(numeric, numeric[1:]))
    decreasing = all(right < left for left, right in zip(numeric, numeric[1:]))
    deltas = [abs(right - left) for left, right in zip(numeric, numeric[1:])]
    spacing = sum(deltas) / len(deltas) if deltas else None
    spacing_deviation = max((abs(value - spacing) for value in deltas), default=0.0) if spacing is not None else None
    return {
        "count": len(values),
        "finite_count": len(numeric),
        "unique": unique,
        "strictly_monotonic": increasing or decreasing or len(numeric) <= 1,
        "ordering": "increasing" if increasing else ("decreasing" if decreasing else "nonmonotonic"),
        "minimum": min(numeric) if numeric else None,
        "maximum": max(numeric) if numeric else None,
        "mean_absolute_spacing": spacing,
        "maximum_spacing_deviation": spacing_deviation,
    }


def dimension_names(header: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    dims = {item["name"].casefold(): item["name"] for item in header["dimensions"]}
    lat = next((dims[name] for name in ("latitude", "lat") if name in dims), None)
    lon = next((dims[name] for name in ("longitude", "lon") if name in dims), None)
    time = next((dims[name] for name in ("time", "year") if name in dims), None)
    for variable in header["variables"]:
        standard_name = str(variable["attributes"].get("standard_name", "")).casefold()
        axis = str(variable["attributes"].get("axis", "")).upper()
        if standard_name == "latitude" or axis == "Y":
            lat = variable["dimensions"][0] if variable["dimensions"] else lat
        elif standard_name == "longitude" or axis == "X":
            lon = variable["dimensions"][0] if variable["dimensions"] else lon
        elif standard_name == "time" or axis == "T":
            time = variable["dimensions"][0] if variable["dimensions"] else time
    return lat, lon, time


def scan_variable(
    data: bytes,
    header: dict[str, Any],
    variable: dict[str, Any],
    *,
    lat_dim: str | None,
    lon_dim: str | None,
    time_dim: str | None,
    time_labels: list[Any] | None,
    marine_mask: list[bool] | None,
    retain_values: bool = False,
) -> dict[str, Any]:
    type_code = variable["type_code"]
    type_name, type_code_char, item_size = TYPE_INFO[type_code]
    attributes = variable["attributes"]
    element_count = math.prod(variable["shape"]) if variable["shape"] else 1
    digest = hashlib.sha256()
    if type_name == "char":
        raw_values = bytearray()
        for offset, byte_count, _ in variable_segments(header, variable):
            chunk = memoryview(data)[offset:offset + byte_count]
            digest.update(chunk)
            if retain_values:
                raw_values.extend(chunk)
        return {
            "total_elements": element_count,
            "valid_finite_elements": None,
            "declared_fill_elements": None,
            "declared_missing_elements": None,
            "nan_elements": 0,
            "positive_infinity_elements": 0,
            "negative_infinity_elements": 0,
            "valid_minimum": None,
            "valid_maximum": None,
            "data_sha256": digest.hexdigest(),
            "coordinate_values": raw_values.decode("utf-8", errors="replace").rstrip("\x00") if retain_values else None,
            "per_time_slice": [],
            "marine_domain_missing_elements": None,
        }

    stats = stat_counter()
    per_time: list[dict[str, Any]] = []
    time_position = variable["dimensions"].index(time_dim) if time_dim in variable["dimensions"] else None
    time_stride = math.prod(variable["shape"][time_position + 1:]) if time_position is not None else 0
    if time_position is not None:
        per_time = [stat_counter() for _ in range(variable["shape"][time_position])]
    fill_value = attributes.get("_FillValue", DEFAULT_FILL.get(type_code))
    fill_values = attr_values(fill_value) if fill_value is not None else []
    missing_values = attr_values(attributes.get("missing_value", []))
    scale = float(attributes.get("scale_factor", 1.0))
    offset = float(attributes.get("add_offset", 0.0))
    valid_range = attributes.get("valid_range")
    valid_min = attributes.get("valid_min")
    valid_max = attributes.get("valid_max")
    if valid_range is not None:
        range_values = attr_values(valid_range)
        declared_min = float(range_values[0]) if len(range_values) else None
        declared_max = float(range_values[-1]) if len(range_values) > 1 else None
    else:
        declared_min = float(valid_min) if valid_min is not None else None
        declared_max = float(valid_max) if valid_max is not None else None
    range_violations = 0
    marine_missing = 0
    marine_missing_locations: list[dict[str, Any]] = []
    marine_missing_locations_truncated = False
    outside_candidate_valid = 0
    coordinate_values: list[Any] | None = [] if retain_values else None
    spatial_positions: tuple[int, int, int, int] | None = None
    if marine_mask is not None and is_spatial(variable, lat_dim, lon_dim):
        lat_position = variable["dimensions"].index(lat_dim)
        lon_position = variable["dimensions"].index(lon_dim)
        n_lat = variable["shape"][lat_position]
        n_lon = variable["shape"][lon_position]
        if len(marine_mask) == n_lat * n_lon:
            spatial_positions = (
                lat_position,
                lon_position,
                math.prod(variable["shape"][lat_position + 1:]),
                math.prod(variable["shape"][lon_position + 1:]),
            )

    flat_index = 0
    unpacker = struct.Struct(f">{type_code_char}")
    chunk_target = max(item_size, (1024 * 1024 // item_size) * item_size)
    for offset_in_file, byte_count, segment_flat_start in variable_segments(header, variable):
        segment_index = 0
        while segment_index < byte_count:
            block_size = min(chunk_target, byte_count - segment_index)
            block_size -= block_size % item_size
            if block_size <= 0:
                block_size = item_size
            block = memoryview(data)[offset_in_file + segment_index:offset_in_file + segment_index + block_size]
            digest.update(block)
            for entry in struct.iter_unpack(f">{type_code_char}", block):
                value = entry[0]
                if coordinate_values is not None:
                    coordinate_values.append(value)
                is_fill = any(compare_marker(value, marker) for marker in fill_values)
                is_missing = any(compare_marker(value, marker) for marker in missing_values) and not is_fill
                update_stats(stats, value, is_fill, is_missing, scale, offset)
                if not is_fill and not is_missing and math.isfinite(float(value)):
                    if declared_min is not None and float(value) < declared_min:
                        range_violations += 1
                    if declared_max is not None and float(value) > declared_max:
                        range_violations += 1
                if time_position is not None:
                    current_index = flat_index
                    time_index = (current_index // time_stride) % variable["shape"][time_position] if time_stride else 0
                    update_stats(per_time[time_index], value, is_fill, is_missing, scale, offset)
                if spatial_positions is not None:
                    lat_position, lon_position, lat_stride, lon_stride = spatial_positions
                    row = (flat_index // lat_stride) % variable["shape"][lat_position]
                    column = (flat_index // lon_stride) % variable["shape"][lon_position]
                    candidate_domain = marine_mask[row * variable["shape"][lon_position] + column]
                    invalid_value = is_fill or is_missing or not math.isfinite(float(value))
                    if candidate_domain and invalid_value:
                        marine_missing += 1
                        if len(marine_missing_locations) < 100:
                            indices = {}
                            for dimension_position, dimension_name in enumerate(variable["dimensions"]):
                                stride = math.prod(variable["shape"][dimension_position + 1:])
                                indices[dimension_name] = (flat_index // stride) % variable["shape"][dimension_position] if stride else 0
                            marine_missing_locations.append({"dimension_indices": indices})
                        else:
                            marine_missing_locations_truncated = True
                    elif not candidate_domain and not invalid_value:
                        outside_candidate_valid += 1
                flat_index += 1
            segment_index += block_size

    if flat_index != element_count:
        raise NetCDFError(f"Variable {variable['name']!r} yielded {flat_index} values, expected {element_count}.")
    per_time_result = []
    for index, slice_stats in enumerate(per_time):
        label = time_labels[index] if time_labels is not None and index < len(time_labels) else index
        per_time_result.append({"time": serialize(label), **slice_stats})
    return {
        **stats,
        "data_sha256": digest.hexdigest(),
        "coordinate_values": coordinate_values,
        "per_time_slice": per_time_result,
        "marine_domain_missing_elements": marine_missing if spatial_positions is not None else None,
        "marine_domain_missing_locations": marine_missing_locations if spatial_positions is not None else None,
        "marine_domain_missing_locations_truncated": marine_missing_locations_truncated,
        "outside_candidate_domain_valid_elements": outside_candidate_valid if spatial_positions is not None else None,
        "declared_valid_range_violations": range_violations,
    }


def mask_value_mapping(attributes: dict[str, Any], observed_values: list[Any]) -> tuple[dict[str, bool] | None, str]:
    def value_key(value: Any) -> str:
        if isinstance(value, (int, float)) and math.isfinite(float(value)) and float(value).is_integer():
            return str(int(value))
        return str(value)

    meanings = str(attributes.get("flag_meanings", "")).split()
    values = attr_values(attributes.get("flag_values", []))
    if meanings and len(meanings) == len(values):
        mapping: dict[str, bool] = {}
        for raw_value, meaning in zip(values, meanings):
            token = meaning.casefold().replace("_", " ")
            if any(word in token for word in ("water", "ocean", "sea")):
                mapping[value_key(raw_value)] = True
            elif "land" in token:
                mapping[value_key(raw_value)] = False
        if mapping and any(value is True for value in mapping.values()) and any(value is False for value in mapping.values()):
            return mapping, "flag_values/flag_meanings"
    description = " ".join(str(attributes.get(key, "")) for key in ("long_name", "comment", "description", "standard_name"))
    description = description.casefold()
    patterns = (
        (r"(?:0\s*[=:]\s*land.{0,30}(?:1\s*[=:]\s*(?:water|sea|ocean))|land\s*=\s*0.{0,30}(?:water|sea|ocean)\s*=\s*1)", {"0": False, "1": True}),
        (r"(?:1\s*[=:]\s*land.{0,30}(?:0\s*[=:]\s*(?:water|sea|ocean))|land\s*=\s*1.{0,30}(?:water|sea|ocean)\s*=\s*0)", {"0": True, "1": False}),
    )
    for pattern, mapping in patterns:
        if re.search(pattern, description):
            return mapping, "explicit long_name/comment encoding"
    return None, "no explicit land/water value convention"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cleaner_fingerprint() -> dict[str, str]:
    return {
        "rule_version": CLEANING_RULE_VERSION,
        "script_sha256": sha256_file(Path(__file__).resolve()),
    }


def repo_file(value: str, allowed_root: Path, label: str) -> Path:
    path = (ROOT / value).resolve()
    if not path.is_relative_to(allowed_root) or not path.is_file():
        raise ValueError(f"{label} is missing or outside its allowed repository directory: {value}")
    return path


def interim_product_file(product: dict[str, Any]) -> Path:
    value = product.get("interim_payload")
    if not isinstance(value, str) or not value:
        raise ValueError(f"Current interim NetCDF path is missing for {product.get('dataset_id', 'unknown product')}.")
    return repo_file(value, INTERIM_ROOT, "current interim NetCDF product")


def load_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read {label} as UTF-8 JSON: {error}") from error
    if not isinstance(document, dict):
        raise ValueError(f"{label} must contain a JSON object.")
    return document, raw


def stage_path_for_current_root(value: str, stage_root: Path) -> str:
    """Map a staged path to the sole active stage after its directory is renamed."""
    value_path = Path(value)
    source_relative = SOURCE_STAGE.relative_to(ROOT)
    if value_path.is_relative_to(source_relative):
        value_path = stage_root.relative_to(ROOT) / value_path.relative_to(source_relative)
    return value_path.as_posix()


def products_from_source_validation(
    manifest: dict[str, Any], stage_root: Path,
) -> list[dict[str, Any]]:
    layers = manifest.get("layers")
    if not isinstance(layers, list):
        raise ValueError("Bio-ORACLE source-validation manifest has no layer list.")
    return [{
        "dataset_id": layer["dataset_id"],
        "source_payload": layer["source_payload"],
        "source_receipt": layer["source_receipt"],
        "bytes": layer["bytes"],
        "sha256": layer["sha256"],
        "interim_payload": stage_path_for_current_root(layer["staged_payload"], stage_root),
        "interim_bytes": layer["bytes"],
        "interim_sha256": layer["sha256"],
        "staged_receipt": stage_path_for_current_root(layer["staged_receipt"], stage_root),
        "staged_receipt_sha256": layer.get("staged_receipt_sha256"),
        "variables": layer["variables"],
    } for layer in layers]


def current_source_bundle() -> tuple[dict[str, Any], list[dict[str, Any]], str, dict[str, Any]]:
    cleaning_manifest_path = CLEANING_STAGE / "manifest.json"
    source_manifest_path = SOURCE_STAGE / "manifest.json"
    current_manifest_path = (
        cleaning_manifest_path if cleaning_manifest_path.is_file() else source_manifest_path
    )
    stage_root = current_manifest_path.parent
    label = "current Bio-ORACLE interim manifest"
    manifest, raw = load_json(current_manifest_path, label)

    if manifest.get("format") == "oceavera-bio-oracle-interim-source-validation-v1":
        products = products_from_source_validation(manifest, stage_root)
        source_run = dict(manifest.get("source_run", {}))
        if source_run.get("staged_copy"):
            source_run["staged_copy"] = stage_path_for_current_root(
                source_run["staged_copy"], stage_root,
            )
        return manifest, products, hashlib.sha256(raw).hexdigest(), source_run

    if manifest.get("format") not in {
        "oceavera-bio-oracle-cleaning-manifest-v1",
        MANIFEST_FORMAT,
    }:
        raise ValueError("Current Bio-ORACLE interim manifest has an unsupported format.")
    listed_products = manifest.get("products")
    if not isinstance(listed_products, list):
        raise ValueError("Current cleaning manifest has no product list.")
    products = [{
        "dataset_id": item["dataset_id"],
        "source_payload": item["source_file"],
        "source_receipt": item["source_receipt"],
        "bytes": item["source_bytes"],
        "sha256": item["source_sha256"],
        "interim_payload": item.get("product_path"),
        "interim_bytes": item.get("output_bytes"),
        "interim_sha256": item.get("output_sha256"),
        "staged_receipt": item.get("staged_receipt"),
        "staged_receipt_sha256": item.get("staged_receipt_sha256"),
        "variables": item["variables"],
    } for item in listed_products]
    source_hash = manifest.get("source_validation_manifest_sha256", "")
    source_run = dict(manifest.get("source_run", {}))
    if source_run.get("staged_copy"):
        source_run["staged_copy"] = stage_path_for_current_root(
            source_run["staged_copy"], stage_root,
        )
    return manifest, products, str(source_hash), source_run


def classify_product(product_id: str, has_time: bool) -> str:
    token = product_id.casefold()
    if re.search(r"(?:^|_)ssp\d{3}(?:_|$)", token):
        return "future_scenario"
    if "baseline" in token:
        return "baseline"
    if not has_time or any(part in token for part in ("terrain", "landmass", "bathymetry")):
        return "static_terrain"
    return "unclassified"


def candidate_mask_variables(headers: dict[str, dict[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    candidates = []
    for source_path, header in headers.items():
        lat_dim, lon_dim, _ = dimension_names(header)
        for variable in header["variables"]:
            text = " ".join([
                variable["name"],
                str(variable["attributes"].get("long_name", "")),
                str(variable["attributes"].get("standard_name", "")),
            ]).casefold()
            is_candidate = bool(re.search(r"\b(land.?mask|land.?mass|sea.?mask|ocean.?mask)\b", text))
            if is_candidate and is_spatial(variable, lat_dim, lon_dim) and not is_coordinate(variable):
                candidates.append((source_path, variable))
    return candidates


def inspect_coordinates(
    data: bytes,
    header: dict[str, Any],
    *,
    lat_dim: str | None,
    lon_dim: str | None,
    time_dim: str | None,
) -> tuple[dict[str, Any], dict[str, list[Any]], list[dict[str, Any]]]:
    coords: dict[str, list[Any]] = {}
    diagnostics: dict[str, Any] = {}
    issues: list[dict[str, Any]] = []
    by_name = {variable["name"]: variable for variable in header["variables"]}
    wanted = [name for name in (lat_dim, lon_dim, time_dim) if name]
    for name in wanted:
        variable = by_name.get(name)
        if variable is None:
            issues.append({"severity": "review", "code": "coordinate_variable_missing", "message": f"Dimension {name!r} has no coordinate variable."})
            continue
        result = scan_variable(
            data, header, variable, lat_dim=lat_dim, lon_dim=lon_dim,
            time_dim=time_dim, time_labels=None, marine_mask=None, retain_values=True,
        )
        values = result["coordinate_values"]
        if not isinstance(values, list):
            issues.append({"severity": "review", "code": "coordinate_not_numeric", "message": f"Coordinate {name!r} is not a numeric vector."})
            continue
        coords[name] = values
        diag = coordinate_diagnostics(values)
        diag["units"] = serialize(variable["attributes"].get("units"))
        diag["standard_name"] = serialize(variable["attributes"].get("standard_name"))
        diag["axis"] = serialize(variable["attributes"].get("axis"))
        if name == time_dim:
            labels, decode_issue = decode_time_labels(values, variable["attributes"])
            diag["decoded_labels"] = labels
            diag["calendar"] = serialize(variable["attributes"].get("calendar", "standard"))
            diag["units"] = serialize(variable["attributes"].get("units"))
            if decode_issue:
                diag["time_decode_note"] = decode_issue
            if not diag["unique"] or not diag["strictly_monotonic"]:
                issues.append({"severity": "review", "code": "time_coordinate_order", "message": f"Time coordinate {name!r} is duplicated or not monotonic."})
        else:
            if not diag["unique"] or not diag["strictly_monotonic"]:
                issues.append({"severity": "review", "code": "spatial_coordinate_order", "message": f"Spatial coordinate {name!r} is duplicated or not monotonic."})
            if diag["finite_count"] != diag["count"]:
                issues.append({"severity": "review", "code": "spatial_coordinate_nonfinite", "message": f"Spatial coordinate {name!r} contains non-finite values."})
        diagnostics[name] = diag
    return diagnostics, coords, issues


def grid_fingerprint(
    coordinates: dict[str, list[Any]],
    lat_dim: str | None,
    lon_dim: str | None,
    coordinate_metadata: dict[str, Any] | None = None,
) -> str | None:
    if not lat_dim or not lon_dim or lat_dim not in coordinates or lon_dim not in coordinates:
        return None
    digest = hashlib.sha256()
    for name in (lat_dim, lon_dim):
        digest.update(name.encode("utf-8"))
        axis = (coordinate_metadata or {}).get(name, {})
        digest.update(json.dumps({
            key: axis.get(key) for key in ("units", "standard_name", "axis")
        }, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        for value in coordinates[name]:
            digest.update(struct.pack(">d", float(value)))
    return digest.hexdigest()


def scan_layer(
    product: dict[str, Any],
    expected_variables: set[str],
    *,
    marine_mask: list[bool] | None,
    marine_mask_grid_hash: str | None,
    preloaded: dict[tuple[str, str], dict[str, Any]],
    fingerprint_by_grid: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    product_id = product["dataset_id"]
    source_rel = product["source_payload"]
    source_path = repo_file(source_rel, RAW_ROOT, f"immutable NetCDF source for {product_id}")
    interim_rel = product.get("interim_payload")
    interim_path = interim_product_file(product)
    receipt_path = repo_file(product["source_receipt"], RAW_ROOT, f"receipt for {product_id}")
    source_length = source_path.stat().st_size
    source_hash = sha256_file(source_path)
    if source_length != int(product["bytes"]):
        issues.append({"severity": "error", "code": "source_size_mismatch", "message": "Source byte count differs from the immutable intake manifest."})
    if source_hash != product["sha256"]:
        issues.append({"severity": "error", "code": "source_checksum_mismatch", "message": "Source SHA-256 differs from the immutable intake manifest."})
    interim_bytes = interim_path.read_bytes()
    interim_length = len(interim_bytes)
    interim_hash = hashlib.sha256(interim_bytes).hexdigest()
    if product.get("interim_bytes") is not None and interim_length != int(product["interim_bytes"]):
        issues.append({"severity": "error", "code": "interim_size_mismatch", "message": "Current interim byte count differs from its cleaning manifest."})
    if product.get("interim_sha256") and interim_hash != product["interim_sha256"]:
        issues.append({"severity": "error", "code": "interim_checksum_mismatch", "message": "Current interim SHA-256 differs from its cleaning manifest."})
    if interim_hash != source_hash:
        issues.append({"severity": "review", "code": "interim_differs_from_raw", "message": "Current interim payload differs from the immutable raw source; it was preserved for review."})
    receipt, _ = load_json(receipt_path, f"source receipt for {product_id}")
    for key in ("sha256", "bytes"):
        if key in receipt and receipt[key] not in (product["sha256"], product["bytes"], source_length):
            expected = product["sha256"] if key == "sha256" else source_length
            if receipt[key] != expected:
                issues.append({"severity": "error", "code": "receipt_payload_mismatch", "message": f"Source receipt {key} does not match the payload."})
    receipt_dataset = receipt.get("dataset_id")
    if receipt_dataset is not None and receipt_dataset != product_id:
        issues.append({"severity": "error", "code": "receipt_dataset_mismatch", "message": "Receipt dataset ID differs from the layer inventory."})

    try:
        header = parse_header(str(interim_rel), interim_bytes)
    except (NetCDFError, OSError, struct.error) as error:
        return {
            "dataset_id": product_id,
            "source_file": source_rel,
            "source_receipt": product["source_receipt"],
            "source_sha256": source_hash,
            "source_bytes": source_length,
            "final_product_path": interim_rel,
            "output_sha256": interim_hash,
            "output_bytes": interim_length,
            "category": "unclassified",
            "status": "review_required",
            "netcdf_readable": False,
            "issues": issues + [{"severity": "error", "code": "netcdf_read_failure", "message": str(error)}],
            "variables": [],
        }

    lat_dim, lon_dim, time_dim = dimension_names(header)
    coordinate_info, coordinates, coord_issues = inspect_coordinates(
        interim_bytes, header, lat_dim=lat_dim, lon_dim=lon_dim, time_dim=time_dim,
    )
    issues.extend(coord_issues)
    time_labels = coordinate_info.get(time_dim, {}).get("decoded_labels") if time_dim else None
    time_axis_values = coordinates.get(time_dim, []) if time_dim else []
    has_time = time_dim is not None and bool(time_axis_values)
    category = classify_product(product_id, has_time)
    if lat_dim is None or lon_dim is None:
        issues.append({"severity": "review", "code": "spatial_dimensions_missing", "message": "Latitude and/or longitude dimensions could not be identified."})

    grid_hash = grid_fingerprint(coordinates, lat_dim, lon_dim, coordinate_info)
    product_marine_mask = marine_mask
    if marine_mask is not None and (grid_hash is None or grid_hash != marine_mask_grid_hash):
        product_marine_mask = None
        issues.append({
            "severity": "review",
            "code": "marine_mask_grid_mismatch",
            "message": "Candidate-domain comparison was skipped because this product's latitude/longitude grid does not exactly match the candidate mask grid.",
            "product_grid_fingerprint": grid_hash,
            "candidate_mask_grid_fingerprint": marine_mask_grid_hash,
        })
    if grid_hash is not None:
        existing = fingerprint_by_grid.get(grid_hash)
        if existing is None:
            fingerprint_by_grid[grid_hash] = {
                "dimensions": {lat_dim: len(coordinates[lat_dim]), lon_dim: len(coordinates[lon_dim])},
                "coordinates": {lat_dim: coordinate_info.get(lat_dim), lon_dim: coordinate_info.get(lon_dim)},
                "first_dataset_id": product_id,
            }
        elif existing["coordinates"] != {lat_dim: coordinate_info.get(lat_dim), lon_dim: coordinate_info.get(lon_dim)}:
            issues.append({"severity": "review", "code": "grid_metadata_mismatch", "message": "Coordinate vectors share a value fingerprint but their metadata differs."})
    if lat_dim and lon_dim and lat_dim in coordinate_info and lon_dim in coordinate_info:
        if coordinate_info[lat_dim]["count"] != REFERENCE["latitude_length"] or coordinate_info[lon_dim]["count"] != REFERENCE["longitude_length"]:
            issues.append({"severity": "review", "code": "reference_grid_shape_difference", "message": "Grid shape differs from the earlier 178 by 165 audit reference."})
        for name in (lat_dim, lon_dim):
            spacing = coordinate_info[name]["mean_absolute_spacing"]
            deviation = coordinate_info[name]["maximum_spacing_deviation"]
            if spacing is not None and (abs(spacing - REFERENCE["grid_spacing_degrees"]) > 0.0001 or (deviation is not None and deviation > 0.0001)):
                issues.append({"severity": "review", "code": "reference_grid_spacing_difference", "message": f"Coordinate {name!r} spacing differs from the earlier 0.05 degree reference."})

    expected_from_source = set(expected_variables)
    parsed_environment_names = {
        variable["name"] for variable in header["variables"]
        if not is_coordinate(variable) and is_spatial(variable, lat_dim, lon_dim)
    }
    if parsed_environment_names != expected_from_source:
        issues.append({"severity": "error", "code": "variable_inventory_mismatch", "message": "NetCDF data-variable names differ from the collection manifest."})

    global_attrs = header["global_attributes"]
    scenario_values = {
        key: serialize(value) for key, value in global_attrs.items()
        if any(token in key.casefold() for token in ("scenario", "experiment", "ssp"))
    }
    filename_scenario = re.search(r"(?:^|_)(baseline|ssp\d{3})(?:_|$)", product_id, re.I)
    if filename_scenario and scenario_values:
        filename_label = filename_scenario.group(1).casefold()
        internal_text = json.dumps(scenario_values, sort_keys=True).casefold()
        if filename_label not in internal_text and filename_label != "baseline":
            issues.append({"severity": "review", "code": "scenario_metadata_conflict", "message": "Scenario metadata conflicts with the dataset identifier."})

    variables_summary: list[dict[str, Any]] = []
    variable_hashes: dict[tuple[tuple[int, ...], int, str], list[str]] = defaultdict(list)
    names_by_id = {variable["name"]: variable for variable in header["variables"]}
    for variable in header["variables"]:
        coordinate = is_coordinate(variable)
        spatial = is_spatial(variable, lat_dim, lon_dim)
        candidate_key = (str(interim_rel), variable["name"])
        scan = preloaded.get(candidate_key)
        if scan is None:
            scan = scan_variable(
                interim_bytes, header, variable,
                lat_dim=lat_dim, lon_dim=lon_dim, time_dim=time_dim,
                time_labels=time_labels, marine_mask=product_marine_mask,
                retain_values=coordinate,
            )
        missing_locations = []
        for location in scan.get("marine_domain_missing_locations") or []:
            indices = location.get("dimension_indices", {})
            latitude_index = indices.get(lat_dim) if lat_dim else None
            longitude_index = indices.get(lon_dim) if lon_dim else None
            time_index = indices.get(time_dim) if time_dim else None
            missing_locations.append({
                "latitude_index": latitude_index,
                "latitude": coordinates.get(lat_dim, [])[latitude_index] if latitude_index is not None and latitude_index < len(coordinates.get(lat_dim, [])) else None,
                "longitude_index": longitude_index,
                "longitude": coordinates.get(lon_dim, [])[longitude_index] if longitude_index is not None and longitude_index < len(coordinates.get(lon_dim, [])) else None,
                "time_index": time_index,
                "time": time_labels[time_index] if time_index is not None and time_labels is not None and time_index < len(time_labels) else (time_index if time_index is not None else None),
                "dimension_indices": indices,
            })
        attrs = variable["attributes"]
        output = {
            "name": variable["name"],
            "role": "coordinate" if coordinate else ("environmental" if spatial else "auxiliary"),
            "dimensions": variable["dimensions"],
            "data_type": variable["type_name"],
            "shape": variable["shape"],
            "units": serialize(attrs.get("units")),
            "fill_value": serialize(attrs.get("_FillValue", DEFAULT_FILL.get(variable["type_code"]))),
            "fill_value_source": "declared" if "_FillValue" in attrs else "NetCDF classic type default",
            "missing_value": serialize(attrs.get("missing_value")),
            "attributes": serialize(attrs),
            "total_elements": scan["total_elements"],
            "valid_finite_elements": scan["valid_finite_elements"],
            "declared_fill_elements": scan["declared_fill_elements"],
            "declared_missing_elements": scan["declared_missing_elements"],
            "nan_elements": scan["nan_elements"],
            "positive_infinity_elements": scan["positive_infinity_elements"],
            "negative_infinity_elements": scan["negative_infinity_elements"],
            "valid_minimum": scan["valid_minimum"],
            "valid_maximum": scan["valid_maximum"],
            "declared_valid_range_violations": scan.get("declared_valid_range_violations", 0),
            "marine_domain_missing_elements": scan.get("marine_domain_missing_elements"),
            "marine_domain_missing_locations": missing_locations,
            "marine_domain_missing_locations_truncated": scan.get("marine_domain_missing_locations_truncated", False),
            "outside_candidate_domain_valid_elements": scan.get("outside_candidate_domain_valid_elements"),
            "per_time_slice": scan["per_time_slice"],
            "data_sha256": scan["data_sha256"],
        }
        if not coordinate and spatial:
            variable_hashes[(tuple(variable["shape"]), variable["type_code"], scan["data_sha256"])].append(variable["name"])
            if scan["valid_finite_elements"] == 0:
                issues.append({"severity": "review", "code": "environmental_variable_empty", "message": f"Environmental variable {variable['name']!r} has no valid finite values."})
            if scan["nan_elements"] or scan["positive_infinity_elements"] or scan["negative_infinity_elements"]:
                issues.append({"severity": "review", "code": "environmental_nonfinite_values", "message": f"Environmental variable {variable['name']!r} contains undeclared or non-finite values."})
            if scan.get("declared_valid_range_violations", 0):
                issues.append({"severity": "review", "code": "declared_valid_range_violation", "message": f"Environmental variable {variable['name']!r} exceeds its declared valid range."})
            if scan.get("marine_domain_missing_elements", 0) and variable["name"].casefold() != "coastline":
                issues.append({"severity": "review", "code": "marine_domain_missing_values", "message": f"Environmental variable {variable['name']!r} has missing values inside the candidate non-fill domain."})
            if scan.get("outside_candidate_domain_valid_elements", 0):
                issues.append({"severity": "review", "code": "outside_candidate_domain_values", "message": f"Environmental variable {variable['name']!r} contains valid values outside the candidate non-fill domain."})
        variables_summary.append(output)

    duplicate_arrays = [names for names in variable_hashes.values() if len(names) > 1]
    if duplicate_arrays:
        variables_by_name = {item["name"]: item for item in variables_summary}
        for names in duplicate_arrays:
            arrays_are_zero = all(
                variables_by_name[name]["valid_finite_elements"] > 0
                and variables_by_name[name]["valid_minimum"] == 0.0
                and variables_by_name[name]["valid_maximum"] == 0.0
                for name in names
            )
            severity = "warning" if arrays_are_zero else "review"
            code = "identical_zero_arrays" if arrays_are_zero else "duplicate_variable_arrays"
            message = (
                "Distinct environmental summaries have identical all-zero arrays in this regional domain; preserved without deduplication."
                if arrays_are_zero else
                "Two or more environmental variables have byte-identical arrays; values were preserved for review."
            )
            issues.append({"severity": severity, "code": code, "message": message, "variables": names})

    axis_reference = {}
    for name in (lat_dim, lon_dim, time_dim):
        if name and name in names_by_id:
            attrs = names_by_id[name]["attributes"]
            for key in ("units", "standard_name", "axis", "positive", "calendar"):
                if key in attrs:
                    axis_reference[f"{name}.{key}"] = serialize(attrs[key])
    crs_attributes = {}
    for source_name, attributes in [("global", global_attrs)] + [(v["name"], v["attributes"]) for v in header["variables"]]:
        for key, value in attributes.items():
            if key.casefold() in {"crs", "spatial_ref", "grid_mapping_spatial_ref", "epsg_code", "geospatial_bounds_crs", "grid_mapping_name"}:
                crs_attributes[f"{source_name}.{key}"] = serialize(value)
    if not crs_attributes:
        issues.append({"severity": "warning", "code": "crs_identifier_absent", "message": "No explicit CRS identifier was found; geographic coordinate units are reported without asserting EPSG:4326."})

    time_summary = coordinate_info.get(time_dim, {}) if time_dim else {}
    return {
        "dataset_id": product_id,
        "source_file": source_rel,
        "source_receipt": product["source_receipt"],
        "source_sha256": source_hash,
        "source_bytes": source_length,
        "final_product_path": interim_rel,
        "output_sha256": interim_hash,
        "output_bytes": interim_length,
        "category": category,
        "netcdf_format": header["format"],
        "netcdf_readable": True,
        "record_count": header["record_count"],
        "dimensions": header["dimensions"],
        "dimension_names": {"latitude": lat_dim, "longitude": lon_dim, "time": time_dim},
        "coordinate_diagnostics": coordinate_info,
        "grid_fingerprint": grid_hash,
        "coordinate_reference_metadata": {"axes": axis_reference, "crs_attributes": crs_attributes},
        "global_attributes": serialize(global_attrs),
        "scenario_metadata": scenario_values,
        "time_labels": serialize(time_summary.get("decoded_labels", [])),
        "variable_count": len(variables_summary),
        "variables": variables_summary,
        "duplicate_variable_arrays": duplicate_arrays,
        "issues": issues,
        "status": "review_required" if any(item["severity"] in {"error", "review"} for item in issues) else "validated",
        "cleaning_action": "validated the current interim NetCDF against immutable raw provenance; no numerical values or metadata rewritten",
    }


def extract_mask(
    product: dict[str, Any],
    candidates: list[tuple[str, dict[str, Any]]],
) -> tuple[list[bool] | None, dict[str, Any], dict[tuple[str, str], dict[str, Any]]]:
    preloaded: dict[tuple[str, str], dict[str, Any]] = {}
    for source_rel, candidate in candidates:
        if source_rel != product.get("interim_payload"):
            continue
        source_path = repo_file(source_rel, INTERIM_ROOT, "interim marine-mask candidate")
        data = source_path.read_bytes()
        header = parse_header(source_rel, data)
        lat_dim, lon_dim, time_dim = dimension_names(header)
        coordinate_info, coordinates, _ = inspect_coordinates(
            data, header, lat_dim=lat_dim, lon_dim=lon_dim, time_dim=time_dim,
        )
        time_labels = coordinate_info.get(time_dim, {}).get("decoded_labels") if time_dim else None
        variable = next(item for item in header["variables"] if item["name"] == candidate["name"])
        values_result = scan_variable(
            data, header, variable, lat_dim=lat_dim, lon_dim=lon_dim,
            time_dim=time_dim, time_labels=time_labels, marine_mask=None, retain_values=True,
        )
        preloaded[(source_rel, variable["name"])] = values_result
        observed = values_result["coordinate_values"]
        mapping, evidence = mask_value_mapping(variable["attributes"], observed or [])
        counts = Counter(str(value) for value in (observed or []))
        if mapping:
            marine = [
                mapping.get(
                    str(int(value)) if isinstance(value, (int, float)) and float(value).is_integer() else str(value),
                    False,
                )
                for value in observed
            ]
            description = {
                "status": "verified_from_metadata",
                "source_file": source_rel,
                "variable": variable["name"],
                "grid_fingerprint": grid_fingerprint(coordinates, lat_dim, lon_dim, coordinate_info),
                "evidence": evidence,
                "attributes": serialize(variable["attributes"]),
                "value_counts": dict(sorted(counts.items())),
                "marine_cell_count": sum(marine),
                "grid_cell_count": len(marine),
            }
            if lat_dim and lon_dim and len(marine) != len(coordinates.get(lat_dim, [])) * len(coordinates.get(lon_dim, [])):
                description["status"] = "review_required_shape_mismatch"
                return None, description, preloaded
            return marine, description, preloaded
        fill_values = attr_values(variable["attributes"].get("_FillValue", DEFAULT_FILL.get(variable["type_code"])))
        missing_values = attr_values(variable["attributes"].get("missing_value", []))
        valid_domain = [
            not any(compare_marker(value, marker) for marker in fill_values + missing_values)
            and math.isfinite(float(value))
            for value in (observed or [])
        ]
        description = {
            "status": "candidate_nonfill_domain",
            "source_file": source_rel,
            "variable": variable["name"],
            "grid_fingerprint": grid_fingerprint(coordinates, lat_dim, lon_dim, coordinate_info),
            "evidence": evidence,
            "attributes": serialize(variable["attributes"]),
            "value_counts": dict(sorted(counts.items())),
            "grid_cell_count": len(observed or []),
            "candidate_nonfill_cell_count": sum(valid_domain),
            "note": "Only the non-fill spatial domain is used for a cross-layer consistency check; numeric land/water values are not interpreted.",
        }
        if lat_dim and lon_dim and len(valid_domain) != len(coordinates.get(lat_dim, [])) * len(coordinates.get(lon_dim, [])):
            description["status"] = "review_required_shape_mismatch"
            return None, description, preloaded
        return valid_domain, description, preloaded
    return None, {"status": "not_found", "note": "No spatial land/water mask variable was identified in NetCDF metadata."}, preloaded


def check_source_inventory(products: list[dict[str, Any]], source_manifest: dict[str, Any]) -> dict[str, Any]:
    expected_payloads = {item["source_payload"] for item in products}
    expected_receipts = {item["source_receipt"] for item in products}
    actual_payloads = {
        path.relative_to(ROOT).as_posix()
        for path in RAW_ROOT.rglob("*.nc") if path.is_file()
    }
    actual_receipts = {
        path.relative_to(ROOT).as_posix()
        for path in RAW_ROOT.rglob("*.manifest.json") if path.is_file()
    }
    inventory = {
        "manifest_product_count": len(products),
        "manifest_variable_count": sum(len(item.get("variables", [])) for item in products),
        "netcdf_files_found": len(actual_payloads),
        "receipt_files_found": len(actual_receipts),
        "missing_payload_paths": sorted(expected_payloads - actual_payloads),
        "additional_payload_paths": sorted(actual_payloads - expected_payloads),
        "missing_receipt_paths": sorted(expected_receipts - actual_receipts),
        "additional_receipt_paths": sorted(actual_receipts - expected_receipts),
    }
    source_run = source_manifest.get("source_run", {})
    if source_run:
        run_path = repo_file(source_run["path"], RAW_ROOT, "Bio-ORACLE catalogue run manifest")
        run_bytes = run_path.read_bytes()
        run_hash = hashlib.sha256(run_bytes).hexdigest()
        if run_hash != source_run.get("sha256") or len(run_bytes) != source_run.get("bytes"):
            inventory["source_run_integrity"] = "mismatch"
        else:
            inventory["source_run_integrity"] = "verified"
        inventory["source_run_path"] = source_run["path"]
        inventory["source_run_sha256"] = run_hash
    return inventory


def check_interim_inventory(products: list[dict[str, Any]]) -> dict[str, Any]:
    expected = {item.get("interim_payload") for item in products}
    actual = {
        path.relative_to(ROOT).as_posix()
        for path in INTERIM_ROOT.rglob("*.nc") if path.is_file()
    }
    return {
        "netcdf_files_found": len(actual),
        "expected_product_count": len(expected),
        "missing_payload_paths": sorted(path for path in expected - actual if isinstance(path, str)),
        "additional_payload_paths": sorted(path for path in actual - expected if isinstance(path, str)),
        "status": "verified" if actual == expected else "review_required",
    }


def verify_staged_bundle(source_manifest: dict[str, Any], source_manifest_path: Path) -> dict[str, Any]:
    """Recheck staged payloads and receipts before the stage is promoted."""
    stage_root = source_manifest_path.parent
    if not source_manifest_path.is_file() or stage_root not in {SOURCE_STAGE, CLEANING_STAGE}:
        return {"status": "not_applicable", "files_checked": 0}
    expected: dict[str, tuple[str, str | None]] = {}
    for layer in source_manifest.get("layers", []):
        expected[stage_path_for_current_root(layer["staged_payload"], stage_root)] = (
            layer["sha256"], "payload",
        )
        expected[stage_path_for_current_root(layer["staged_receipt"], stage_root)] = (
            layer.get("staged_receipt_sha256", ""), layer["source_receipt"],
        )
    source_run = source_manifest.get("source_run", {})
    if source_run.get("staged_copy"):
        staged_copy = stage_path_for_current_root(source_run["staged_copy"], stage_root)
        expected[staged_copy] = (source_run.get("sha256", ""), source_run["path"])
    manifest_relative = source_manifest_path.relative_to(ROOT).as_posix()
    expected[manifest_relative] = ("", None)
    expected_paths = set(expected)
    actual_paths = {
        path.relative_to(ROOT).as_posix()
        for path in stage_root.rglob("*") if path.is_file()
    }
    missing = sorted(expected_paths - actual_paths)
    extra = sorted(actual_paths - expected_paths)
    mismatches = []
    checked = 0
    for staged_rel, (expected_hash, source_ref) in expected.items():
        staged = (ROOT / staged_rel).resolve()
        if not staged.is_file():
            continue
        actual_hash = sha256_file(staged)
        checked += 1
        if source_ref == "payload":
            if actual_hash != expected_hash:
                mismatches.append(staged_rel)
            continue  # The raw copy is rehashed and parsed from its immutable source.
        if source_ref:
            source = repo_file(source_ref, RAW_ROOT, "source receipt")
            source_hash = sha256_file(source)
            if actual_hash != source_hash:
                mismatches.append(staged_rel)
        elif expected_hash and actual_hash != expected_hash:
            mismatches.append(staged_rel)
    return {
        "status": "verified" if not missing and not extra and not mismatches else "review_required",
        "files_checked": checked,
        "missing_paths": missing,
        "additional_paths": extra,
        "checksum_mismatches": mismatches,
    }


def duplicate_file_groups(files: list[dict[str, Any]]) -> list[list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for item in files:
        if item.get("source_sha256"):
            groups[item["source_sha256"]].append(item["source_file"])
    return [sorted(paths) for paths in groups.values() if len(paths) > 1]


def product_status_counts(files: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(item.get("status", "review_required") for item in files).items()))


def reconcile_cached_findings(summary: dict[str, Any]) -> dict[str, Any]:
    """Apply explicit sparse-layer and exact-zero duplicate interpretations."""
    for file_result in summary.get("files", []):
        variables = {item.get("name"): item for item in file_result.get("variables", [])}
        retained_issues = []
        for issue in file_result.get("issues", []):
            if issue.get("code") == "duplicate_variable_arrays":
                groups = issue.get("variables") or file_result.get("duplicate_variable_arrays", [])
                names = [name for group in groups for name in group]
                if groups and all(
                    name in variables
                    and variables[name].get("valid_finite_elements", 0) > 0
                    and variables[name].get("valid_minimum") == 0.0
                    and variables[name].get("valid_maximum") == 0.0
                    for name in names
                ):
                    retained_issues.append({
                        "severity": "warning",
                        "code": "identical_zero_arrays",
                        "message": "Distinct environmental summaries have identical all-zero arrays in this regional domain; preserved without deduplication.",
                        "variables": names,
                    })
                    continue
            if issue.get("code") == "marine_domain_missing_values" and "coastline" in issue.get("message", "").casefold():
                continue
            retained_issues.append(issue)
        file_result["issues"] = retained_issues
        file_result["status"] = (
            "review_required"
            if any(issue.get("severity") in {"review", "error"} for issue in retained_issues)
            else "validated"
        )

    environmental_variables = [
        variable for file_result in summary.get("files", [])
        for variable in file_result.get("variables", [])
        if variable.get("role") == "environmental"
    ]
    continuous_domain_variables = [
        variable for variable in environmental_variables
        if variable.get("name", "").casefold() not in {
            "coastline", str(summary.get("spatial", {}).get("marine_mask", {}).get("variable", "")).casefold(),
        }
    ]
    comparable_variables = [
        item for item in continuous_domain_variables
        if item.get("marine_domain_missing_elements") is not None
        and item.get("outside_candidate_domain_valid_elements") is not None
    ]
    marine_missing = sum(item["marine_domain_missing_elements"] for item in comparable_variables)
    outside_valid = sum(item["outside_candidate_domain_valid_elements"] for item in comparable_variables)
    mask_report = summary.get("spatial", {}).get("marine_mask", {})
    mask_report.setdefault("encoding_status", mask_report.get("status", "unresolved_semantics"))
    grid_mismatches = [
        item["dataset_id"] for item in summary.get("files", [])
        if any(issue.get("code") == "marine_mask_grid_mismatch" for issue in item.get("issues", []))
    ]
    mask_report["products_with_grid_mismatch"] = grid_mismatches
    if grid_mismatches and mask_report.get("candidate_nonfill_cell_count") is None:
        mask_report["status"] = "grid_mismatch_requires_review"
        mask_report["cross_layer_consistency"] = "candidate-domain comparison was skipped for products whose coordinate grid did not exactly match the mask grid"
    if mask_report.get("source_file") and mask_report.get("candidate_nonfill_cell_count") is not None:
        mask_report["environmental_variable_instances_compared"] = len(comparable_variables)
        mask_report["environmental_variable_instances_not_compared"] = len(continuous_domain_variables) - len(comparable_variables)
        mask_report["missing_values_inside_candidate_domain"] = marine_missing
        mask_report["valid_values_outside_candidate_domain"] = outside_valid
        mask_report["sparse_variables_excluded_from_continuous_domain_check"] = ["coastline"]
        mask_report["candidate_mask_variable_excluded_from_self_comparison"] = mask_report.get("variable")
        mask_report["sparse_variable_missing_elements"] = sum(
            item.get("marine_domain_missing_elements") or 0
            for item in environmental_variables if item.get("name", "").casefold() == "coastline"
        )
        mask_report["reference_marine_cell_count_matches"] = mask_report.get("candidate_nonfill_cell_count") == REFERENCE["marine_cells"]
        if grid_mismatches:
            mask_report["status"] = "grid_mismatch_requires_review"
            mask_report["cross_layer_consistency"] = "candidate-domain comparison was skipped for products whose coordinate grid did not exactly match the mask grid"
        elif len(comparable_variables) != len(continuous_domain_variables):
            mask_report["status"] = "candidate_domain_comparison_incomplete"
            mask_report["cross_layer_consistency"] = "not every continuous environmental variable could be compared with the candidate non-fill domain"
        elif marine_missing == 0 and outside_valid == 0 and mask_report["reference_marine_cell_count_matches"]:
            mask_report["status"] = "empirically_consistent_nonfill_domain"
            mask_report["cross_layer_consistency"] = "all continuous environmental arrays match the candidate non-fill domain; sparse coastline values are reported separately"
        else:
            mask_report["status"] = "candidate_domain_requires_review"
            mask_report["cross_layer_consistency"] = "one or more continuous environmental arrays differ from the candidate non-fill domain"
    summary["variable_counts"]["marine_domain_missing_values"] = marine_missing
    summary["variable_counts"]["outside_candidate_domain_valid_values"] = outside_valid
    summary["variable_counts"]["sparse_layer_marine_domain_missing_values"] = sum(
        item.get("marine_domain_missing_elements") or 0
        for item in environmental_variables if item.get("name", "").casefold() == "coastline"
    )
    summary["variable_counts"]["marine_missingness_assessable"] = bool(mask_report.get("source_file")) and len(comparable_variables) == len(continuous_domain_variables)
    summary["variable_counts"]["marine_mask_encoding_verified"] = mask_report.get("encoding_status") == "verified_from_metadata"
    summary["cleaning_decisions"] = {
        "sparse_terrain_layers": {
            "variables": ["coastline"],
            "treatment": "reported separately; fill cells are not treated as missing continuous marine measurements",
        },
        "identical_all_zero_arrays": {
            "treatment": "reported as a warning and preserved because distinct summary variables can legitimately be equal over a tropical regional extent",
        },
        "landmass_encoding": "numeric values were not assigned land/water meanings; only the non-fill pattern was checked against continuous environmental arrays",
    }
    summary["global_issues"] = [
        issue for issue in summary.get("global_issues", [])
        if issue.get("code") not in {"marine_mask_unresolved", "marine_mask_semantics_unresolved"}
    ]
    mask_status = mask_report.get("status")
    if mask_status in {
        "unresolved_semantics", "not_found", "review_required_shape_mismatch",
        "candidate_domain_requires_review", "candidate_domain_comparison_incomplete",
        "grid_mismatch_requires_review",
    }:
        summary["global_issues"].append({"severity": "review", "code": "marine_mask_unresolved", "details": mask_report})
    elif mask_status == "empirically_consistent_nonfill_domain":
        summary["global_issues"].append({
            "severity": "warning",
            "code": "marine_mask_semantics_unresolved",
            "details": mask_report,
        })
    summary["dataset_counts"]["validated_products"] = sum(
        item.get("status") == "validated" for item in summary.get("files", [])
    )
    summary["dataset_counts"]["review_required_products"] = sum(
        item.get("status") == "review_required" for item in summary.get("files", [])
    )
    summary["cleaning_status"] = (
        "review_required"
        if summary["dataset_counts"]["review_required_products"]
        or any(issue.get("severity") in {"review", "error"} for issue in summary.get("global_issues", []))
        else "validated_with_warnings"
    )
    summary["duplicate_checks"]["within_file_identical_variable_arrays"] = [
        {"dataset_id": item["dataset_id"], "variables": names}
        for item in summary.get("files", []) for names in item.get("duplicate_variable_arrays", [])
    ]
    summary["duplicate_checks"]["identical_zero_arrays_preserved"] = [
        issue for item in summary.get("files", []) for issue in item.get("issues", [])
        if issue.get("code") == "identical_zero_arrays"
    ]
    return summary


def reuse_verified_output(
    input_manifest: dict[str, Any],
    products: list[dict[str, Any]],
    inventory: dict[str, Any],
    *,
    force_full_scan: bool,
) -> dict[str, Any] | None:
    """Reuse an earlier complete report only after rehashing all immutable inputs."""
    if force_full_scan or input_manifest.get("format") not in {
        "oceavera-bio-oracle-cleaning-manifest-v1",
        MANIFEST_FORMAT,
    }:
        return None
    summary_path = CLEANING_STAGE / "cleaning_summary.json"
    if not summary_path.is_file():
        return None
    try:
        summary, _ = load_json(summary_path, "existing Bio-ORACLE cleaning summary")
    except (ValueError, OSError):
        return None
    files = summary.get("files")
    if summary.get("format") != CLEANING_SUMMARY_FORMAT or not isinstance(files, list):
        return None
    if summary.get("cleaner") != cleaner_fingerprint():
        return None
    if not interim_products_match_manifest(input_manifest, products):
        return None
    if len(files) != len(products) or summary.get("dataset_counts", {}).get("source_products") != len(products):
        return None
    if any(inventory.get(key) for key in ("missing_payload_paths", "additional_payload_paths", "missing_receipt_paths", "additional_receipt_paths")):
        return None
    if inventory.get("source_run_integrity") != "verified":
        return None
    by_id = {item.get("dataset_id"): item for item in files}
    if set(by_id) != {item["dataset_id"] for item in products}:
        return None
    for product in products:
        previous = by_id[product["dataset_id"]]
        if previous.get("source_file") != product["source_payload"] or previous.get("source_sha256") != product["sha256"]:
            return None
        source = repo_file(product["source_payload"], RAW_ROOT, "cached Bio-ORACLE source")
        if source.stat().st_size != product["bytes"] or sha256_file(source) != product["sha256"]:
            return None
        receipt, _ = load_json(repo_file(product["source_receipt"], RAW_ROOT, "cached Bio-ORACLE receipt"), "source receipt")
        if receipt.get("dataset_id") not in (None, product["dataset_id"]):
            return None
        if receipt.get("sha256") not in (None, product["sha256"]):
            return None
        if receipt.get("bytes") not in (None, product["bytes"]):
            return None
    print("Reused the complete prior array report after rechecking cleaner rules, raw sources, receipts and current interim outputs.")
    return summary


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as output:
            temporary_path = Path(output.name)
            output.write(json.dumps(serialize(value), ensure_ascii=False, indent=2, sort_keys=True) + "\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def write_summary_atomic_from_spool(
    path: Path,
    summary: dict[str, Any],
    file_spool: Any,
) -> None:
    """Publish the detailed file results without loading the full report into RAM."""
    path.parent.mkdir(parents=True, exist_ok=True)
    overrides = {
        item["dataset_id"]: {
            key: item[key]
            for key in ("issues", "status", "final_product_path", "cleaning_action")
            if key in item
        }
        for item in summary.get("files", [])
    }
    summary_header = {key: value for key, value in summary.items() if key != "files"}
    encoded_header = json.dumps(
        serialize(summary_header), ensure_ascii=False, indent=2, sort_keys=True,
    )
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as output:
            temporary_path = Path(output.name)
            output.write(encoded_header[:-1])
            output.write(',\n  "files": [\n')
            file_spool.flush()
            file_spool.seek(0)
            first = True
            for line in file_spool:
                if not line.strip():
                    continue
                item = json.loads(line)
                override = overrides.get(item.get("dataset_id"))
                if override is not None:
                    item.update(override)
                if not first:
                    output.write(",\n")
                serialized = json.dumps(
                    serialize(item), ensure_ascii=False, indent=2, sort_keys=True,
                )
                output.write("\n".join(f"    {part}" for part in serialized.splitlines()))
                first = False
            output.write("\n  ]\n}\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def compact_file_result(item: dict[str, Any]) -> dict[str, Any]:
    """Keep aggregation fields in RAM; the complete result is stored in a JSONL spool."""
    variable_fields = (
        "name", "role", "total_elements", "valid_finite_elements",
        "declared_fill_elements", "declared_missing_elements", "nan_elements",
        "positive_infinity_elements", "negative_infinity_elements", "valid_minimum",
        "valid_maximum", "declared_valid_range_violations",
        "marine_domain_missing_elements", "outside_candidate_domain_valid_elements",
    )
    compact = {
        key: item[key]
        for key in (
            "dataset_id", "source_file", "source_receipt", "source_sha256",
            "source_bytes", "final_product_path", "output_sha256", "output_bytes",
            "category", "netcdf_readable", "coordinate_diagnostics", "grid_fingerprint",
            "coordinate_reference_metadata", "duplicate_variable_arrays", "issues", "status",
        )
        if key in item
    }
    compact["variables"] = [
        {key: variable[key] for key in variable_fields if key in variable}
        for variable in item.get("variables", [])
    ]
    return compact


def output_product_relative_path(product: dict[str, Any]) -> Path:
    dataset_id = str(product["dataset_id"])
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", dataset_id):
        raise ValueError(f"Bio-ORACLE dataset ID is not safe for an interim path: {dataset_id!r}")
    source_name = Path(str(product["source_payload"])).name
    if not source_name or Path(source_name).name != source_name:
        raise ValueError(f"Bio-ORACLE source filename is not safe for an interim path: {source_name!r}")
    current_path = Path(str(product.get("interim_payload", "")))
    for known_root in (SOURCE_STAGE.relative_to(ROOT), CLEANING_STAGE.relative_to(ROOT)):
        if current_path.is_relative_to(known_root):
            return current_path.relative_to(known_root)
    return Path(dataset_id) / source_name


def interim_products_match_manifest(
    manifest: dict[str, Any],
    products: list[dict[str, Any]],
) -> bool:
    if manifest.get("format") != MANIFEST_FORMAT:
        return False
    manifest_products = manifest.get("products")
    if not isinstance(manifest_products, list) or len(manifest_products) != len(products):
        return False
    by_id = {item.get("dataset_id"): item for item in manifest_products}
    if set(by_id) != {item["dataset_id"] for item in products}:
        return False

    expected_paths: set[str] = set()
    for product in products:
        listed = by_id[product["dataset_id"]]
        expected_relative = output_product_relative_path(product)
        expected_path = (CLEANING_STAGE / expected_relative).relative_to(ROOT).as_posix()
        if listed.get("product_path") != expected_path or product.get("interim_payload") != expected_path:
            return False
        expected_bytes = product.get("interim_bytes", product["bytes"])
        expected_sha256 = product.get("interim_sha256") or product["sha256"]
        if listed.get("output_bytes") != expected_bytes:
            return False
        if listed.get("output_sha256") != expected_sha256:
            return False
        expected_paths.add(expected_path)
        try:
            output = repo_file(listed["product_path"], CLEANING_STAGE, "current interim NetCDF product")
        except (OSError, ValueError):
            return False
        if output.stat().st_size != listed["output_bytes"]:
            return False
        if sha256_file(output) != listed["output_sha256"]:
            return False
    actual_paths = {
        path.relative_to(ROOT).as_posix()
        for path in CLEANING_STAGE.rglob("*.nc")
        if path.is_file()
    }
    return actual_paths == expected_paths


def publish_cleaning_stage(
    products: list[dict[str, Any]],
    summary: dict[str, Any],
    source_validation_hash: str,
    source_run: dict[str, Any],
    source_stage: Path,
    file_spool: Any | None = None,
) -> dict[str, Any]:
    if source_stage == SOURCE_STAGE:
        if CLEANING_STAGE.exists():
            raise ValueError("Cannot promote source validation while a cleaning stage already exists.")
        try:
            SOURCE_STAGE.replace(CLEANING_STAGE)
        except OSError as error:
            raise ValueError(f"Could not promote the validated interim stage to cleaning: {error}") from error
    elif source_stage != CLEANING_STAGE:
        raise ValueError("The current Bio-ORACLE stage is outside the supported interim paths.")
    if not CLEANING_STAGE.is_dir() or CLEANING_STAGE.is_symlink():
        raise ValueError("The interim NetCDF dataset could not be promoted to the cleaning stage.")

    def cleaning_relative_path(value: str) -> str:
        path = Path(value)
        if path.is_relative_to(SOURCE_STAGE.relative_to(ROOT)):
            path = CLEANING_STAGE.relative_to(ROOT) / path.relative_to(SOURCE_STAGE.relative_to(ROOT))
        if not path.is_relative_to(CLEANING_STAGE.relative_to(ROOT)):
            raise ValueError(f"Interim product path is outside the cleaning stage: {value}")
        return path.as_posix()

    summary_by_id = {item["dataset_id"]: item for item in summary.get("files", [])}
    products_out = []
    byte_identical_count = 0
    for product in products:
        result = summary_by_id.get(product["dataset_id"])
        if result is None or not result.get("final_product_path"):
            raise ValueError(f"No scanned interim result exists for {product['dataset_id']}.")
        final_path = cleaning_relative_path(str(result["final_product_path"]))
        result["final_product_path"] = final_path
        output_path = repo_file(final_path, CLEANING_STAGE, "scanned cleaning-stage NetCDF product")
        output_bytes = int(result["output_bytes"])
        output_sha256 = str(result["output_sha256"])
        if output_path.stat().st_size != output_bytes or sha256_file(output_path) != output_sha256:
            raise ValueError(f"Interim product changed after scanning: {product['dataset_id']}.")
        unchanged = output_bytes == int(product["bytes"]) and output_sha256 == product["sha256"]
        byte_identical_count += int(unchanged)
        result["cleaning_action"] = (
            "validated and preserved the existing interim NetCDF byte-for-byte; no numerical values or metadata rewritten"
            if unchanged else
            "validated and preserved the existing interim NetCDF; it differs from raw and is flagged for review"
        )
        products_out.append({
            "dataset_id": product["dataset_id"],
            "source_file": product["source_payload"],
            "source_receipt": product["source_receipt"],
            "source_bytes": product["bytes"],
            "source_sha256": product["sha256"],
            "staged_receipt": cleaning_relative_path(product["staged_receipt"])
            if product.get("staged_receipt") else None,
            "staged_receipt_sha256": product.get("staged_receipt_sha256"),
            "variables": product["variables"],
            "disposition": result.get("status", "review_required"),
            "product_path": final_path,
            "output_bytes": output_bytes,
            "output_sha256": output_sha256,
        })

    if len(products_out) != summary.get("dataset_counts", {}).get("source_products"):
        raise ValueError("Cleaning manifest does not account for every current interim product.")
    summary["cleaner"] = cleaner_fingerprint()
    summary["interim_products"] = {
        "directory": "data/interim/bio_oracle/cleaning/",
        "materialized_count": len(products_out),
        "byte_identical_to_raw_count": byte_identical_count,
        "modified_count": len(products_out) - byte_identical_count,
        "format": "NetCDF (publisher-delivered format)",
        "data_copy_created_during_cleaning": False,
    }
    summary["dataset_counts"]["unchanged_products"] = byte_identical_count
    summary["dataset_counts"]["modified_products"] = len(products_out) - byte_identical_count
    summary["dataset_counts"]["files_requiring_review"] = sum(item.get("status") == "review_required" for item in summary.get("files", []))
    cleaning_source_run = dict(source_run)
    if cleaning_source_run.get("staged_copy"):
        cleaning_source_run["staged_copy"] = cleaning_relative_path(
            cleaning_source_run["staged_copy"],
        )
    manifest = {
        "format": MANIFEST_FORMAT,
        "cleaner": cleaner_fingerprint(),
        "source_run": cleaning_source_run,
        "source_validation_manifest_sha256": source_validation_hash,
        "operation": (
            "structural, metadata, missing-value, numerical, spatial, temporal, and duplicate validation "
            "of the existing interim NetCDF products; the source-validation directory is promoted by rename, "
            "with no extra dataset copy or numerical rewrite during cleaning"
        ),
        "product_count": len(products_out),
        "variable_instance_count": sum(len(item.get("variables", [])) for item in products),
        "validated_product_count": summary["dataset_counts"]["validated_products"],
        "review_required_product_count": summary["dataset_counts"]["review_required_products"],
        "products": products_out,
    }
    if summary["dataset_counts"]["source_products"] != len(products_out):
        raise ValueError("Output summary does not account for every current interim product.")
    if file_spool is None:
        write_json_atomic(CLEANING_STAGE / "cleaning_summary.json", summary)
    else:
        write_summary_atomic_from_spool(
            CLEANING_STAGE / "cleaning_summary.json", summary, file_spool,
        )
    write_json_atomic(CLEANING_STAGE / "manifest.json", manifest)
    return summary


def run_cleaning(*, force_full_scan: bool = False) -> dict[str, Any]:
    input_manifest, products, source_validation_hash, source_run = current_source_bundle()
    stage_directories = [
        path.name for path in INTERIM_ROOT.iterdir()
        if path.is_dir() and path.name in {"cleaning", "source_validation"}
    ]
    if len(stage_directories) > 1:
        raise ValueError("Bio-ORACLE has more than one active stage directory; resolve the D-049 layout before cleaning.")
    if not products:
        raise ValueError("The Bio-ORACLE source bundle contains no products.")
    product_ids = [item.get("dataset_id") for item in products]
    if len(product_ids) != len(set(product_ids)):
        raise ValueError("The Bio-ORACLE source bundle repeats dataset IDs.")
    source_stage = CLEANING_STAGE if CLEANING_STAGE.is_dir() else SOURCE_STAGE
    if source_stage.name not in stage_directories:
        raise ValueError("Bio-ORACLE interim stage manifest does not match the active stage directory.")
    for product in products:
        for required in ("dataset_id", "source_payload", "source_receipt", "bytes", "sha256", "variables"):
            if required not in product:
                raise ValueError(f"Bio-ORACLE product entry is missing {required!r}.")
        repo_file(product["source_payload"], RAW_ROOT, "NetCDF product")
        repo_file(product["source_receipt"], RAW_ROOT, "NetCDF receipt")
        interim_product_file(product)

    source_manifest_path = source_stage / "manifest.json"
    if input_manifest.get("format") == "oceavera-bio-oracle-interim-source-validation-v1":
        source_manifest = input_manifest
        source_run = input_manifest.get("source_run", {})
        staged_checks = verify_staged_bundle(source_manifest, source_manifest_path)
    else:
        source_manifest = {
            "source_run": source_run,
            "layer_count": len(products),
            "variable_count": sum(len(item.get("variables", [])) for item in products),
        }
        staged_checks = {"status": "already_replaced", "files_checked": 0}

    inventory = check_source_inventory(products, source_manifest)
    inventory["interim"] = check_interim_inventory(products)
    if inventory.get("source_run_integrity") == "mismatch":
        raise ValueError("Bio-ORACLE catalogue run manifest does not match its recorded fingerprint.")
    cached_summary = reuse_verified_output(
        input_manifest, products, inventory, force_full_scan=force_full_scan,
    )
    if cached_summary is not None:
        cached_summary = reconcile_cached_findings(cached_summary)
        if interim_products_match_manifest(input_manifest, products):
            current_manifest = input_manifest
            current_manifest["validated_product_count"] = cached_summary["dataset_counts"]["validated_products"]
            current_manifest["review_required_product_count"] = cached_summary["dataset_counts"]["review_required_products"]
            file_status = {item["dataset_id"]: item["status"] for item in cached_summary["files"]}
            for product_entry in current_manifest["products"]:
                product_entry["disposition"] = file_status.get(product_entry["dataset_id"], "review_required")
            current_manifest["cleaner"] = cleaner_fingerprint()
            write_json_atomic(CLEANING_STAGE / "cleaning_summary.json", cached_summary)
            write_json_atomic(CLEANING_STAGE / "manifest.json", current_manifest)
            print("Reused the current interim NetCDF products after verifying their source and output SHA-256 values.")
        else:
            cached_summary = publish_cleaning_stage(
                products,
                cached_summary,
                source_validation_hash,
                source_run,
                source_stage,
            )
            print("Refreshed the cleaning reports after validating the existing interim NetCDF products.")
        print(f"NetCDF products: {cached_summary['dataset_counts']['source_products']:,}")
        print(f"Readable: {cached_summary['dataset_counts']['readable_products']:,}; unreadable: {cached_summary['dataset_counts']['unreadable_products']:,}")
        print(f"Validated: {cached_summary['dataset_counts']['validated_products']:,}; review required: {cached_summary['dataset_counts']['review_required_products']:,}")
        print(f"Environmental variable instances: {cached_summary['variable_counts']['environmental_variable_instances']:,}; distinct names: {cached_summary['variable_counts']['distinct_environmental_variable_names']:,}")
        print("Reproducibility: unchanged source hashes verified; cached array diagnostics reused.")
        print(f"Cleaning manifest: {CLEANING_STAGE.relative_to(ROOT).as_posix()}/manifest.json")
        print(f"Cleaning summary: {CLEANING_STAGE.relative_to(ROOT).as_posix()}/cleaning_summary.json")
        return cached_summary

    # Find the first candidate mask without retaining headers for every product.
    # Keeping all 356 parsed headers consumed avoidable memory before array scans.
    headers: dict[str, dict[str, Any]] = {}
    candidates: list[tuple[str, dict[str, Any]]] = []
    for product in products:
        interim_rel = product["interim_payload"]
        try:
            headers[interim_rel] = parse_header(interim_rel)
        except (NetCDFError, OSError, struct.error) as error:
            print(f"Header check will be recorded during full scan for {product['dataset_id']}: {error}")
            continue
        candidates = candidate_mask_variables({interim_rel: headers[interim_rel]})
        if candidates:
            break
        headers.clear()
    marine_mask = None
    mask_report: dict[str, Any] = {"status": "not_found", "note": "No spatial land/water mask variable was identified in NetCDF metadata."}
    preloaded: dict[tuple[str, str], dict[str, Any]] = {}
    for product in products:
        if any(source_rel == product["interim_payload"] for source_rel, _ in candidates):
            marine_mask, mask_report, preloaded = extract_mask(product, candidates)
            break

    grid_fingerprints: dict[str, dict[str, Any]] = {}
    files: list[dict[str, Any]] = []
    file_spool = tempfile.TemporaryFile(mode="w+t", encoding="utf-8", newline="\n")
    progress_every = max(1, len(products) // 20)
    for index, product in enumerate(products, start=1):
        expected_vars = set(product.get("variables", []))
        try:
            item = scan_layer(
                product, expected_vars, marine_mask=marine_mask,
                marine_mask_grid_hash=mask_report.get("grid_fingerprint"),
                preloaded=preloaded, fingerprint_by_grid=grid_fingerprints,
            )
        except (ValueError, OSError, KeyError, TypeError, struct.error) as error:
            item = {
                "dataset_id": product["dataset_id"],
                "source_file": product["source_payload"],
                "source_receipt": product["source_receipt"],
                "source_sha256": None,
                "source_bytes": None,
                "final_product_path": product.get("interim_payload"),
                "output_sha256": None,
                "output_bytes": None,
                "category": "unclassified",
                "status": "review_required",
                "netcdf_readable": False,
                "issues": [{"severity": "error", "code": "layer_inspection_failure", "message": str(error)}],
                "variables": [],
            }
        json.dump(serialize(item), file_spool, ensure_ascii=False, separators=(",", ":"))
        file_spool.write("\n")
        files.append(compact_file_result(item))
        del item
        if index == 1 or index == len(products) or index % progress_every == 0:
            print(f"Inspected {index:,}/{len(products):,} Bio-ORACLE layers.")

    # Use an undocumented landmass value only as a non-fill spatial domain candidate.
    if mask_report.get("status") == "verified_from_metadata":
        actual_cells = mask_report["grid_cell_count"]
        if actual_cells != REFERENCE["latitude_length"] * REFERENCE["longitude_length"]:
            mask_report["reference_grid_shape_difference"] = True
        if mask_report["marine_cell_count"] != REFERENCE["marine_cells"]:
            mask_report["reference_marine_cell_difference"] = mask_report["marine_cell_count"] - REFERENCE["marine_cells"]

    environmental_variables = [
        variable for item in files for variable in item.get("variables", [])
        if variable.get("role") == "environmental"
    ]
    if mask_report.get("status") == "candidate_nonfill_domain":
        marine_missing = sum(item.get("marine_domain_missing_elements") or 0 for item in environmental_variables)
        outside_valid = sum(item.get("outside_candidate_domain_valid_elements") or 0 for item in environmental_variables)
        mask_report["environmental_variable_instances_compared"] = len(environmental_variables)
        mask_report["missing_values_inside_candidate_domain"] = marine_missing
        mask_report["valid_values_outside_candidate_domain"] = outside_valid
        mask_report["reference_marine_cell_count_matches"] = mask_report["candidate_nonfill_cell_count"] == REFERENCE["marine_cells"]
        if marine_missing == 0 and outside_valid == 0 and mask_report["reference_marine_cell_count_matches"]:
            mask_report["status"] = "empirically_consistent_nonfill_domain"
            mask_report["cross_layer_consistency"] = "all environmental arrays match the candidate non-fill domain"
        else:
            mask_report["status"] = "candidate_domain_requires_review"
            mask_report["cross_layer_consistency"] = "one or more environmental arrays differ from the candidate non-fill domain"
    variable_instances = len(environmental_variables)
    environmental_names = sorted({item["name"] for item in environmental_variables})
    category_counts = Counter(item.get("category", "unclassified") for item in files)
    duplicate_sources = duplicate_file_groups(files)
    if duplicate_sources:
        for item in files:
            if any(item.get("source_file") in group for group in duplicate_sources):
                item["issues"].append({"severity": "review", "code": "duplicate_source_payload", "message": "SHA-256 matches another Bio-ORACLE payload; both source products were preserved."})
                item["status"] = "review_required"
    if len(grid_fingerprints) > 1:
        first_fingerprint = next(iter(grid_fingerprints))
        for item in files:
            if item.get("grid_fingerprint") != first_fingerprint:
                item["issues"].append({"severity": "review", "code": "grid_alignment_mismatch", "message": "Coordinate vectors differ from another Bio-ORACLE product grid."})
                item["status"] = "review_required"

    inventory_issues = []
    for key in ("missing_payload_paths", "additional_payload_paths", "missing_receipt_paths", "additional_receipt_paths"):
        if inventory[key]:
            inventory_issues.append({"severity": "error", "code": key, "paths": inventory[key]})
    if inventory["interim"]["status"] != "verified":
        inventory_issues.append({"severity": "error", "code": "interim_inventory_mismatch", "details": inventory["interim"]})
    global_issues = inventory_issues
    if staged_checks.get("status") == "review_required":
        global_issues.append({"severity": "review", "code": "source_stage_bundle_integrity", "details": staged_checks})
    if mask_report.get("status") in {"unresolved_semantics", "not_found", "review_required_shape_mismatch", "candidate_domain_requires_review"}:
        global_issues.append({"severity": "review", "code": "marine_mask_unresolved", "details": mask_report})

    summary = reconcile_cached_findings({
        "format": CLEANING_SUMMARY_FORMAT,
        "cleaner": cleaner_fingerprint(),
        "reference_expectations": REFERENCE,
        "inventory": inventory,
        "source_stage_recheck": staged_checks,
        "dataset_counts": {
            "source_products": len(products),
            "readable_products": sum(bool(item.get("netcdf_readable")) for item in files),
            "unreadable_products": sum(not bool(item.get("netcdf_readable")) for item in files),
            "validated_products": sum(item.get("status") == "validated" for item in files),
            "review_required_products": sum(item.get("status") == "review_required" for item in files),
            "corrected_products": 0,
            "excluded_products": 0,
            "unchanged_products": sum(
                item.get("output_sha256") == item.get("source_sha256") and item.get("output_sha256") is not None
                for item in files
            ),
            "modified_products": sum(
                item.get("output_sha256") != item.get("source_sha256") and item.get("output_sha256") is not None
                for item in files
            ),
            "category_counts": dict(sorted(category_counts.items())),
        },
        "variable_counts": {
            "variable_instances": variable_instances,
            "environmental_variable_instances": len(environmental_variables),
            "environmental_array_elements": sum(item["total_elements"] for item in environmental_variables),
            "distinct_environmental_variable_names": len(environmental_names),
            "environmental_variable_names": environmental_names,
            "empty_environmental_variable_instances": sum(item["valid_finite_elements"] == 0 for item in environmental_variables),
            "declared_fill_values": sum(item["declared_fill_elements"] or 0 for item in environmental_variables),
            "declared_missing_values": sum(item["declared_missing_elements"] or 0 for item in environmental_variables),
            "declared_valid_range_violations": sum(item["declared_valid_range_violations"] for item in environmental_variables),
            "nan_values": sum(item["nan_elements"] for item in environmental_variables),
            "positive_infinity_values": sum(item["positive_infinity_elements"] for item in environmental_variables),
            "negative_infinity_values": sum(item["negative_infinity_elements"] for item in environmental_variables),
            "marine_domain_missing_values": sum(item.get("marine_domain_missing_elements") or 0 for item in environmental_variables),
            "outside_candidate_domain_valid_values": sum(item.get("outside_candidate_domain_valid_elements") or 0 for item in environmental_variables),
            "marine_missingness_assessable": marine_mask is not None,
            "confirmed_invalid_measurements": sum(
                item["nan_elements"] + item["positive_infinity_elements"] + item["negative_infinity_elements"]
                for item in environmental_variables
            ),
            "numerical_modifications_performed": 0,
        },
        "spatial": {
            "unique_grids": len(grid_fingerprints),
            "grids": list(grid_fingerprints.values()),
            "marine_mask": mask_report,
            "crs_identifiers": sorted({
                json.dumps(item.get("coordinate_reference_metadata", {}).get("crs_attributes", {}), sort_keys=True)
                for item in files if item.get("coordinate_reference_metadata", {}).get("crs_attributes")
            }),
        },
        "duplicate_checks": {
            "byte_identical_source_groups": duplicate_sources,
            "duplicate_source_files": sum(len(group) - 1 for group in duplicate_sources),
            "within_file_identical_variable_arrays": [
                {"dataset_id": item["dataset_id"], "variables": names}
                for item in files for names in item.get("duplicate_variable_arrays", [])
            ],
            "repeated_coordinate_or_time_axes": [
                {"dataset_id": item["dataset_id"], "coordinate": name}
                for item in files for name, diag in item.get("coordinate_diagnostics", {}).items()
                if not diag.get("unique", True)
            ],
        },
        "global_issues": global_issues,
        "files": files,
    })
    summary = publish_cleaning_stage(
        products,
        summary,
        source_validation_hash,
        source_run,
        source_stage,
        file_spool,
    )
    file_spool.close()

    print(f"NetCDF products: {summary['dataset_counts']['source_products']:,}")
    print(f"Readable: {summary['dataset_counts']['readable_products']:,}; unreadable: {summary['dataset_counts']['unreadable_products']:,}")
    print(f"Validated: {summary['dataset_counts']['validated_products']:,}; review required: {summary['dataset_counts']['review_required_products']:,}")
    print(f"Environmental variable instances: {summary['variable_counts']['environmental_variable_instances']:,}; distinct names: {summary['variable_counts']['distinct_environmental_variable_names']:,}")
    print(f"Corrected files: 0; excluded files: 0; duplicate source groups: {len(duplicate_sources):,}")
    print(f"Interim NetCDF products: {summary['interim_products']['materialized_count']:,} ({summary['interim_products']['byte_identical_to_raw_count']:,} byte-identical to raw)")
    print(f"Cleaning manifest: {CLEANING_STAGE.relative_to(ROOT).as_posix()}/manifest.json")
    print(f"Cleaning summary: {CLEANING_STAGE.relative_to(ROOT).as_posix()}/cleaning_summary.json")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force-full-scan",
        action="store_true",
        help="Re-read every NetCDF array even when unchanged source hashes have a complete prior report.",
    )
    arguments = parser.parse_args()
    try:
        run_cleaning(force_full_scan=arguments.force_full_scan)
    except (ValueError, OSError, RuntimeError, struct.error) as error:
        print(f"Bio-ORACLE cleaning failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
