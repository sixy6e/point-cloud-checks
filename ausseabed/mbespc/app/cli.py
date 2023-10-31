#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Command line tool that executes quality assurance checks on point clouds
    derived from multibeam echosounder data.
"""

import click
from pathlib import Path

from ausseabed.mbespc.lib.density_check import ResolutionIndependentDensityCheck


@click.group()
def cli():
    pass


@cli.command(help=(
    "Run point cloud quality assurance checks over input defined "
    "within QAJSON file")
)
@click.option(
    '-i', '--input',
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    help='Path to input QA JSON file')
def qajson(
        input
    ):
    """
    Run point cloud quality assurance checks over input defined
    within QAJSON file
    """

    # TODO: later
    # this is where a QAJSON file would be loaded, and the files+checks+params
    # defined in the QAJSON would be run through the appropriate checks.
    # Not currently essential as this will primarily be done through QAX

    click.echo("Not implemented")


@cli.command(help=(
    "Run resolution independent density check on point cloud")
)
@click.option(
    '-pf', '--point-file',
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    help="Path to input point cloud file"
)
@click.option(
    '-gf', '--grid-file',
    required=True,
    help=(
        "Path to input gridded file. Resolution, target extents, and "
        "CRS will be extracted from this file."
    )
)
def density_check(point_file: Path, grid_file: Path):
    """ Command runs the resolution independent density check only
    """
    density_check = ResolutionIndependentDensityCheck(
        point_cloud_file=point_file,
        grid_file=grid_file
    )
    density_check.run()

    click.echo(f"{density_check.failed_nodes} / {density_check.total_nodes} failed")


if __name__ == '__main__':
    cli()
