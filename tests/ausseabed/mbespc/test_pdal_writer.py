from pathlib import Path
import numpy
from rasterio.crs import CRS
from rasterio import MemoryFile
from affine import Affine

from ausseabed.mbespc.lib import pdal_writer


def test_gdal_writer_json():
    """Test that the json dump is as expected."""
    pth = Path("datafile.tif")
    width, height = (10, 10)
    transform = Affine.from_gdal(*(284937.25, 0.5, 0.0, 5758302.75, 0.0, -0.5))
    crs = CRS.from_epsg(32755)
    data = numpy.random.randint(0, 256, (height, width)).astype("uint8")
    kwargs = {
        "width": width,
        "height": height,
        "count": 1,
        "dtype": "uint8",
        "crs": crs,
        "transform": transform,
        "driver": "GTiff",
    }

    with MemoryFile() as memfile:
        with memfile.open(**kwargs) as outds:
            outds.write(data, 1)
        with memfile.open() as inds:
            obj = pdal_writer.GdalWriter.from_dataset(inds, pth)

    expected = '{"type": "writers.gdal", "binmode": true, "filename": "datafile.tif", "resolution": 0.5, "origin_x": 284937.25, "origin_y": 5758297.75, "width": 10, "height": 10, "override_srs": "EPSG:32755", "output_type": "count", "gdaldriver": "TileDB", "gdalopts": ["COMPRESSION=ZSTD", "COMPRESSION_LEVEL=16", "BLOCKSIZE=256,256"], "nodata": -9999, "data_type": "int"}'  # pylint: disable=line-too-long # noqa: E501

    assert obj.to_json() == expected
