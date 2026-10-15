"""Focused tests for date mapping and deterministic Bio-ORACLE cell matching."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import warnings
from pathlib import Path

import numpy as np
from netCDF4 import Dataset


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_PATH = ROOT / "src/data_preparation/08_integrate_spatiotemporal_data.py"
INTEGRATION_SPEC = importlib.util.spec_from_file_location("oceavera_integration_step_08", INTEGRATION_PATH)
if INTEGRATION_SPEC is None or INTEGRATION_SPEC.loader is None:
    raise ImportError(f"Could not load integration script: {INTEGRATION_PATH}")
integration = importlib.util.module_from_spec(INTEGRATION_SPEC)
sys.modules[INTEGRATION_SPEC.name] = integration
INTEGRATION_SPEC.loader.exec_module(integration)


class DateAndGridTests(unittest.TestCase):
    def test_date_boundaries_use_the_actual_supported_slice_policy(self) -> None:
        expected = {
            1999: None,
            2000: "baseline_2000",
            2009: "baseline_2000",
            2010: "baseline_2010",
            2019: "baseline_2010",
            2020: "ssp245_2020",
            2026: "ssp245_2020",
            2027: None,
            None: None,
        }
        for year, period in expected.items():
            with self.subTest(year=year):
                self.assertEqual(integration.temporal_period(year), period)

    def test_obis_year_fields_support_iso_and_epoch_milliseconds(self) -> None:
        self.assertEqual(integration.parse_year("2025-08-24"), 2025)
        self.assertEqual(integration.parse_year("1965-02-02T12:00:00Z"), 1965)
        self.assertEqual(integration.parse_year("1755993600000"), 2025)
        self.assertEqual(integration.parse_year("-155001600000", "date_start"), 1965)
        self.assertIsNone(integration.parse_year("2008/2013"))
        self.assertEqual(integration.resolve_observation_year({"year": "", "eventDate": "2009-03-19"}), (2009, "eventDate"))

    def test_epoch_fields_use_milliseconds_even_at_the_unix_epoch(self) -> None:
        for field in ("date_start", "date_mid", "date_end"):
            for value, year in (("-8121600000", 1969), ("-1", 1969), ("0", 1970),
                                ("1", 1970), ("2000", 1970), ("1123200000", 1970)):
                with self.subTest(field=field, value=value):
                    self.assertEqual(integration.parse_year(value, field), year)
        self.assertEqual(integration.parse_year("2000", "year"), 2000)
        self.assertEqual(integration.parse_year("2010", "date_year"), 2010)
        self.assertIsNone(integration.parse_year("0", "year"))
        resolved = integration.resolve_observation_date({
            "year": "1969", "eventDate": "1969-09-29T12:00:00Z",
            "date_start": "-8121600000", "date_mid": "-8121600000", "date_end": "-8121600000",
        })
        self.assertEqual(resolved["year"], 1969)
        self.assertEqual(resolved["eligibility"], "ineligible")

    def test_intervals_crossing_each_boundary_remain_ambiguous(self) -> None:
        for interval in ("1999/2000", "2009/2010", "2019/2020", "2026/2027", "2001/2025"):
            with self.subTest(interval=interval):
                self.assertEqual(integration.resolve_observation_date({"eventDate": interval})["eligibility"], "ambiguous")
        self.assertEqual(integration.resolve_observation_date({})["eligibility"], "unknown")

    def test_intervals_are_not_truncated_to_the_first_year(self) -> None:
        resolved = integration.resolve_observation_date({
            "year": "",
            "eventDate": "2008/2013",
            "date_start": "1199145600000",
            "date_mid": "1293753600000",
            "date_end": "1388448000000",
            "date_year": "2010",
        })
        self.assertEqual(resolved["year"], 2010)
        self.assertEqual(resolved["period"], "baseline_2010")
        self.assertEqual(resolved["status"], "resolved_single_year_with_interval")

    def test_interval_without_single_year_evidence_is_period_only_or_ambiguous(self) -> None:
        bounded_period = integration.resolve_observation_date({"eventDate": "2012/2015"})
        self.assertIsNone(bounded_period["year"])
        self.assertEqual(bounded_period["period"], "baseline_2010")
        self.assertEqual(bounded_period["eligibility"], "eligible")
        crossing_periods = integration.resolve_observation_date({"eventDate": "2008/2013"})
        self.assertIsNone(crossing_periods["period"])
        self.assertEqual(crossing_periods["eligibility"], "ambiguous")

    def test_conflicting_single_year_periods_are_ambiguous(self) -> None:
        resolved = integration.resolve_observation_date({
            "year": "2008", "eventDate": "2008/2013", "date_mid": "2010", "date_year": "2010",
        })
        self.assertEqual(resolved["eligibility"], "ambiguous")
        self.assertEqual(resolved["status"], "ambiguous_conflicting_date_evidence")

    def test_temperature_and_cloud_units_are_harmonized_from_source_metadata(self) -> None:
        absolute = integration.unit_policy("tas_mean", "K", "")
        future = integration.unit_policy("tas_mean", "degree_C", "")
        temperature_range = integration.unit_policy("tas_range", "K", "")
        cloud_fraction = integration.unit_policy("clt_mean", "(0 - 1)", "cloud_area_fraction")
        self.assertEqual(absolute["standardized_units"], "degree_C")
        self.assertEqual(future["standardized_units"], "degree_C")
        self.assertIn("quarantine", temperature_range["conversion"])
        self.assertEqual(cloud_fraction["standardized_units"], "1")
        original = np.ma.array([26.72473488096375])
        self.assertTrue(integration.harmonize_source_values(original, "tas_mean", "K").mask.all())
        self.assertEqual(float(original[0]), 26.72473488096375)
        np.testing.assert_array_equal(integration.harmonize_source_values(original, "tas_mean", "degree_C"), original)
        self.assertTrue(integration.harmonize_source_values(np.ma.array([-270.13]), "tas_range", "K").mask.all())
        self.assertTrue(integration.harmonize_source_values(np.ma.array([1.6]), "clt_sd", "1").mask.all())
        with self.assertRaises(integration.IntegrationError):
            integration.unit_policy("clt_mean", "percent", "cloud_area_fraction")

    def test_shared_feature_units_and_scientific_definitions_are_checked(self) -> None:
        shared = {
            "dataset_id": "tas_baseline_2000_2020_depthsurf",
            "scenario": "baseline",
            "depth": "depthsurf",
            "time_indexes_by_year": {2000: 0, 2010: 1},
            "variables": [{
                "column": "bio_oracle__example__depthsurf",
                "name": "example", "units": "m", "long_name": "Example", "standard_name": "example",
            }],
        }
        changed = {
            **shared,
            "dataset_id": "example_ssp245_2020_2100_depthsurf",
            "scenario": "ssp245",
            "time_indexes_by_year": {2020: 0},
            "variables": [{
                **shared["variables"][0], "units": "cm",
            }],
        }
        with self.assertRaises(integration.IntegrationError):
            integration.build_feature_inventory([shared, changed])

    def test_tie_break_uses_the_lowest_array_index(self) -> None:
        row, column, status = integration.nearest_cell(
            longitude=10.5,
            latitude=0.5,
            longitude_axis=np.array([10.0, 11.0]),
            latitude_axis=np.array([0.0, 1.0]),
        )
        self.assertEqual((row, column, status), (0, 0, "matched"))

    def test_outer_half_cell_edges_are_inclusive_and_outside_points_are_not_clamped(self) -> None:
        axes = (np.array([10.0, 11.0]), np.array([0.0, 1.0]))
        self.assertEqual(integration.nearest_cell(9.5, -0.5, *axes), (0, 0, "matched"))
        self.assertEqual(integration.nearest_cell(9.499, 0.0, *axes)[2], "outside_raster_extent")
        self.assertEqual(integration.nearest_cell(10.0, 91.0, *axes)[2], "invalid_observation_coordinate")

    def test_descending_axes_are_supported(self) -> None:
        self.assertEqual(integration.nearest_cell(10.0, 0.0, np.array([11.0, 10.0, 9.0]), np.array([1.0, 0.0, -1.0])), (1, 1, "matched"))

    def test_netCDF4_applies_mask_and_scale_once_and_keeps_decoded_zero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scaled.nc"
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="Setting the shape on a NumPy array has been deprecated",
                    category=DeprecationWarning,
                )
                with Dataset(path, "w") as dataset:
                    dataset.createDimension("time", 1)
                    dataset.createDimension("latitude", 2)
                    dataset.createDimension("longitude", 2)
                    variable = dataset.createVariable("sample", "i2", ("time", "latitude", "longitude"), fill_value=-9999)
                    variable.set_auto_maskandscale(False)
                    variable[0, 0, 0] = -20
                    variable[0, 0, 1] = -9999
                    variable[0, 1, 0] = 4
                    variable[0, 1, 1] = 10
                    variable.scale_factor = 0.5
                    variable.add_offset = 10.0
            with Dataset(path) as dataset:
                values = integration.read_data_slice(dataset.variables["sample"], "time", 0, "latitude", "longitude")
        self.assertEqual(float(values[0, 0]), 0.0)
        self.assertTrue(bool(np.ma.getmaskarray(values)[0, 1]))
        self.assertEqual(float(values[1, 0]), 12.0)


if __name__ == "__main__":
    unittest.main()
