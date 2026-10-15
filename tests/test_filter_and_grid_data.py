"""Focused tests for independent temporal, marine and grid filtering."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import json

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point, box


ROOT = Path(__file__).resolve().parents[1]
FILTER_PATH = ROOT / "src/data_preparation/09_filter_and_grid_data.py"
FILTER_SPEC = importlib.util.spec_from_file_location("oceavera_filter_step_09", FILTER_PATH)
if FILTER_SPEC is None or FILTER_SPEC.loader is None:
    raise ImportError(f"Could not load filtering script: {FILTER_PATH}")
filtering = importlib.util.module_from_spec(FILTER_SPEC)
sys.modules[FILTER_SPEC.name] = filtering
FILTER_SPEC.loader.exec_module(filtering)


class FilterAndGridTests(unittest.TestCase):
    def test_script_09_does_not_import_script_08_or_netcdf(self) -> None:
        source = FILTER_PATH.read_text(encoding="utf-8")
        self.assertNotIn("importlib", source)
        self.assertNotIn("08_integrate_spatiotemporal_data", source)
        self.assertNotIn("netCDF4", source)
        self.assertNotIn(".nc", source)
        self.assertEqual(len(inspect.signature(filtering.main).parameters), 0)

    def test_reading_full_integration_does_not_change_its_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            full_path = root / "full.parquet"
            manifest_path = root / "manifest.json"
            feature_columns = {f"bio_oracle__feature_{index}": {} for index in range(382)}
            source_columns = {f"obis_field_{index}": [f"value-{index}"] for index in range(112)}
            metadata = {
                "resolved_event_year": [2001], "environment_period": ["baseline_2000"],
                "temporal_eligibility": ["eligible"], "temporal_resolution_status": ["resolved"],
                "integration_source_row": [1], "raster_row": [1], "raster_column": [1],
                "raster_cell_id": [1], "flags": ["[]"],
            }
            frame = gpd.GeoDataFrame(
                {**source_columns, **metadata, **{column: [np.nan] for column in feature_columns}},
                geometry=[Point(81, 7)], crs=4326,
            )
            frame.to_parquet(full_path, index=False, compression="zstd", geometry_encoding="WKB", schema_version="1.1.0")
            before = hashlib.sha256(full_path.read_bytes()).hexdigest()
            manifest = {
                "output": {"sha256": before},
                "records": {"cleaned_obis_rows": 1, "output_fields": len(frame.columns),
                            "original_obis_field_count": 112, "original_obis_fields_preserved_exactly": 112},
                "feature_columns": feature_columns,
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with patch.object(filtering, "INTEGRATION_REPORT_PATH", manifest_path):
                loaded, _ = filtering.read_integration(root, full_path)
            after = hashlib.sha256(full_path.read_bytes()).hexdigest()
        self.assertEqual(before, after)
        self.assertEqual(loaded.shape, frame.shape)
        self.assertTrue(set(source_columns).issubset(loaded.columns))
        self.assertTrue(set(feature_columns).issubset(loaded.columns))

    def test_temporal_period_edges(self) -> None:
        self.assertEqual(filtering.period_label(2000), "2000-2009")
        self.assertEqual(filtering.period_label(2009), "2000-2009")
        self.assertEqual(filtering.period_label(2010), "2010-2019")
        self.assertEqual(filtering.period_label(2019), "2010-2019")
        self.assertEqual(filtering.period_label(2020), "2020-2026")
        self.assertEqual(filtering.period_label(2026), "2020-2026")

    def test_flags_are_parsed_as_exact_json_array_tokens(self) -> None:
        self.assertEqual(filtering.parse_obis_flags('["NO_DEPTH", "ON_LAND"]'), ({"NO_DEPTH", "ON_LAND"}, True))
        self.assertEqual(filtering.parse_obis_flags('["NOT_ON_LAND", "MARINE_UNSURE"]'), ({"NOT_ON_LAND", "MARINE_UNSURE"}, True))
        self.assertFalse(filtering.parse_obis_flags("not json")[1])
        self.assertFalse(filtering.parse_obis_flags('{"flags": ["ON_LAND"]}')[1])
        self.assertEqual(filtering.geographic_quality_group({"ON_LAND", "MARINE_UNSURE"}), filtering.GEOGRAPHIC_GROUPS[0])

    def test_marine_filter_uses_polygon_and_exact_flags_not_marine_attribute(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mask_path = root / "marine-area.geojson"
            output_path = root / "marine-observations.parquet"
            gpd.GeoDataFrame({"source": ["test"]}, geometry=[box(80, 6, 82, 8)], crs="EPSG:4326").to_file(mask_path)
            points = gpd.GeoDataFrame(
                {
                    "integration_source_row": [1, 2, 3, 4, 5, 6],
                    "marine": ["true"] * 6,
                    "flags": [
                        '["ON_LAND"]',
                        '["MARINE_UNSURE"]',
                        '[]',
                        "invalid-json",
                        '[]',
                        '["ON_LAND", "MARINE_UNSURE"]',
                    ],
                },
                geometry=[Point(81, 7), Point(81.1, 7), Point(81.2, 7), Point(81.3, 7), Point(79, 7), Point(80, 7)],
                crs="EPSG:4326",
            )
            marine, report = filtering.apply_marine_mask(points, mask_path, "Test marine-area source record", output_path, root)
        self.assertEqual(marine["integration_source_row"].tolist(), [3])
        self.assertEqual(report["counts"]["inside_marine_polygon"], 4)
        self.assertEqual(report["counts"]["on_land_flagged_rows"], 2)
        self.assertEqual(report["counts"]["marine_unsure_flagged_rows"], 2)
        self.assertEqual(report["counts"]["rows_with_both_flags"], 1)
        self.assertEqual(report["counts"]["missing_or_invalid_flags_rows"], 1)
        self.assertFalse(report["obis_marine_taxon_attribute_used_for_coordinate_verification"])

    def test_grid_axes_use_persisted_values_and_fingerprints(self) -> None:
        latitudes = np.array([2.0, 1.0, 0.0], dtype="<f8")
        longitudes = np.array([10.0, 11.0], dtype="<f8")
        manifest = {
            "spatial_grid": {
                "rows": len(latitudes),
                "columns": len(longitudes),
                "latitude_axis_centres": latitudes.tolist(),
                "longitude_axis_centres": longitudes.tolist(),
                "latitude_axis_sha256": hashlib.sha256(latitudes.tobytes()).hexdigest(),
                "longitude_axis_sha256": hashlib.sha256(longitudes.tobytes()).hexdigest(),
            }
        }
        actual_longitudes, actual_latitudes = filtering.read_grid_axes(ROOT, manifest)
        np.testing.assert_array_equal(actual_longitudes, longitudes)
        np.testing.assert_array_equal(actual_latitudes, latitudes)
        polygon = filtering.make_cell_polygon(actual_longitudes, actual_latitudes, 0, 0)
        self.assertAlmostEqual(polygon.bounds[0], 9.5)
        self.assertAlmostEqual(polygon.bounds[1], 1.5)
        self.assertAlmostEqual(polygon.bounds[2], 10.5)
        self.assertAlmostEqual(polygon.bounds[3], 2.5)

    def test_policy_b_retains_water_centres_and_records_uncertainty_categories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mask_path = root / "water.gpkg"
            water = box(80, 6, 82, 8).difference(box(80.9, 6.9, 81.1, 7.1))
            gpd.GeoDataFrame(geometry=[water], crs=4326).to_file(mask_path)
            points = gpd.GeoDataFrame({
                "integration_source_row": [1, 2, 3, 4, 5], "flags": ["[]"] * 5,
                "coordinateUncertaintyInMeters": ["1000", "5000", "", "500000", "1000"],
                "scientificName": ["inside", "coast", "unknown", "outside extent", "land"],
            }, geometry=[Point(81.5, 7.5), Point(81.11, 7), Point(81.5, 7), Point(81.5, 7), Point(81, 7)], crs=4326)
            marine, report = filtering.apply_marine_mask(points, mask_path, "synthetic test water", root / "out.parquet", root)
        self.assertEqual(marine.integration_source_row.tolist(), [1, 2, 3, 4])
        self.assertEqual(marine["marine_position_confidence"].tolist(), [
            "known_footprint_marine",
            "known_footprint_crosses_coast_or_land",
            "unknown_uncertainty",
            "known_footprint_outside_reference_extent",
        ])
        self.assertEqual(marine.marine_uncertainty_verified.tolist(), [True, False, False, False])
        self.assertEqual(marine.geometry.geom_equals(points.geometry.iloc[:4]).all(), True)
        self.assertEqual(report["counts"]["retained_policy_b_water_centre_candidates"], 4)
        self.assertEqual(report["counts"]["excluded_by_known_uncertainty"], 0)
        self.assertEqual(report["counts"]["retained_known_uncertainty_crosses_coast_or_land"], 1)
        self.assertEqual(report["counts"]["retained_known_uncertainty_outside_reference"], 1)
        self.assertEqual(report["exclusive_decision_counts"]["outside_marine_water"], 1)
        self.assertEqual(sum(report["exclusive_decision_counts"].values()), 5)

    def test_flagged_and_invalid_rows_remain_excluded_under_policy_b(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mask_path = root / "water.geojson"
            gpd.GeoDataFrame(geometry=[box(80, 6, 82, 8)], crs=4326).to_file(mask_path)
            points = gpd.GeoDataFrame({
                "integration_source_row": [1, 2, 3, 4, 5],
                "flags": ['["ON_LAND"]', '["MARINE_UNSURE"]', "[]", "invalid", "[]"],
            }, geometry=[Point(81, 7), Point(81.1, 7), Point(81.2, 7), Point(81.3, 7), Point(79, 7)], crs=4326)
            marine, report = filtering.apply_marine_mask(points, mask_path, "synthetic water", root / "out.parquet", root)
        self.assertEqual(marine.integration_source_row.tolist(), [3])
        self.assertEqual(report["exclusive_decision_counts"]["ON_LAND"], 1)
        self.assertEqual(report["exclusive_decision_counts"]["MARINE_UNSURE"], 1)
        self.assertEqual(report["exclusive_decision_counts"]["missing_or_invalid_flags"], 1)
        self.assertEqual(report["exclusive_decision_counts"]["outside_marine_water"], 1)

    def test_uncertainty_distances_are_geodesic_metres(self) -> None:
        from pyproj import Geod
        polygon = filtering.geodesic_uncertainty_footprint(80.5, 7.0, 1000)
        x, y = polygon.exterior.coords[0]
        _, _, distance = Geod(ellps="WGS84").inv(80.5, 7.0, x, y)
        self.assertAlmostEqual(distance, 1000 / np.cos(np.pi / 360), places=5)

    def test_default_reference_is_reused_and_checksum_changes_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            mask = Path(directory) / "water.gpkg"
            provenance = Path(directory) / "source.json"
            mask.write_bytes(b"synthetic reference fingerprint")
            record = {"status": "validated", "prepared_sha256": filtering.file_sha256(mask),
                      "study_bounds": list(filtering.STUDY_BOUNDS)}
            provenance.write_text(json.dumps(record))
            with patch.object(filtering, "DEFAULT_MARINE_PATH", mask), patch.object(filtering, "MARINE_PROVENANCE_PATH", provenance):
                self.assertEqual(filtering.prepare_default_marine_reference(), record)
                mask.write_bytes(b"changed")
                with self.assertRaises(filtering.FilterError):
                    filtering.prepare_default_marine_reference()

    def test_grid_axes_reject_changed_manifest_values(self) -> None:
        manifest = {
            "spatial_grid": {
                "rows": 2,
                "columns": 2,
                "latitude_axis_centres": [0.0, 1.0],
                "longitude_axis_centres": [10.0, 11.0],
                "latitude_axis_sha256": "wrong",
                "longitude_axis_sha256": "wrong",
            }
        }
        with self.assertRaises(filtering.FilterError):
            filtering.read_grid_axes(ROOT, manifest)

    def test_species_cell_period_summary_counts_reconcile(self) -> None:
        rows = pd.DataFrame(
            {
                "taxonomy_species_key": ["AphiaID:1", "AphiaID:1", "AphiaID:2"],
                "grid_cell_id": [4, 4, 4],
                "raster_row": [1, 1, 1],
                "raster_column": [0, 0, 0],
                "analysis_period": ["2000-2009"] * 3,
            }
        )
        summary = rows.groupby(
            ["taxonomy_species_key", "grid_cell_id", "raster_row", "raster_column", "analysis_period"],
            as_index=False,
        ).size().rename(columns={"size": "occurrence_record_count"})
        check = filtering.validate_grid_count_reconciliation(rows, summary)
        self.assertEqual(check["source_species_rank_observations"], 3)
        self.assertTrue(check["matches"])
        summary.loc[0, "occurrence_record_count"] += 1
        with self.assertRaises(filtering.FilterError):
            filtering.validate_grid_count_reconciliation(rows, summary)

    def test_species_key_requires_species_rank(self) -> None:
        species = pd.Series({"taxonRank": "Species", "AphiaID": "343936"})
        genus = pd.Series({"taxonRank": "genus", "AphiaID": "123"})
        self.assertEqual(filtering.taxonomy_species_key(species), "AphiaID:343936")
        self.assertIsNone(filtering.taxonomy_species_key(genus))


if __name__ == "__main__":
    unittest.main()
