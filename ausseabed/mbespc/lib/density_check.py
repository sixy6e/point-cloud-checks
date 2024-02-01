"""
Resolution independent density check
"""

from pathlib import Path
from typing import Optional
import tempfile
import json
import geopandas
import shutil
import logging

from ausseabed.qajson.model import QajsonParam, QajsonOutputs, QajsonExecution
from ausseabed.mbespc.lib import pdal_pipeline, utils

LOG = logging.getLogger(__name__)


class AlgorithmIndependentDensityCheck:
    # details used by the QAX plugin
    id = "1bdb56d7-a725-42b4-8c42-10dbe0c0dbda"
    name = "Algorithm Independent Density Check"
    version = "1"
    input_params = [
        QajsonParam("Minimum Soundings per node", 5),
        QajsonParam("Minimum Soundings per node percentage", 95.0),
    ]

    def __init__(
        self,
        point_cloud_file: Path,
        grid_file: Path,
        minimum_count: int,
        minimum_count_percentage: float,
        outdir: Optional[Path] = None
    ) -> None:
        self.point_cloud_file = point_cloud_file
        self.grid_file = grid_file
        self.minimum_count = minimum_count
        self.minimum_count_percentage = minimum_count_percentage
        self.outdir = outdir

        # total number of non-nodata nodes in grid
        self.total_nodes: Optional[int] = None
        # total number of nodes that failed density check
        self.failed_nodes: Optional[int] = None
        # Did the check pass
        self.passed: Optional[bool] = None
        # histogram - list of tuples. First tuple item is the density count,
        # second tuple item is the number of grid cells that have this
        # density
        self.histogram: Optional[list[tuple[int, int]]] = None
        self.percentage: Optional[float] = None
        self.percentage_passed: Optional[float] = None
        self.percentage_failed: Optional[float] = None

        self.gdf: Optional[geopandas.GeoDataFrame] = None

    def run(self):
        """
        Runs/executes the density check workflow.
        Requires not just the point cloud dataset, but also the grid file which
        will be used as the basis on which to define the density grid.
        Grid properties include:
            * Spatial extent
            * Width
            * Height
            * Resolution
            * CRS
            * No data value (assumed to be finite)
        """
        with tempfile.TemporaryDirectory(suffix=".density-check") as tmpdir:
            out_pathname = Path(tmpdir).joinpath("density.tif") 

            LOG.info("Calculating density")
            hist, bins, cell_count = pdal_pipeline.density(
                self.grid_file, self.point_cloud_file, out_pathname
            )  # noqa: E501

            LOG.info("Converting low density pixels to vector")
            gdf = utils.vectorise_low_density(out_pathname, self.minimum_count)

            if self.outdir is not None:
                outdir = self.outdir / self.point_cloud_file.stem / self.name
                outdir.mkdir(parents=True, exist_ok=True)

                _ = shutil.copy(out_pathname, outdir)

                gdf_pathname = outdir / "low-density-pixels.shp"
                gdf.to_file(gdf_pathname, driver="ESRI Shapefile")

        failed_nodes = int(hist[0:self.minimum_count].sum())
        percentage = float((failed_nodes / cell_count) * 100)
        percentage_passed = 100 - percentage
        passed = bool(percentage_passed > self.minimum_count_percentage)

        # total number of non-nodata nodes in grid
        self.total_nodes = cell_count

        # total number of nodes that failed density check
        self.failed_nodes = failed_nodes
        self.percentage_failed = percentage
        self.percentage_passed = percentage_passed

        self.passed = passed

        # (density, number of cells that have that density)
        self.histogram = list(zip(bins.tolist(), hist.tolist()))

        self.gdf = gdf
