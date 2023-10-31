"""
Resolution independent density check
"""

from pathlib import Path

class ResolutionIndependentDensityCheck():

    def __init__(
        self,
        point_cloud_file: Path,
        grid_file: Path
    ) -> None:
        self.point_cloud_file = point_cloud_file
        self.grid_file = grid_file

    def run(self):
        # total number of non-nodata nodes in grid
        self.total_nodes = 0
        # total number of nodes that failed density check
        self.failed_nodes = 0

        # TODO: all the actual check stuff, update above values with output
        raise RuntimeError(f"{self.__name__}.run is not implemented")

