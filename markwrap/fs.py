'''
Python wrapper for filesystem commands
'''

import logging
import os
import shutil
from .util import check


def mv(source, destination):
	logging.info("Parameters: source=[%s] destination=[%s]", str(source), str(destination))
	check.fileSizeNonZero(source)
	check.isDir(destination)

	expected = os.path.join(destination, os.path.basename(source))
	check.nonexistent(expected)

	logging.info("Moving %s to directory %s", source, destination)
	moved = shutil.move(source, destination)
	check.fileSizeNonZero(moved)
	check.equal(expected, moved)
	check.nonexistent(source)
	logging.info("Moved %s to file %s", source, moved)

def cp(source, destination):
	logging.info("Parameters: source=[%s] destination=[%s]", str(source), str(destination))
	check.fileSizeNonZero(source)
	check.isDir(destination)

	expected = os.path.join(destination, os.path.basename(source))
	check.nonexistent(expected)

	logging.info("Copying %s to directory %s", source, destination)
	copied = shutil.copy(source, destination)
	check.fileSizeNonZero(copied)
	check.equal(expected, copied)
	check.fileSizeNonZero(source)
	logging.info("Copied %s to file %s", source, copied)

	return copied
