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
utils for drawio-exporter
"""

import logging
import os
import platform
import shutil
import subprocess
from pathlib import Path

import psutil

logger = logging.getLogger(__name__)


# pylint: disable=too-many-return-statements
def drawio_path() -> Path:
    """
    Return the path to the draw.io executable
    """
    system = platform.system()

    if system == "Darwin":
        for prefix in ["/Applications", "~/Applications"]:
            exe = Path(prefix) / "draw.io.app/Contents/MacOS/draw.io"
            if exe.exists() and os.access(exe, os.X_OK):
                return exe
        return None

    if system == "Linux":
        exe = shutil.which("drawio")
        if exe is not None:
            return Path(exe)
        exe = Path("/opt/draw.io/drawio")
        if exe.exists() and os.access(exe, os.X_OK):
            return drawio_path
        return None

    if system == "Windows":
        exe = shutil.which("draw.io.exe")
        if exe is not None:
            return Path(exe)
        for arch in ["", "(x86)"]:
            exe = Path(f"C:/Program Files{arch}/draw.io/draw.io.exe")
            if exe.exists():
                return exe
        return None

    return None


def filtered_lines(lines, line_filter):
    """
    Filter lines
    """
    seen = set()
    for line in lines:
        if len(line) == 0:
            continue
        if line in seen:
            continue
        if not any(f in line for f in line_filter):
            seen.add(line)
            yield line


def xvfb_pid():
    """
    Return the PID of the Xvfb process or None
    """
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] == "Xvfb":
            return proc.info["pid"]
    return None


def check_xvfb():
    """
    Check if Xvfb is running and start it if not
    """
    pid = xvfb_pid()
    if pid is not None:
        logger.debug("Xvfb is already running (PID = %d)", pid)
        return
    logger.info("Starting Xvfb")
    # pylint: disable=consider-using-with
    subprocess.Popen(
        ["Xvfb", ":42", "-screen", "0", "1024x768x24"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    pid = xvfb_pid()
    if pid is None:
        logger.fatal("Failed to start Xvfb")
