import pytest
from rasterio.crs import CRS

from ausseabed.mbespc.lib import pdal_filter


def test_filter_reprojection_json():
    """Test that the json dump is as expected."""
    crs = CRS.from_epsg(4326)
    filt_prj = pdal_filter.Reprojection.from_crs(crs)
    expected = '{"type": "filters.reprojection", "out_srs": "EPSG:4326"}'
    assert filt_prj.to_json() == expected
