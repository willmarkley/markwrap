'''
Python wrapper for the brew (Homebrew) command

Please manually test and verify before committing changes.
'''

import logging
import shutil
from . import process

BREW="/usr/local/bin/brew"

logging.debug("Validating Homebrew install at %s", BREW)
validate_result = shutil.which(BREW)
if (validate_result is None):
	logging.error("Homebrew not found with shutil at %s", BREW)
	raise RuntimeError()
logging.debug("Homebrew found at %s", BREW)
process.quietRun([BREW,"--version"])
logging.debug("Validated Homebrew install at %s", BREW)


def list():
	return process.run([BREW, "list", "-1"])

def update():
	process.run([BREW, "update"])

def upgrade():
	process.run([BREW, "upgrade"])
	process.run([BREW, "cask", "upgrade"])

