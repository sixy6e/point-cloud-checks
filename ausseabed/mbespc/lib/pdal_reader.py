import json
from pathlib import Path


# This driver definition might be simpler to define via attrs


class DriverError(Exception):
    """Simple custom error for PDAL driver specifics."""

    # TODO; see how qax handles errors, and remove this custom exception


class PdalDriver:
    """
    A basic interface for establishing a PDAL reader driver for use within
    a PDAL pipeline JSON construct.
    """

    def __init__(self, uri: Path):
        self.uri = uri
        self._skip = ["uri"]

    @classmethod
    def from_uri(cls, uri: Path):
        """Given a URI, derive the proper PDAL driver."""
        loader = {
            ".las": DriverLas,
            ".laz": DriverLas,
            ".tiledb": DriverTileDB,
            ".tdb": DriverTileDB,
        }

        try:
            sub_cls = loader[uri.suffix]
        except KeyError as err:
            msg = f"Could not determine driver for {uri}"
            raise DriverError(msg) from err

        return sub_cls(uri)

    def to_json(self):
        """
        Export the PDAL reader type to JSON.
        Private properties are ignored, as are empty strings and properties
        containing None;
        (If there is a future need for expanding reader options).
        """
        data = vars(self)
        json_d = {}

        for key, val in data:
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

    def __init__(self, uri: Path):
        self.type = "readers.las"
        self.filename = str(uri)
        super().__init__(uri)


class DriverTileDB(PdalDriver):
    """Driver specific to TileDB point cloud arrays."""

    def __init__(self, uri: Path):
        self.type = "readers.tiledb"
        self.strict = False
        self.array_name = str(uri)
        super().__init__(uri)
