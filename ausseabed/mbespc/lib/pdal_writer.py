import json
from pathlib import Path
from typing import List, Dict, Any
# from typing import Self  # Self is avail >= py3.11

import rasterio  # type: ignore[import]

from ausseabed.mbespc.lib import utils


class GdalWriter:
    """
    Basic JSON Helper class for the PDAL GDAL writer.
    Doesn't cater for all options in the PDAL writers.gdal operator.
    """

    def __init__(
        self,
        filename: str,
        resolution: float,
        ll_x: float,
        ll_y: float,
        width: int,
        height: int,
        output_crs: str,
    ):
        self.type = "writers.gdal"
        self.binmode: bool = True
        self.filename: str = filename
        self.resolution: float = resolution
        self.origin_x: float = ll_x
        self.origin_y: float = ll_y
        self.width: int = width
        self.height: int = height
        self.override_srs: str = output_crs
        self.output_type: str = "count"
        # TODO; change over to GTiff once prototyping is complete
        self.gdaldriver: str = "TileDB"
        self.gdalopts: List[str] = [
            "COMPRESSION=ZSTD",
            "COMPRESSION_LEVEL=16",
            "BLOCKXSIZE=256",
            "BLOCKYSIZE=256",
        ]
        self.nodata = -9999
        self.data_type = "int"

    @classmethod
    def from_dataset(
        cls, dataset: rasterio.DatasetReader, out_pathname: Path
    ):  # -> Self:
        """Constructor for GdalWriter via a rasterio dataset."""
        resolution = dataset.res[0]
        crs = dataset.crs.to_string()
        height = dataset.height
        width = dataset.width
        # ds.transform * (0, height) == dataset.xy(height-1, 0, offset="ll")
        # PDAL defines grid origin as lower left of 2d array
        origin_x, origin_y = dataset.transform * (0, height)
        obj = cls(
            str(out_pathname),
            resolution,
            origin_x,
            origin_y,
            width,
            height,
            crs,
        )
        return obj

    def to_json(self) -> str:
        """
        Export the PDAL writer type to JSON.
        """
        data = self.to_dict()

        return json.dumps(data)

    def to_dict(self) -> Dict[str, Any]:
        """
        Export the PDAL writer type to dict.
        Private properties are ignored.
        """
        data = vars(self)

        return utils.sanitize_properties(data)
