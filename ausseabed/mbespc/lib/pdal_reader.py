import json
from pathlib import Path
# from typing import Self  # Self is avail >= py3.11
from typing import Any, Dict, Type, Union

from ausseabed.mbespc.lib import errors, utils


class DriverError(Exception):
    """Simple custom error for PDAL driver specifics."""


class PdalDriver:
    """
    A basic interface for establishing a PDAL reader driver for use within
    a PDAL pipeline JSON construct.
    """

    def __init__(self, pathname: Path):
        self.pathname = pathname
        self._skip = ["pathname"]

    @staticmethod
    def from_string(uri: str):  # -> Self | DriverError:
        """
        Given a string URI, derive the appropriate PDAL driver.
        Reason for a str over a strict Path obj, is that Path will
        strip certain protocol info.
        """
        sub_cls: Union[Type[DriverLas], Type[DriverTileDB]]

        pth = Path(uri)

        match pth.suffix:
            case ".las":
                sub_cls = DriverLas
            case ".laz":
                sub_cls = DriverLas
            case ".tiledb":
                sub_cls = DriverTileDB
            case ".tdb":
                sub_cls = DriverTileDB
            case _:
                msg = f"Could not determine driver for {uri}"
                raise errors.MbesPcError(msg)

        return sub_cls(pth)

    def to_json(self) -> str:
        """
        Export the PDAL reader type to JSON.
        """
        data = self.to_dict()

        return json.dumps(data)

    def to_dict(self) -> Dict[str, Any]:
        """
        Export the PDAL reader type to dict.
        Private properties are ignored, as are empty strings and properties
        containing None;
        (If there is a future need for expanding reader options).
        """
        data = vars(self)

        return utils.sanitize_properties(data, self._skip)


class DriverLas(PdalDriver):
    """Driver specific to LAS/LAZ files."""

    def __init__(self, pathname: Path):
        self.type = "readers.las"
        self.filename = str(pathname)
        super().__init__(pathname)


class DriverTileDB(PdalDriver):
    """Driver specific to TileDB point cloud arrays."""

    def __init__(self, pathname: Path):
        self.type = "readers.tiledb"
        self.strict = False
        self.array_name = str(pathname)
        super().__init__(pathname)
