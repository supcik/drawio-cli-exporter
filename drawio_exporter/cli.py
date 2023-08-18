#############################################################################
#
# Copyright (c) 2022 HEIA-FR / ISC
# Haute école d'ingénierie et d'architecture de Fribourg
# Informatique et Systèmes de Communication
#
# SPDX-License-Identifier: MIT OR Apache-2.0
#
# Created : Jacques Supcik <jacques.supcik@hefr.ch>, 18-Aug-2023
#
#############################################################################

"""
drawio-exporter is a wrapper around draw.io to export diagrams from the command line.
"""

import logging
import os
import platform
import subprocess

import click

from . import utils

logger = logging.getLogger(__name__)

stderr_filter = [
    "Failed to connect to socket",
    "Could not parse server address",
    "Floss manager not present",
    "Exiting GPU process",
    "called with multiple threads",
    "extension not supported",
    "Failed to send GpuControl.CreateCommandBuffer",
    "Init observer found at shutdown",
]

stdout_filter = [
    "Checking for beta autoupdate feature for deb/rpm distributions",
    "Found package-type: deb",
]


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("input-file", type=click.Path(exists=True))
@click.argument("drawio_args", nargs=-1, type=click.UNPROCESSED)
@click.option("--debug", is_flag=True)
@click.option("--drawio-path", default=None, type=click.Path(exists=True))
@click.option("--display", default=":42", type=str)
@click.option("--skip-xvfb-check", is_flag=True, help="Skip Xvfb check")
# pylint: disable=too-many-arguments
def cli(input_file, drawio_args, debug, drawio_path, display, skip_xvfb_check):
    """
    command line interface for drawio-exporter
    """
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if debug else logging.INFO,
    )

    logger.debug("System: %s", platform.system())
    env = {}
    if platform.system() == "Linux" and os.getenv("DISPLAY") is None:
        if not skip_xvfb_check:
            utils.check_xvfb()
        env["DISPLAY"] = display

    if drawio_path is None:
        drawio_path = utils.drawio_path()

    if drawio_path is None:
        logger.fatal("draw.io not found")
        return

    logger.debug("draw.io found at: %s", drawio_path)

    cmd = [
        drawio_path,
        input_file,
        "--no-sandbox",
        "--export",
    ]
    cmd.extend(drawio_args)

    res = subprocess.run(cmd, capture_output=True, text=True, check=True, env=env)

    for line in utils.filtered_lines(res.stdout.split("\n"), stdout_filter):
        logger.info(line)
    for line in utils.filtered_lines(res.stderr.split("\n"), stderr_filter):
        logger.error(line)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    cli()
