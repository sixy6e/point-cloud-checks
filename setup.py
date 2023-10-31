from setuptools import setup, find_packages

setup(
    name='ausseabed.mbespc',
    namespace_packages=['ausseabed'],
    version='0.0.1',
    url='https://github.com/ausseabed/point-cloud-checks',
    author=(
        "Josh Sixsmith;"
        "Lachlan Hurst;"
    ),
    author_email=(
        "joshua.sixsmith@ga.gov.au;"
        "lachlan.hurst@gmail.com;"
    ),
    description=(
        'Quality Assurance checks for point clouds derived from Multi Beam Echo '
        'Sounder data'
    ),
    entry_points={
        "gui_scripts": [],
        "console_scripts": [
            'mbespc = ausseabed.mbespc.app.cli:cli',
        ],
    },
    packages=[
        'ausseabed.mbespc',
        'ausseabed.mbespc.app',
        'ausseabed.mbespc.lib',
        'ausseabed.mbespc.qax'
    ],
    zip_safe=False,
    package_data={},
    install_requires=[
        'Click',
        'ausseabed.qajson'
    ],
    tests_require=['pytest'],
)
