"""
Collection of utils used by test cases
"""

import laspy
import numpy as np
import osgeo
import random
import pyproj
import pyproj.enums

from osgeo import gdal, osr
from pathlib import Path


class LasTestFileBuilder():
    """
    Build a simple las file that randomly generates points to satisfy
    a 2d point density array.
    """

    def __init__(
        self,
        densities: list[list[int]],
        top_left_x: float,
        top_left_y: float,
        resolution: float,
        crs: pyproj.CRS,
        output_file: Path
    ) -> None:
        self.densities = densities
        self.top_left_x = top_left_x
        self.top_left_y = top_left_y
        self.resolution = resolution
        self.crs = crs
        self.output_file = output_file

    def run(self):
        x_coordinates:list[float] = []
        y_coordinates:list[float] = []
        z_coordinates:list[float] = []

        x = self.top_left_x
        y = self.top_left_y
        for row in self.densities:
            # loop through all the rows of the grid
            for col in row:
                # loop through all the columns of the grid
                # each col value is the density count - the number
                # of points we're going to generate in this cell
                for pt_count in range(0, col):
                    x_max = x + self.resolution
                    y_min = y - self.resolution
                    # currently the height information isn't particularly relevant
                    # so just use a dummy value 
                    pt_z = 2.3
                    pt_x = random.uniform(x, x_max)
                    pt_y = random.uniform(y_min, y)

                    x_coordinates.append(pt_x)
                    y_coordinates.append(pt_y)
                    z_coordinates.append(pt_z)

                x += self.resolution

            x = self.top_left_x
            y -= self.resolution

        x_np = np.array(x_coordinates, dtype=np.int32)
        y_np = np.array(y_coordinates, dtype=np.int32)
        z_np = np.array(z_coordinates, dtype=np.int32)

        header = laspy.header.LasHeader()
        header.add_crs(self.crs)
        header.x_scale = 1.0
        header.y_scale = 1.0
        header.z_scale = 1.0

        las = laspy.create()
        las.header = header
        las.X = x_np
        las.Y = y_np
        las.Z = z_np
        las.update_header()
        las.write(str(self.output_file))


class TifTestFileBuilder():
    """
    Build a simple tif file that includes the values given in a 2d array
    """

    def __init__(
        self,
        values: list[list[int]],
        top_left_x: float,
        top_left_y: float,
        resolution: float,
        crs: pyproj.CRS,
        output_file: Path
    ) -> None:
        self.values = values
        self.top_left_x = top_left_x
        self.top_left_y = top_left_y
        self.resolution = resolution
        self.crs = crs
        self.output_file = output_file

        # optional band name used to set the description field in tif metadata
        self.band_name = None

    def run(self):
        """
        Run the process to build the test geotiff
        """
        driver = gdal.GetDriverByName("GTiff")
        dst_ds = driver.Create(
            str(self.output_file),
            len(self.values[0]),
            len(self.values),
            1,
            gdal.GDT_Int16
        )
        np_2d_array = np.array(self.values, dtype=np.int16)
        
        dst_ds.GetRasterBand(1).WriteArray(np_2d_array)
        dst_ds.GetRasterBand(1).SetNoDataValue(-9999)

        if self.band_name:
            dst_ds.GetRasterBand(1).SetDescription(self.band_name)

        # top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
        dst_ds.SetGeoTransform([
            self.top_left_x,
            self.resolution,
            0,
            self.top_left_y,
            0,
            -1.0 * self.resolution
        ])

        osr_crs = osr.SpatialReference()
        if osgeo.version_info.major < 3:
            osr_crs.ImportFromWkt(self.crs.to_wkt(pyproj.enums.WktVersion.WKT1_GDAL))
        else:
            osr_crs.ImportFromWkt(self.crs.to_wkt())

        dst_ds.SetProjection( osr_crs.ExportToWkt() )
        dst_ds = None


def build_las_and_tif_densities(
        las_file: Path,
        tif_file: Path,
        densities: list[list[int]]
    ):
    """
    Creats a las file with points distributed randomly to match that of the densities
    array. A density tif file is also created. 
    """
    # FWIW the coordinates and CRS details below generate a grid over Port Phillip
    # Bay in Victoria
    lb = LasTestFileBuilder(
        densities=densities,
        top_left_x=16129836,
        top_left_y=-4572563,
        resolution=1000,
        crs=pyproj.CRS.from_epsg(3857),
        output_file=las_file
    )
    lb.run()

    tb = TifTestFileBuilder(
        values=densities,
        top_left_x=16129836,
        top_left_y=-4572563,
        resolution=1000,
        crs=pyproj.CRS.from_epsg(3857),
        output_file=tif_file
    )
    tb.run()