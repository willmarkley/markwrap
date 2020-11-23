'''
Python wrapper for the brew (Homebrew) command

Please manually test and verify before committing changes.
'''

import logging
import shutil
from .util import process

BREW="/usr/local/bin/brew"

logging.debug("Validating Homebrew install at %s", BREW)
validate_result = shutil.which(BREW)
if (validate_result is None):
	logging.error("Homebrew not found with shutil at %s", BREW)
	raise RuntimeError()
logging.debug("Homebrew found at %s", BREW)
process.quietRun([BREW,"--version"])
logging.debug("Validated Homebrew install at %s", BREW)


def listFormulae():
	return process.run([BREW, "list", "--formulae", "-1"])

def listCasks():
	return process.run([BREW, "list", "--casks", "-1"])

def update():
	process.run([BREW, "update"])

def upgrade():
	process.run([BREW, "upgrade"])
