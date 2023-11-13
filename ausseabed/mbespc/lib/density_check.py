"""
Resolution independent density check
"""

from pathlib import Path


from ausseabed.qajson.model import QajsonParam, QajsonOutputs, QajsonExecution


class AlgorithmIndependentDensityCheck():

    id = '1bdb56d7-a725-42b4-8c42-10dbe0c0dbda'
    name = 'Algorithm Independent Density Check'
    version = '1'
    input_params = []

    def __init__(
        self,
        point_cloud_file: Path,
        grid_file: Path,
        minimum_count: int
    ) -> None:
        self.point_cloud_file = point_cloud_file
        self.grid_file = grid_file
        self.minimum_count = minimum_count

    def run(self):
        # total number of non-nodata nodes in grid
        self.total_nodes = 0
        # total number of nodes that failed density check
        self.failed_nodes = 0

        # TODO: check implementation
        # - generate density grid version of point cloud based on CRS and
        #   geotransform of the grid_file
        #     - It's believed the easiest was to get this info from users is to
        #       use an existing grid file as a template. Doesn't matter what data
        #       it stores, we'll just extract resolution and corner coords
        # - Check how many nodes (pixels) of the grid are under the minimum_count
        #   and set the failed_nodes value

