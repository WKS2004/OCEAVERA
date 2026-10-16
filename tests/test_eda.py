"""Focused synthetic checks for the read-only EDA analysis helpers."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src/data_preparation/11_explore_presence_background_data.py"
SPEC = importlib.util.spec_from_file_location("oceavera_eda", SCRIPT)
eda = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(eda)


def synthetic_data() -> gpd.GeoDataFrame:
    """Create paired positive/background records with repeats and missing values."""
    pair_keys = [
        ("A", "2000-2009"), ("A", "2000-2009"), ("B", "2000-2009"),
        ("B", "2010-2019"), ("C", "2010-2019"), ("C", "2010-2019"),
    ]
    rows = []
    for pair_id, (taxon, period) in enumerate(pair_keys):
        eligible = pair_id < 4
        positive_cell = 11 if pair_id < 2 else 20 + pair_id
        for label in (1, 0):
            cell = positive_cell if label == 1 else 100 + pair_id
            lon = (80.0 + pair_id * 0.01) if label == 1 else (81.0 + pair_id * 0.01)
            row = {
                eda.TARGET: label, eda.KEY: taxon, eda.PERIOD: period, eda.CELL: cell,
                eda.ELIGIBLE: eligible, "sample_id": f"sample-{pair_id}-{label}",
                "sample_type": "presence" if label == 1 else "background",
                "paired_presence_source_row": pair_id,
                "integration_source_row": pair_id if label == 1 else np.nan,
                "taxonRank": "species", "ml_eligibility_reason": "eligible" if eligible else "rank",
                "AphiaID": 1000 + pair_id, "scientificName": f"Species {taxon}",
                "raster_cell_center_longitude": lon, "raster_cell_center_latitude": 7.0 + pair_id * .01,
                "decimalLongitude": lon, "decimalLatitude": 7.0 + pair_id * .01,
            }
            for index, feature in enumerate(eda.CORE):
                row[feature] = float(pair_id + index + 1)
            rows.append((row, Point(lon, 7.0 + pair_id * .01)))
    rows[0][0][list(eda.CORE)[0]] = np.inf
    rows[1][0][list(eda.CORE)[1]] = np.nan
    rows[2][0][list(eda.CORE)[2]] = np.nan
    rows[3][0][list(eda.CORE)[2]] = np.nan
    for row, _ in rows:
        row[list(eda.CORE)[3]] = 8.0  # constant feature
        row[list(eda.CORE)[4]] = np.nan  # empty feature
    frame = pd.DataFrame([row for row, _ in rows])
    return gpd.GeoDataFrame(frame, geometry=[point for _, point in rows], crs="EPSG:4326")


class EdaSectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.output_root = Path(self.temp.name)
        self.tables = self.output_root / "reports/eda/tables"
        self.figures = self.output_root / "reports/eda/figures"
        self.tables.mkdir(parents=True)
        self.figures.mkdir(parents=True)
        self.root_patch = patch.multiple(eda, ROOT=self.output_root, TABLES=self.tables,
                                         FIGURES=self.figures)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.addCleanup(self.temp.cleanup)
        self.frame = synthetic_data()
        self.env = list(eda.CORE)

    def test_all_sections_create_expected_evidence_outputs(self) -> None:
        eligible = self.frame.loc[self.frame[eda.ELIGIBLE].astype(bool)]
        eda.section_a(self.frame, self.env, eligible)
        eda.section_b(self.frame, self.env)
        eda.section_c(self.frame)
        eda.section_d(self.frame)
        catalog = {name: {"quarantined_periods": [], "quarantine_reasons_by_period": {}}
                   for name in self.env}
        eda.section_e(self.frame, self.env, catalog)
        eda.section_f(self.frame, LineString([(79.0, 5.0), (79.0, 9.0)]))
        self.assertEqual(len(list(self.tables.glob("*.csv"))), 16)
        self.assertEqual(len(list(self.figures.glob("*.png"))), 8)

    def test_missingness_infinity_constant_and_empty_features_are_reported(self) -> None:
        eda.section_b(self.frame, self.env)
        missing = pd.read_csv(self.tables / "B_environmental_missingness.csv")
        full = missing.loc[missing["population"].eq("complete_population")].set_index("feature")
        self.assertEqual(full.loc[self.env[0], "positive_infinity"], 1)
        self.assertEqual(full.loc[self.env[0], "missing"], 1)
        eda.section_e(self.frame, self.env, {})
        screen = pd.read_csv(self.tables / "E_feature_profile_screen.csv")
        full_screen = screen.loc[screen["population"].eq("complete_population")].set_index("feature")
        self.assertTrue(bool(full_screen.loc[self.env[3], "constant_or_empty"]))
        self.assertTrue(bool(full_screen.loc[self.env[4], "constant_or_empty"]))
        self.assertEqual(full_screen.loc[self.env[4], "valid_profiles"], 0)

    def test_repeated_taxon_cell_period_records_are_kept_and_counted(self) -> None:
        eda.section_b(self.frame, self.env)
        repeated = pd.read_csv(self.tables / "B_repeated_positive_taxon_cell_period.csv")
        full = repeated.loc[repeated["population"].eq("complete_population")]
        self.assertEqual(len(full), 1)
        self.assertEqual(full.iloc[0]["source_records"], 2)

    def test_protected_fingerprint_detects_changes_without_writing_data(self) -> None:
        protected = self.output_root / "frozen.parquet"
        protected.write_bytes(b"synthetic frozen source")
        digest = eda.sha256(protected)
        with patch.multiple(eda, ROOT=self.output_root,
                            EXPECTED_SHA256={"frozen.parquet": digest}):
            before = eda.protected_fingerprints()
            self.assertEqual(before["frozen.parquet"], digest)
            self.assertEqual(eda.sha256(protected), digest)
            protected.write_bytes(b"changed")
            with self.assertRaises(RuntimeError):
                eda.protected_fingerprints()


if __name__ == "__main__":
    unittest.main()
