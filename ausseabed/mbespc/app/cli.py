#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Command line tool that executes quality assurance checks on point clouds
    derived from multibeam echosounder data.
"""

import click
from pathlib import Path

from ausseabed.mbespc.lib.density_check import AlgorithmIndependentDensityCheck


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
    type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True),
    help="Path to input point cloud file"
)
@click.option(
    '-gf', '--grid-file',
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True),
    help=(
        "Path to input gridded file. Resolution, target extents, and "
        "CRS will be extracted from this file."
    )
)
@click.option(
    '-mc', '--minimum-count',
    type=int,
    default=5,
    show_default=True,
    help=(
        "Minimum density value per cell. "
    )
)
@click.option(
    '-mcp', '--minimum-count-percentage',
    type=float,
    default=95.0,
    show_default=True,
    help=(
        "Minimum density value per cell dataset percentage"
    )
)
def density_check(
        point_file: Path,
        grid_file: Path,
        minimum_count: int,
        minimum_count_percentage: float
    ):
    """ Command runs the resolution independent density check only
    """
    click.echo("Running density check")
    density_check = AlgorithmIndependentDensityCheck(
        point_cloud_file=point_file,
        grid_file=grid_file,
        minimum_count=minimum_count,
        minimum_count_percentage=minimum_count_percentage
    )
    density_check.run()

    # print out some summary info from the check run
    click.echo(f"Check passed: {density_check.passed}")
    click.echo(f"{density_check.failed_nodes} / {density_check.total_nodes} failed")
    click.echo("Histogram (density value, cells count)")

    hist_strs = [f"  {d : 3}, {c : 8}" for d,c in density_check.histogram]
    click.echo("\n".join(hist_strs))


if __name__ == '__main__':
    cli()
