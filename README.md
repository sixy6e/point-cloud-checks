# point-cloud-checks
Point cloud checks for bathymetry data

# Installation

Assumes a miniconda Python distribution has been installed.

    git clone https://github.com/ausseabed/point-cloud-checks
    cd point-cloud-checks

    conda env create --file conda.yml
    conda activate mbespc

    pip install .

Note: to install a development version include the `-e` parameter in the last command (e.g.; `pip install -e .`).

# Tests

To run unit tests

    pytest -s


