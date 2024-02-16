import logging
import os
import sys
from pathlib import Path

LOG = logging.getLogger(__name__)

# when bundled into an exe by pyinstall, pdal doesn't quite get set up correctly
# requiring certain env vars be set in order to find pdal libs
# see https://github.com/PDAL/python/issues/145
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # running in pyinstaller bundle
    bundle_path = Path(sys._MEIPASS)
    pdal_path = bundle_path.joinpath('pdal')
    os.environ['PDAL_DRIVER_PATH'] = str(pdal_path.resolve())

    LOG.info("ausseabed.mbespc running in pyinstaller bundle")
    LOG.info(f"set env var PDAL_DRIVER_PATH = {os.environ['PDAL_DRIVER_PATH']}")
else:
    # running as normal python process
    LOG.info("ausseabed.mbespc running in python process")
