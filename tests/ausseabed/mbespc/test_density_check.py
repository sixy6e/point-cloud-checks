import os
import pyproj
from pathlib import Path
from tests.ausseabed.testutils import LasTestFileBuilder


def test_simple():
    assert True


def get_generated_test_data_dir() -> Path:
    """
    Get a folder where programmatically generated test data files can be
    created
    """
    current_dir = Path(os.getcwd())
    test_dir = current_dir.joinpath('tests')
    testdata_dir = test_dir.joinpath('generated_test_data')
    if not testdata_dir.is_dir():
        testdata_dir.mkdir()
    return testdata_dir


def test_lastestbuilder():
    data_dir = get_generated_test_data_dir()
    test_las_file = data_dir.joinpath("test.las")

    print(f"creating: {str(test_las_file)}")

    densities = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [10, 11, 12]
    ]

    lb = LasTestFileBuilder(
        densities=densities,
        top_right_x=16129836,
        top_right_y=-4572563,
        resolution=1000,
        crs=pyproj.CRS.from_epsg(3857),
        output_file=test_las_file
    )
    lb.run()




    
    

