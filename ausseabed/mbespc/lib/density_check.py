"""
Resolution independent density check
"""

from pathlib import Path
from typing import Optional

from ausseabed.qajson.model import QajsonParam, QajsonOutputs, QajsonExecution


class AlgorithmIndependentDensityCheck():

    # details used by the QAX plugin
    id = '1bdb56d7-a725-42b4-8c42-10dbe0c0dbda'
    name = 'Algorithm Independent Density Check'
    version = '1'
    input_params = [
        QajsonParam("Minimum Soundings per node", 5),
        QajsonParam("Minimum Soundings per node percentage", 95.0),
    ]

    def __init__(
        self,
        point_cloud_file: Path,
        grid_file: Path,
        minimum_count: int,
        minimum_count_percentage: float
    ) -> None:
        self.point_cloud_file = point_cloud_file
        self.grid_file = grid_file
        self.minimum_count = minimum_count
        self.minimum_count_percentage = minimum_count_percentage

        # total number of non-nodata nodes in grid
        self.total_nodes:Optional[int] = None
        # total number of nodes that failed density check
        self.failed_nodes:Optional[int] = None
        # Did the check pass
        self.passed:Optional[bool] = None
        # histogram - list of tuples. First tuple item is the density count,
        # second tuple item is the number of grid cells that have this
        # density
        self.histogram: Optional[list[tuple[int,int]]] = None

    def run(self):
        # TODO: check implementation
        # - generate density grid version of point cloud based on CRS and
        #   geotransform of the grid_file
        #     - It's believed the easiest was to get this info from users is to
        #       use an existing grid file as a template. Doesn't matter what data
        #       it stores, we'll just extract resolution and corner coords
        # - Check how many nodes (pixels) of the grid are under the minimum_count
        #   and set the failed_nodes value

        # NOTE: following code is placeholder / dummy values

        # total number of non-nodata nodes in grid
        self.total_nodes = 100
        # total number of nodes that failed density check
        self.failed_nodes = 4
        self.passed = True

        # (density, number of cells that have that density)
        self.histogram = [
            (0, 10),
            (1, 20),
            (3, 40),
            (4, 50),
            (5, 60),
        ]
