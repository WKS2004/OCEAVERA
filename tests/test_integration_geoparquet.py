"""Focused GeoParquet publication checks for the replacement integration."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_PATH = ROOT / "src/data_preparation/08_integrate_spatiotemporal_data.py"
INTEGRATION_SPEC = importlib.util.spec_from_file_location("oceavera_integration_step_08", INTEGRATION_PATH)
if INTEGRATION_SPEC is None or INTEGRATION_SPEC.loader is None:
    raise ImportError(f"Could not load integration script: {INTEGRATION_PATH}")
integration = importlib.util.module_from_spec(INTEGRATION_SPEC)
sys.modules[INTEGRATION_SPEC.name] = integration
INTEGRATION_SPEC.loader.exec_module(integration)


class GeoParquetPublicationTests(unittest.TestCase):
    def test_write_readback_preserves_points_and_geo_metadata(self) -> None:
        frame = gpd.GeoDataFrame(
            {"source_row": [1, 2], "environment_value": [0.0, None]},
            geometry=[Point(80.0, 7.0), Point(81.0, 8.0)],
            crs="EPSG:4326",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "output.parquet"
            checks = integration.publish_geoparquet(frame, path)
            readback = gpd.read_parquet(path)
        self.assertEqual(checks["rows"], 2)
        self.assertEqual(checks["geoparquet_version"], "1.1.0")
        self.assertEqual(checks["compression"], ["ZSTD"])
        self.assertEqual(readback.geometry.iloc[0], Point(80.0, 7.0))
        self.assertEqual(readback["environment_value"].iloc[0], 0.0)
        self.assertTrue(readback["environment_value"].isna().iloc[1])


if __name__ == "__main__":
    unittest.main()
