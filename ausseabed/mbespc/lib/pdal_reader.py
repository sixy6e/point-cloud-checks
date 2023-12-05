import json
from pathlib import Path
# from typing import Self  # Self is avail >= py3.11


# This driver definition might be simpler to define via attrs


class DriverError(Exception):
    """Simple custom error for PDAL driver specifics."""

    # TODO; see how qax handles errors, and remove this custom exception


class PdalDriver:
    """
    A basic interface for establishing a PDAL reader driver for use within
    a PDAL pipeline JSON construct.
    """

    def __init__(self, pathname: Path):
        self.pathname = pathname
        self._skip = ["pathname"]

    @staticmethod
    def from_string(uri: str) -> PdalDriver | DriverError:
        """Given a string URI, derive the appropriate PDAL driver."""
        loader = {
            ".las": DriverLas,
            ".laz": DriverLas,
            ".tiledb": DriverTileDB,
            ".tdb": DriverTileDB,
        }

        pth = Path(uri)

        try:
            sub_cls = loader[pth.suffix]
        except KeyError as err:
            msg = f"Could not determine driver for {uri}"
            raise DriverError(msg) from err

        return sub_cls(pth)

    def to_json(self):
        """
        Export the PDAL reader type to JSON.
        Private properties are ignored, as are empty strings and properties
        containing None;
        (If there is a future need for expanding reader options).
        """
        data = vars(self)
        json_d = {}

        for key, val in data.items():
            if key in self._skip:
                continue
            if key[0] == "_":
                continue
            if val == "":
                continue
            if key is None:
                continue
            json_d[key] = val

        return json.dumps(json_d)


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
