from pathlib import Path
import pytest

from ausseabed.mbespc.lib.density_check import AlgorithmIndependentDensityCheck
from tests.ausseabed.testutils import build_las_and_tif_densities


@pytest.fixture(scope="session")
def data_files(tmp_path_factory):
    test_las = tmp_path_factory.mktemp("data-files") / "test.las"
    test_tif = tmp_path_factory.mktemp("data-files") / "test.tif"

    densities = [
        [1, 1, 5],
        [5, 5, 5],
        [6, 5, 7],
        [5, 6, 9],
    ]

    # generate temporary test files from the density array
    build_las_and_tif_densities(test_las, test_tif, densities)

    return test_las, test_tif


def test_density_check_simple(data_files):
    """
    Only the two `1s` should fail the threshold of 5.
    """
    test_las, test_tif = data_files
    min_threshold = 5
    min_percentage = 0.83
    hist = [
        (0, 0),
        (1, 2),
        (2, 0),
        (3, 0),
        (4, 0),
        (5, 6),
        (6, 2),
        (7, 1),
        (8, 0),
        (9, 1),
    ]  # (bin, frequency/density)

    # intialise and execute
    check = AlgorithmIndependentDensityCheck(
        test_las, test_tif, min_threshold, min_percentage
    )
    check.run()

    print(check.failed_nodes)
    print(check.histogram)

    assert all(
        [
            check.failed_nodes == 2,
            check.total_nodes == 12,
            check.passed,
            all(check.histogram[i] == val for i, val in enumerate(hist)),
        ]
    )
