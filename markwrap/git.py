'''
Python wrapper for the git command

Please manually test and verify before committing changes.
'''

import logging
import shutil
from . import check
from . import process

GIT="/usr/local/bin/git"

logging.debug("Validating git install at %s", GIT)
validate_result = shutil.which(GIT)
if (validate_result is None):
	logging.error("git not found with shutil at %s", GIT)
	raise RuntimeError()
logging.debug("git found at %s", GIT)
process.quietRun([GIT,"--version"])
logging.debug("Validated git install at %s", GIT)


def nodiff(repoDir):
	check.isDir(repoDir)
	process.quietRun([GIT, "add", "--intent-to-add", "."], cwd=repoDir)
	result = process.run([GIT, "diff", "origin/master"], cwd=repoDir)
	if len(result) == 0:
		return True
	return False

def headHash(repoDir):
	check.isDir(repoDir)
	return process.run([GIT, "rev-parse", "HEAD"], cwd=repoDir).rstrip()
