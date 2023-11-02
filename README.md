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

# Testing

To run unit tests

    pytest -s

## Generating test datasets

The project includes a special test module that when run will produce some simple test files that can be used to manually test this application. To run only this process use the following command.

    pytest -s tests/ausseabed/mbespc/test_generate_data.py

When complete a new folder will be created that includes several test files (.las and .tif), it can be found at

    ./tests/generated_test_data/

