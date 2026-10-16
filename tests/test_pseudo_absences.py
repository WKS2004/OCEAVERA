"""Focused checks for full-population long-format construction helpers."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from netCDF4 import Dataset
from shapely.geometry import Point


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src/data_preparation/10_construct_pseudo_absences.py"
SPEC = importlib.util.spec_from_file_location("oceavera_long_background", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load Script 10: {SCRIPT}")
stage = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = stage
SPEC.loader.exec_module(stage)


class LongPresenceBackgroundTests(unittest.TestCase):
    def test_seeded_sampling_is_repeatable_and_globally_unique(self) -> None:
        pool = np.arange(100, dtype=int)
        first, first_shortfall = stage.draw_background_cells(
            np.random.default_rng(stage.SEED), pool, 40
        )
        second, second_shortfall = stage.draw_background_cells(
            np.random.default_rng(stage.SEED), pool, 40
        )
        np.testing.assert_array_equal(first, second)
        self.assertEqual(first_shortfall, 0)
        self.assertEqual(second_shortfall, 0)
        self.assertEqual(len(np.unique(first)), 40)

    def test_candidate_shortfall_is_returned_for_caller_to_stop(self) -> None:
        selected, shortfall = stage.draw_background_cells(
            np.random.default_rng(stage.SEED), np.array([4, 8]), wanted=5
        )
        self.assertEqual(set(selected), {4, 8})
        self.assertEqual(shortfall, 3)

    def test_background_pool_requires_water_and_all_core_values(self) -> None:
        water = np.array([True, True, False, True, True, True])
        first = np.array([1.0, 1.0, 1.0, np.nan, 1.0, 1.0])
        second = np.array([1.0, np.nan, 1.0, 1.0, 1.0, 1.0])
        pool = stage.eligible_background_pool(
            water, [first, second], {0, 4}
        )
        np.testing.assert_array_equal(pool, np.array([5]))

    def test_pool_rejects_wrong_raster_shape(self) -> None:
        with self.assertRaisesRegex(ValueError, "shape mismatch"):
            stage.eligible_background_pool(
                np.ones(3, dtype=bool), [np.ones(2)], set()
            )

    def test_species_eligibility_requires_every_declared_condition(self) -> None:
        frame = pd.DataFrame({
            "taxonRank": ["Species", "Genus", "Species", "Species", "Species", "Species", "Species", "Species"],
            "AphiaID": ["10", "11", "bad", "12", "13", "0", "14", "15"],
            "absence": ["false"] * 7 + ["true"],
            "marine": ["true"] * 7 + ["false"],
        })
        core_complete = np.array([True, True, True, False, True, True, True, True])
        centre_in_water = np.array([True, True, True, True, False, True, True, True])
        eligible, counts = stage.species_level_eligibility(
            frame, core_complete, centre_in_water
        )
        np.testing.assert_array_equal(
            eligible,
            np.array([True, False, False, False, False, False, True, False]),
        )
        self.assertEqual(counts["eligible_rows"], 2)
        self.assertEqual(counts["species_rank_rows"], 7)
        self.assertEqual(counts["aphia_id_rows"], 6)
        self.assertEqual(counts["absence_false_rows"], 7)
        self.assertEqual(counts["marine_true_rows"], 7)

    def test_species_eligibility_checks_vector_lengths(self) -> None:
        frame = pd.DataFrame({
            "taxonRank": ["Species"],
            "AphiaID": [10],
            "absence": [False],
            "marine": [True],
        })
        with self.assertRaisesRegex(ValueError, "do not match"):
            stage.species_level_eligibility(
                frame, np.array([], dtype=bool), np.array([True])
            )

    def test_raster_indices_centres_and_ids_match_manifest_axes(self) -> None:
        frame = gpd.GeoDataFrame(
            {
                "raster_row": [1, 2],
                "raster_column": [0, 1],
                "raster_cell_id": [2, 5],
                "grid_cell_id": [2, 5],
                "raster_cell_center_latitude": [11.0, 12.0],
                "raster_cell_center_longitude": [20.0, 21.0],
                "integration_source_row": [100, 101],
            },
            geometry=[Point(20, 11), Point(21, 12)],
            crs="EPSG:4326",
        )
        evidence = stage.verify_observation_grid(
            frame, np.array([10.0, 11.0, 12.0]), np.array([20.0, 21.0])
        )
        self.assertEqual(evidence["raster_index_discrepancies"], 0)
        self.assertEqual(evidence["raster_centre_discrepancies"], 0)

    def test_inconsistent_cell_centre_is_rejected(self) -> None:
        frame = gpd.GeoDataFrame(
            {
                "raster_row": [1],
                "raster_column": [0],
                "raster_cell_id": [2],
                "grid_cell_id": [2],
                "raster_cell_center_latitude": [10.0],
                "raster_cell_center_longitude": [20.0],
                "integration_source_row": [100],
            },
            geometry=[Point(20, 11)],
            crs="EPSG:4326",
        )
        with self.assertRaisesRegex(ValueError, "latitudes disagree"):
            stage.verify_observation_grid(
                frame, np.array([10.0, 11.0]), np.array([20.0, 21.0])
            )

    def test_duplicate_source_row_identity_is_rejected(self) -> None:
        frame = gpd.GeoDataFrame(
            {
                "raster_row": [1, 1],
                "raster_column": [0, 0],
                "raster_cell_id": [2, 2],
                "grid_cell_id": [2, 2],
                "raster_cell_center_latitude": [11.0, 11.0],
                "raster_cell_center_longitude": [20.0, 20.0],
                "integration_source_row": [100, 100],
            },
            geometry=[Point(20, 11), Point(20, 11)],
            crs="EPSG:4326",
        )
        with self.assertRaisesRegex(ValueError, "Duplicate source-row"):
            stage.verify_observation_grid(
                frame, np.array([10.0, 11.0]), np.array([20.0, 21.0])
            )

    def test_netcdf_reader_uses_time_axes_masking_scaling_and_units_once(self) -> None:
        reader = stage.integration_utilities()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scaled.nc"
            with Dataset(path, "w") as nc:
                nc.createDimension("time", 2)
                nc.createDimension("latitude", 2)
                nc.createDimension("longitude", 2)
                time = nc.createVariable("time", "f8", ("time",))
                time.axis = "T"
                time.units = "seconds since 1970-01-01T00:00:00Z"
                time[:] = [946684800.0, 1262304000.0]
                variable = nc.createVariable(
                    "temperature",
                    "i2",
                    ("longitude", "time", "latitude"),
                    fill_value=-9999,
                )
                variable.units = "test_unit"
                variable.scale_factor = 0.5
                variable.add_offset = 10.0
                variable.set_auto_maskandscale(False)
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore",
                        message="Setting the shape on a NumPy array has been deprecated.*",
                        category=DeprecationWarning,
                    )
                    variable[:] = [
                        [[0, 2], [10, 12]],
                        [[4, 6], [14, -9999]],
                    ]
            with Dataset(path) as nc:
                variable = nc.variables["temperature"]
                values = stage.decoded_netcdf_slice(
                    variable,
                    1,
                    {
                        "time_dimension": "time",
                        "latitude_dimension": "latitude",
                        "longitude_dimension": "longitude",
                    },
                    reader,
                    "temperature",
                    "test_unit",
                )
                years = [
                    value.year
                    for value in stage.num2date(
                        nc.variables["time"][:],
                        nc.variables["time"].units,
                        only_use_cftime_datetimes=False,
                    )
                ]
        np.testing.assert_allclose(
            values, [[15.0, 17.0], [16.0, np.nan]], equal_nan=True
        )
        self.assertEqual(years, [2000, 2010])

    def test_quarantined_period_is_detected(self) -> None:
        feature = {"quarantined_periods": ["baseline_2000"]}
        self.assertTrue(stage.is_quarantined(feature, "baseline_2000"))
        self.assertFalse(stage.is_quarantined(feature, "baseline_2010"))

    def test_numeric_and_null_comparison_reports_differences(self) -> None:
        result = stage.compare_values(
            np.array([1.0, np.nan, 3.0]),
            np.array([1.0, 4.0, 3.0001]),
        )
        self.assertEqual(result["positions_checked"], 3)
        self.assertEqual(result["null_fill_discrepancies"], 1)
        self.assertEqual(result["numerical_mismatches"], 1)
        self.assertAlmostEqual(result["maximum_absolute_difference"], 0.0001)

    def test_geoparquet_readback_preserves_schema_geometry_crs_and_compression(self) -> None:
        frame = gpd.GeoDataFrame(
            {
                "occurrenceID": pd.Series(["obis-1", pd.NA], dtype="string"),
                "integration_source_row": pd.Series([101, pd.NA], dtype="Int64"),
                "AphiaID": pd.Series([12345, 12345], dtype="Int64"),
                "geometry": [Point(81.0, 7.0), Point(82.0, 8.0)],
                "presence_background_label": pd.Series([1, 0], dtype="int8"),
                "sample_type": pd.Series(
                    ["observed_presence", "sampled_background"], dtype="string"
                ),
                "target_taxon_key": pd.Series(
                    ["AphiaID:12345", "AphiaID:12345"], dtype="string"
                ),
                "paired_presence_source_row": pd.Series([101, 101], dtype="int64"),
                "eligible_species_level_ml": pd.Series([True, True], dtype="bool"),
                "ml_eligibility_reason": pd.Series(
                    ["preliminary_species_core_eligible"] * 2, dtype="string"
                ),
                "background_sampling_method": pd.Series(
                    [pd.NA, "uniform_unique_GSHHG_water_core_complete"],
                    dtype="string",
                ),
                "sample_id": pd.Series(
                    ["presence:101", "background:101"], dtype="string"
                ),
            },
            geometry="geometry",
            crs="EPSG:4326",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "long-format.parquet"
            frame.to_parquet(
                path,
                index=False,
                compression="zstd",
                geometry_encoding="WKB",
                schema_version="1.1.0",
            )
            reopened = gpd.read_parquet(path)
            pd.testing.assert_frame_equal(frame, reopened, check_dtype=True)
            self.assertTrue(reopened.geometry.geom_equals(frame.geometry).all())
            metadata = stage.geoparquet_metadata(path)
        self.assertEqual(list(frame.columns[4:]), list(stage.OUTPUT_COLUMNS))
        self.assertEqual(frame["presence_background_label"].value_counts().to_dict(), {1: 1, 0: 1})
        self.assertTrue(pd.isna(frame.iloc[1]["occurrenceID"]))
        self.assertTrue(pd.isna(frame.iloc[1]["integration_source_row"]))
        self.assertEqual(frame.iloc[1]["paired_presence_source_row"], 101)
        self.assertEqual(metadata["geoparquet_version"], "1.1.0")
        self.assertEqual(metadata["geometry_encoding"], "WKB")
        self.assertEqual(metadata["compression"], ["ZSTD"])

    def test_distribution_summary_excludes_missing_values(self) -> None:
        summary = stage.distribution_summary(np.array([1.0, 3.0, np.nan]))
        self.assertEqual(summary["count"], 2)
        self.assertEqual(summary["minimum"], 1.0)
        self.assertEqual(summary["median"], 2.0)
        self.assertEqual(summary["maximum"], 3.0)

    def test_fingerprints_show_existing_inputs_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "existing.parquet"
            path.write_bytes(b"input bytes remain unchanged")
            before = stage.snapshot_files({"existing": path})
            _ = path.read_bytes()
            after = stage.snapshot_files({"existing": path})
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
