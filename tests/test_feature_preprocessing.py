"""Unit tests for OCEAVERA Script 12 using synthetic locations only."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

SCRIPT = Path(__file__).resolve().parents[1] / "src/data_preparation/12_feature_engineering_and_preprocessing.py"
# Also runnable when the user has only extracted the bundle in a separate folder.
if not SCRIPT.exists():
    SCRIPT = Path(__file__).with_name("12_feature_engineering_and_preprocessing.py")
spec = importlib.util.spec_from_file_location("oceavera_prepare_step12", SCRIPT)
assert spec is not None and spec.loader is not None
step12 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = step12
spec.loader.exec_module(step12)


def synthetic_frame() -> gpd.GeoDataFrame:
    """Twenty different spatial blocks, each containing both class labels."""
    records = []
    for block in range(20):
        for label in [1, 0]:
            d = {
                "sample_id": f"{label}-{block}",
                "integration_source_row": block if label == 1 else np.nan,
                "paired_presence_source_row": block if label == 0 else np.nan,
                "target_taxon_key": f"AphiaID:{100 + (block % 4)}",
                "grid_cell_id": block * 2 + label,
                "analysis_period": "2010-2019",
                "presence_background_label": label,
                "raster_cell_center_latitude": 5 + (block % 5) * .8 + label * .01,
                "raster_cell_center_longitude": 78 + (block // 5) * .8 + label * .01,
                "bio_oracle__no3_mean__depthsurf": 0.1 + block,
                "bio_oracle__po4_mean__depthsurf": 0.02 + block,
            }
            for i, name in enumerate(step12.CORE):
                d[name] = -40.0 if name.endswith("bathymetry_mean__benthic") else i + block * .03 + 1
            d["geometry"] = Point(d["raster_cell_center_longitude"], d["raster_cell_center_latitude"])
            records.append(d)
    return gpd.GeoDataFrame(records, crs="EPSG:4326")


class FeaturePreparationTests(unittest.TestCase):
    def test_engineered_depth_and_missing(self):
        frame = synthetic_frame()
        frame.loc[0, step12.CORE[-1]] = np.nan
        frame.loc[2, step12.CORE[-1]] = 0.0
        result = step12.add_engineered_features(frame)
        self.assertTrue(np.isnan(result.loc[0, step12.ENG_DEPTH]))
        self.assertEqual(result.loc[1, step12.ENG_DEPTH], 40)
        self.assertAlmostEqual(result.loc[1, step12.ENG_LOG_DEPTH], np.log1p(40))
        self.assertEqual(result.loc[2, step12.ENG_DEPTH], 0.0)
        self.assertEqual(result.loc[2, step12.ENG_LOG_DEPTH], 0.0)
        self.assertEqual(result.loc[1, step12.ENG_TEMP_SAL],
                         frame.loc[1, step12.CORE[0]] * frame.loc[1, step12.CORE[1]])

    def test_spatial_split_never_shares_cells_or_blocks(self):
        frame = step12.add_spatial_blocks(step12.add_engineered_features(synthetic_frame()))
        result, report = step12.split_spatial_blocks(frame)
        self.assertEqual(set(result["split"]), {"train", "validation", "test"})
        self.assertEqual(report["cross_split_cell_overlap"], 0)
        self.assertEqual(report["cross_split_spatial_block_overlap"], 0)
        self.assertEqual(report["paired_background_split_audit"]["pairs"], 20)
        self.assertEqual(report["paired_background_split_audit"]["cross_partition"], 0)
        self.assertEqual(len(result), len(frame))
        for split in ["train", "validation", "test"]:
            self.assertEqual(set(result.loc[result["split"].eq(split), step12.TARGET]), {0, 1})

    def test_feature_sets_do_not_include_leakage_fields(self):
        frame = step12.add_spatial_blocks(step12.add_engineered_features(synthetic_frame()))
        frame, _ = step12.split_spatial_blocks(frame)
        sets, report = step12.make_feature_sets(frame)
        self.assertEqual(len(sets["core_six"]), 6)
        self.assertEqual(len(sets["core_plus_engineered"]), 9)
        self.assertTrue(set(step12.CORE).issubset(sets["core_plus_engineered"]))
        self.assertTrue(set(step12.NEW_FEATURES).issubset(sets["core_plus_engineered"]))
        self.assertNotIn("sample_id", sum(sets.values(), []))
        self.assertNotIn(step12.TARGET, sum(sets.values(), []))
        self.assertIn("bio_oracle__no3_mean__depthsurf", report["optional_columns_admitted_from_training_only"])

    def test_quarantined_optional_candidate_is_not_admitted(self):
        frame = step12.add_spatial_blocks(step12.add_engineered_features(synthetic_frame()))
        frame, _ = step12.split_spatial_blocks(frame)
        sets, report = step12.make_feature_sets(
            frame, {"bio_oracle__no3_mean__depthsurf": ["baseline_2000"]})
        self.assertNotIn("bio_oracle__no3_mean__depthsurf", sets["domain_expanded"])
        self.assertIn("source quarantined", report["optional_columns_rejected"][
            "bio_oracle__no3_mean__depthsurf"])

    def test_templates_unfitted_and_unknown_species_supported(self):
        frame = step12.add_engineered_features(synthetic_frame())
        frame[step12.CORE[0]] = np.nan
        feature_names = step12.CORE
        for scaled in [False, True]:
            pipe = step12.build_preprocessor(feature_names, scaled=scaled)
            self.assertFalse(hasattr(pipe, "transformers_"))
            # Fitting here is ONLY on synthetic unit-test data, never source data.
            pipe.fit(frame.iloc[:24][feature_names + [step12.TAXON]])
            transformed = pipe.transform(frame.iloc[24:26][feature_names + [step12.TAXON]])
            self.assertTrue(np.isfinite(transformed).all())
            self.assertGreater(transformed.shape[1], len(feature_names))

    def test_taxon_support_table(self):
        frame = step12.add_spatial_blocks(step12.add_engineered_features(synthetic_frame()))
        frame, _ = step12.split_spatial_blocks(frame)
        table = step12.support_table(frame)
        self.assertEqual(len(table), 4)
        self.assertIn("spatial_evaluation_supported_provisionally", table.columns)


if __name__ == "__main__":
    unittest.main()
