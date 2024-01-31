import json
from pathlib import Path
import tempfile
from typing import Tuple, Optional

import numpy
import rasterio  # type: ignore[import]
import pdal  # type: ignore[import]

from ausseabed.mbespc.lib import pdal_reader, pdal_filter, pdal_writer, errors, utils


def density(
    grid_dataset_pathname: Path, point_cloud_pathname: Path, outdir: Optional[Path] = None
) -> Tuple[numpy.ndarray, numpy.ndarray, int]:  # noqa: E501
    """
    Workflow for creating the density grid.
    """
    with tempfile.TemporaryDirectory(suffix=".density-check") as tmpdir:
        with rasterio.open(str(grid_dataset_pathname)) as src:
            # define reader section of the pipeline
            reader = pdal_reader.PdalDriver.from_string(str(point_cloud_pathname))  # noqa: E501

            # reprojection
            # from_crs in this instance means build obj from crs
            projection = pdal_filter.Reprojection.from_crs(src.crs)

            # writer
            out_pathname = Path(tmpdir).joinpath("density.tiledb")  # type: ignore[attr-defined] # pylint: disable=line-too-long # noqa: E501
            writer = pdal_writer.GdalWriter.from_dataset(src, out_pathname)

            pipeline_stages = [
                reader.to_dict(),
                projection.to_dict(),
                writer.to_dict(),
            ]

            json_pipeline = json.dumps(pipeline_stages)
            pipeline = pdal.Pipeline(json_pipeline)

            try:
                pipeline.execute_streaming()
            except Exception as err:
                msg = f"Error running pipeline: {json_pipeline}"
                raise errors.MbesPcError(msg) from err

        # update density grid with no-data mask from base grid
        maxv, cell_count = utils.update_density_no_data(
            grid_dataset_pathname, out_pathname
        )  # noqa: E501

        # calculate histogram of point density (not probability density)
        hist, bins = utils.histogram_point_density(out_pathname, maxv)

        if outdir is not None:
            kwargs = {
                "compress": "deflate",
                "zlevel": 6,
                "tiled": "yes",
                "blockxsize": 256,
                "blockysize": 256,
                "predictor": 2,
            }
            export_pathname = Path(outdir, "density.tif")
            rasterio.shutil.copy(out_pathname, export_pathname, driver="GTiff", **kwargs)

    #

    return hist, bins, cell_count
