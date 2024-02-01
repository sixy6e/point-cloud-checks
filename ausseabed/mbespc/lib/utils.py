from pathlib import Path
from typing import Any, Dict, List, Union, Tuple
import numpy
import rasterio
from rasterio import features
from shapely.geometry import shape
import geopandas


def update_density_no_data(grid_pathname: Path, density_pathname: Path) -> Tuple[int, int]:
    """
    Update the density grid calculated via the PDAL pipeline by accounting
    for the base grids' no-data mask.
    The rationale is to exclude valid zero counts from no-data locations.

    :param grid_pathname: Pathname to the base grid file
    :type grid_pathname: class:`pathlib.Path`
    :param density_pathname: Pathname to the density grid file
    :type density_pathname: class:`pathlib.Path`
    :return: A tuple of ints for the maximum cell density,
       and the total of non-nodata pixels
    :rtype: tuple
    """
    with rasterio.open(str(grid_pathname)) as src:
        with rasterio.open(str(density_pathname), "r+") as den_src:
            # we need determine the max value in order to determine
            # appropriate upper bin for the histogram
            max_ = 0
            cell_count = 0
            for _, window in den_src.block_windows():
                d_data = den_src.read(1, window=window)
                z_data = src.read(1, window=window)
                mask = z_data == src.nodata
                cell_count += (~mask).sum()
                d_data[mask] = den_src.nodata
                max_ = max(max_, numpy.max(d_data))
                den_src.write(d_data, 1, window=window)

    return int(max_), int(cell_count)


def histogram_point_density(
    density_pathname: Path, maxv: int
) -> Tuple[numpy.ndarray, numpy.ndarray]:
    """
    Calculate the frequency histogram of the point density grid layer.
    This routine works in chunked fashion to minimise memory use.
    The method works using a binsize of 1 to provide unique bins
    for values in the range [0, maxv].

    :param density_pathname: Pathname to the density grid file
    :type density_pathname: class:`pathlib.Path`
    :param maxv: Maximum density value to be considered for the histogram
    :type maxv: int
    :return: A tuple of :class: `numpy.ndarray` objects
    :rtype: tuple
    """
    # initialise the histogram that we'll update
    hist = numpy.zeros(maxv + 1, dtype="int64")

    # numpy's histogram is open ended for the final bin i.e.
    # [3, 4] whereas previous bins are half-open [2, 3)
    # so an extra bin is defined to ensure equivalent bin sizes
    # for all the data we care about
    bins = numpy.arange(maxv + 2)

    with rasterio.open(density_pathname) as src:
        for _, window in src.block_windows():
            data = src.read(1, window=window)
            h_tmp, _ = numpy.histogram(data, bins=bins, range=(0, maxv))
            hist += h_tmp

    return hist, bins[:-1]


def sanitize_properties(
    data: Dict[Union[str, None], Any], skip: List[Any] | None = None
) -> Dict[str, Any]:
    """
    Clean the exported properties of a class.
    Private properties are ignored, as are empty strings and properties
    containing None;

    :param data: A dict containing the key value pairs from the
        exported class
    :type data: dict
    :param skip: A list containing keys to skip, or None. Default is None
    :type skip: list or None
    :return: A dict containing only the sanitised key value pairs
    :rtype: dict
    """
    if skip is None:
        skip = []

    data_cp = data.copy()
    for key, val in data.items():
        if key in skip:
            del data_cp[key]
        if key is not None and key[0] == "_":
            del data_cp[key]
        if val == "":
            del data_cp[key]
        if key is None:
            del data_cp[key]

    return data_cp  # type: ignore[return-value]


def mask_finite(data: numpy.ndarray, nodata: int | float) -> numpy.ndarray:
    """
    Create a boolean mask identifying nodata and data.
    Whilst establishing a mask is simple via standard operators, catering for
    non-finite data is not, i.e. NaN != NaN
    """
    is_finite = numpy.isfinite(nodata)

    if is_finite:
        mask = data != nodata
    else:
        mask = numpy.isfinite(data)

    return mask


def vectorise_low_density(
    density_pathname: Path,
    min_soundings: int,
) -> geopandas.GeoDataFrame:
    """
    Given a criterion of minimum soundings per cell, identify the cells
    and convert the results to vector.

    :param density_pathname: Pathname to the density grid file
    :type density_pathname: class:`pathlib.Path`
    :param min_soundings: Minumum value for a pixel to be considered valid
    :type min_soundings: int
    :return: A geopandas GeoDataFrame containing the vectorised cell locations
        failing to meet the minimum criterion.
    :rtype: geopandas.GeoDataFrame
    """
    geoms = []

    with rasterio.open(density_pathname) as dataset:
        nodata = dataset.nodata
        for _, window in dataset.block_windows():
            transform = dataset.window_transform(window)
            data = dataset.read(1, window=window)
            mask = mask_finite(data, nodata)

            # update mask with soundings that don't meet criterion
            mask &= data < min_soundings

            # vectorise
            shapes = features.shapes(
                data, mask, connectivity=8, transform=transform
            )
            for shp, _ in shapes:
                geoms.append(shape(shp))

        gdf = geopandas.GeoDataFrame({"geometry": geoms}, crs=dataset.crs)

    return gdf
