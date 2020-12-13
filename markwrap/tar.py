'''
Python wrapper for the tar command
'''

import logging
import os
import tarfile
from .util import check

def compress(dirs, tarballName):
	logging.info("Parameters: dirs=[%s] tarballName=[%s]", str(dirs), str(tarballName))
	basenames = []
	for dir in dirs:
		check.isDir(dir)
		basenames.append(os.path.basename(dir))
	check.noDuplicates(basenames)

	check.nonexistent(tarballName)
	check.endsIn(tarballName, ".tar.gz")

	logging.info("Compressing %s into %s", dirs, tarballName)
	with tarfile.open(tarballName, "w:gz") as tar:
		for dir in dirs:
			tar.add(dir, arcname=os.path.basename(dir))

	check.fileSizeNonZero(tarballName)
	if not tarfile.is_tarfile(tarballName):
		logging.error("Compression failed.  Output file is not tarFile: %s", tarballName)
		raise RuntimeError()
	logging.info("Compressed %s into %s", dirs, tarballName)

def decompress(tarball, destinationPath):
	logging.info("Parameters: tarball=[%s] destinationPath=[%s]", str(tarball), str(destinationPath))
	check.isFile(tarball)
	check.nonexistent(destinationPath)

	if not tarfile.is_tarfile(tarball):
		logging.error("tarball must be a tar file: %s", tarball)
		raise RuntimeError()

	logging.info("Decompressing %s into %s", tarball, destinationPath)
	with tarfile.open(tarball, "r:gz") as tar:
		tar.extractall(destinationPath)
	logging.info("Decompressed %s into %s", tarball, destinationPath)
