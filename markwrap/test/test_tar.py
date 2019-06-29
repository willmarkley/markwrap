import markwrap.tar as tar
import logging
import pytest
import os
import shutil
import subprocess
import tarfile

TEST_FILE = os.path.abspath(__file__)
TEST_DIR = os.path.dirname(TEST_FILE)
TEST_RESOURCES = TEST_DIR + "/tst.resources"

def diffdirs(dir1, dir2):
	result = subprocess.call(["diff","-r",dir1,dir2], subprocess.PIPE, stderr=subprocess.STDOUT)
	if (result != 0):
		return True
	else:
		return False

def test_compress(caplog, tmp_path):
	caplog.set_level(logging.DEBUG)

	TMP_DIR = tmp_path / "tst.resources"
	shutil.copytree(TEST_RESOURCES, TMP_DIR)

	# Assert exception for relative path #
	with pytest.raises(RuntimeError):
		tar.compress("relativePath", [TMP_DIR / "dirs" / "a"])
	assert caplog.text == "[ERROR] tar.compress - tarballName must be an absolute path: relativePath\n"
	caplog.clear()

	# Assert exception for tarballName already existing #
	with pytest.raises(RuntimeError):
		tar.compress(TMP_DIR / "dirs" / "a" / "a1.txt", [TMP_DIR / "dirs" / "a"])
	assert caplog.text == "[ERROR] tar.compress - tarballName already exists: " + str(TMP_DIR / "dirs" / "a" / "a1.txt") + "\n"
	caplog.clear()

	# Assert exception for tarballName not ending in .tar.gz existing #
	with pytest.raises(RuntimeError):
		tar.compress(TMP_DIR / "improperTarballNameEnding.txt", [TMP_DIR / "dirs" / "a"])
	assert caplog.text == "[ERROR] tar.compress - tarballName must end in .tar.gz: " + str(TMP_DIR / "improperTarballNameEnding.txt") + "\n"
	caplog.clear()

	# Assert exception for dirs not existing #
	with pytest.raises(RuntimeError):
		tar.compress(TMP_DIR / "test.tar.gz", [TMP_DIR / "dirs" / "d"])
	assert caplog.text == "[ERROR] tar.compress - Cannot compress non-existant directory: " + str(TMP_DIR / "dirs" / "d") + "\n"
	caplog.clear()

	# Assert exception for dirs being a file #
	with pytest.raises(RuntimeError):
		tar.compress(TMP_DIR / "test.tar.gz", [TMP_DIR / "dirs" / "a" / "a1.txt"])
	assert caplog.text == "[ERROR] tar.compress - Cannot compress non-directory: " + str(TMP_DIR / "dirs" / "a" / "a1.txt") + "\n"
	caplog.clear()

	# Assert happy path has no exception #
	tar.compress(TMP_DIR / "test.tar.gz", [TMP_DIR / "dirs" / "a", TMP_DIR / "dirs" / "b", TMP_DIR / "dirs" / "c"])

	with tarfile.open(TMP_DIR / "test.tar.gz", "r:gz") as tarball:
		tarball.extractall(TMP_DIR / "extracted")

	if diffdirs(TMP_DIR / "dirs", TMP_DIR / "extracted"):
		assert False

	dirsStr = str([TMP_DIR / "dirs" / "a", TMP_DIR / "dirs" / "b", TMP_DIR / "dirs" / "c"])

	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.compress - Compressing " + dirsStr + " into " + str(TMP_DIR / "test.tar.gz")
	assert lines[1] == "[INFO] tar.compress - Compressed " + dirsStr + " into " + str(TMP_DIR / "test.tar.gz")
	caplog.clear()

def test_decompress(caplog, tmp_path):
	caplog.set_level(logging.DEBUG)

	TMP_DIR = tmp_path / "tst.resources"
	shutil.copytree(TEST_RESOURCES, TMP_DIR)

	# Assert exception for tarballName not existing #
	with pytest.raises(RuntimeError):
		tar.decompress(TMP_DIR / "doesnotExist.tar.gz", TMP_DIR / "new")
	assert caplog.text == "[ERROR] tar.decompress - tarballName does not exist: " + str(TMP_DIR / "doesnotExist.tar.gz") + "\n"
	caplog.clear()

	# Assert exception for tarballName not being a tar file #
	with pytest.raises(RuntimeError):
		tar.decompress(TMP_DIR / "dirs" / "a" / "a1.txt", TMP_DIR / "new")
	assert caplog.text == "[ERROR] tar.decompress - tarballName must be a tar file: " + str(TMP_DIR / "dirs" / "a" / "a1.txt") + "\n"
	caplog.clear()

	# Assert exception for dir existing #
	with pytest.raises(RuntimeError):
		tar.decompress(TMP_DIR / "archive.tar.gz", TMP_DIR / "dirs")
	assert caplog.text == "[ERROR] tar.decompress - destinationPath already exists: " + str(TMP_DIR / "dirs") + "\n"
	caplog.clear()

	# Assert exception for dir being a relative path #
	with pytest.raises(RuntimeError):
		tar.decompress(TMP_DIR / "archive.tar.gz", "new")
	assert caplog.text == "[ERROR] tar.decompress - destinationPath must be an absolute path: new\n"
	caplog.clear()

	# Assert happy path has no exception #
	tar.decompress(TMP_DIR / "archive.tar.gz", TMP_DIR / "new")

	if diffdirs(TMP_DIR / "dirs", TMP_DIR / "new"):
		assert False

	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.decompress - Decompressing " + str(TMP_DIR / "archive.tar.gz") + " into " + str(TMP_DIR / "new")
	assert lines[1] == "[INFO] tar.decompress - Decompressed " + str(TMP_DIR / "archive.tar.gz") + " into " + str(TMP_DIR / "new")
	caplog.clear()
