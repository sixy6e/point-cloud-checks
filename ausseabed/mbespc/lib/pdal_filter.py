import json
from typing import Any, Dict
# from typing import Self  # Self is avail >= py3.11

from rasterio.crs import CRS  # type: ignore[import] # pylint: disable=E0611
from ausseabed.mbespc.lib import utils


class Reprojection:
    """JSON Helper class for the PDAL reprojection filter."""

    def __init__(self, out_crs: str):
        self.type = "filters.reprojection"
        self.out_srs = out_crs

    @classmethod
    def from_crs(cls, out_crs: CRS):  # -> Self:
        """
        Instantiate the Reprojection class given a rasterio.crs.CRS object.
        """
        crs = out_crs.to_string()

        return cls(crs)

    def to_json(self) -> str:
        """
        Export the PDAL filter type to JSON.
        """
        data = self.to_dict()

        return json.dumps(data)

    def to_dict(self) -> Dict[str, Any]:
        """
        Export the PDAL filter type to dict.
        Private properties are ignored.
        """
        data = vars(self)

        return utils.sanitize_properties(data)
