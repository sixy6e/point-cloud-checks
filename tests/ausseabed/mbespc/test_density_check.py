import tempfile
from pathlib import Path

from ausseabed.mbespc.lib.density_check import ResolutionIndependentDensityCheck
from tests.ausseabed.testutils import build_las_and_tif_densities


def test_density_check_simple():

    densities = [
        [1, 1, 5],
        [5, 5, 5],
        [6, 5, 7],
        [5, 6, 9]
    ]

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        test_las = tmp_path.joinpath('test.las')
        test_tif = tmp_path.joinpath('test.tif')

        # generate temporary test files from the density array
        build_las_and_tif_densities(test_las, test_tif, densities)

        # now run these test files through the check
        check = ResolutionIndependentDensityCheck(test_las, test_tif, 5)
        check.run()

        # only the two `1` density counts should fail the threshold of 5
        assert check.failed_nodes == 2
        assert check.total_nodes == 12
