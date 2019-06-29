import markwrap.tar as tar
import markwrap.test.constants as tstconst
import logging
import pytest
import os
import shutil
import subprocess
import tarfile

def diffdirs(dir1, dir2):
	result = subprocess.call(["diff","-r",dir1,dir2], subprocess.PIPE, stderr=subprocess.STDOUT)
	if (result != 0):
		return True
	else:
		return False


def test_compress(caplog, tmp_path):
	caplog.set_level(logging.DEBUG)
	TMP_DIR = tmp_path / "tst.resources"
	shutil.copytree(tstconst.TEST_RESOURCES_DIR, TMP_DIR)

	HAPPY_PATH_DIRS = [TMP_DIR / tstconst.EXISTING_DIR_A, TMP_DIR / tstconst.EXISTING_DIR_B, TMP_DIR / tstconst.EXISTING_DIR_C]
	HAPPY_PATH_TARBALLNAME = TMP_DIR / tstconst.NONEXISTENT_ARCHIVE

	ERROR_RELATIVE_PATH_ARCHIVE = tstconst.NONEXISTENT_ARCHIVE
	ERROR_EXISTING_FILE = TMP_DIR / tstconst.EXISTING_FILE
	ERROR_BAD_FILENAME_ENDING = TMP_DIR / tstconst.NONEXISTENT_FILE

	ERROR_RELATIVE_PATH_DIR = tstconst.EXISTING_DIR
	ERROR_NONEXISTENT_DIR = TMP_DIR / tstconst.NONEXISTENT_DIR

	ORIGINAL_DIR = TMP_DIR / tstconst.EXISTING_DIR
	TARGET_DIR = TMP_DIR / "extracted"

## INVALID INPUT
	with pytest.raises(RuntimeError):
		tar.compress(ERROR_RELATIVE_PATH_ARCHIVE, HAPPY_PATH_DIRS)
	assert caplog.text == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_PATH_ARCHIVE) + "\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.compress(ERROR_EXISTING_FILE, HAPPY_PATH_DIRS)
	assert caplog.text == "[ERROR] check.nonexistent - file or directory already exists: " + str(ERROR_EXISTING_FILE) + "\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.compress(ERROR_BAD_FILENAME_ENDING, HAPPY_PATH_DIRS)
	assert caplog.text == "[ERROR] tar.compress - tarballName must end in .tar.gz: " + str(ERROR_BAD_FILENAME_ENDING) + "\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.compress(HAPPY_PATH_TARBALLNAME, [ERROR_RELATIVE_PATH_DIR])
	assert caplog.text == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_PATH_DIR) + "\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.compress(HAPPY_PATH_TARBALLNAME, [ERROR_NONEXISTENT_DIR])
	assert caplog.text == "[ERROR] check.exists - file or directory does not exist: " + str(ERROR_NONEXISTENT_DIR) + "\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.compress(HAPPY_PATH_TARBALLNAME, [ERROR_EXISTING_FILE])
	assert caplog.text == "[ERROR] check.isDir - d is not a directory: " + str(ERROR_EXISTING_FILE) + "\n"
	caplog.clear()

## HAPPY PATH
	tar.compress(HAPPY_PATH_TARBALLNAME, HAPPY_PATH_DIRS)

	with tarfile.open(HAPPY_PATH_TARBALLNAME, "r:gz") as tarball:
		tarball.extractall(TARGET_DIR)

	if diffdirs(ORIGINAL_DIR, TARGET_DIR):
		assert False

	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.compress - Compressing " + str(HAPPY_PATH_DIRS) + " into " + str(HAPPY_PATH_TARBALLNAME)
	assert lines[1] == "[INFO] tar.compress - Compressed " + str(HAPPY_PATH_DIRS) + " into " + str(HAPPY_PATH_TARBALLNAME)
	caplog.clear()


def test_decompress(caplog, tmp_path):
	caplog.set_level(logging.DEBUG)
	TMP_DIR = tmp_path / "tst.resources"
	shutil.copytree(tstconst.TEST_RESOURCES_DIR, TMP_DIR)

	HAPPY_PATH_TARBALL = TMP_DIR / tstconst.EXISTING_ARCHIVE
	HAPPY_PATH_DESTPATH = TMP_DIR / tstconst.NONEXISTENT_DIR

	ERROR_RELATIVE_PATH_ARCHIVE = tstconst.EXISTING_ARCHIVE
	ERROR_NONEXISTENT_FILE = TMP_DIR / tstconst.NONEXISTENT_FILE
	ERROR_NONTARBALL = TMP_DIR / tstconst.EXISTING_FILE

	ERROR_EXISTING_DIR = TMP_DIR / tstconst.EXISTING_DIR
	ERROR_RELATIVE_PATH_DIR = tstconst.NONEXISTENT_DIR

	ORIGINAL_DIR = TMP_DIR / tstconst.EXISTING_DIR

## INVALID INPUT
	with pytest.raises(RuntimeError):
		tar.decompress(ERROR_RELATIVE_PATH_ARCHIVE, HAPPY_PATH_DESTPATH)
	assert caplog.text == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_PATH_ARCHIVE) + "\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.decompress(ERROR_NONEXISTENT_FILE, HAPPY_PATH_DESTPATH)
	assert caplog.text == "[ERROR] check.exists - file or directory does not exist: " + str(ERROR_NONEXISTENT_FILE) + "\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.decompress(ERROR_EXISTING_DIR, HAPPY_PATH_DESTPATH)
	assert caplog.text == "[ERROR] check.isFile - f is not a file: " + str(ERROR_EXISTING_DIR) + "\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.decompress(ERROR_NONTARBALL, HAPPY_PATH_DESTPATH)
	assert caplog.text == "[ERROR] tar.decompress - tarballName must be a tar file: " + str(ERROR_NONTARBALL) + "\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.decompress(HAPPY_PATH_TARBALL, ERROR_RELATIVE_PATH_DIR)
	assert caplog.text == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_PATH_DIR) + "\n"
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.decompress(HAPPY_PATH_TARBALL, ERROR_EXISTING_DIR)
	assert caplog.text == "[ERROR] check.nonexistent - file or directory already exists: " + str(ERROR_EXISTING_DIR) + "\n"
	caplog.clear()

## HAPPY PATH
	tar.decompress(HAPPY_PATH_TARBALL, HAPPY_PATH_DESTPATH)

	if diffdirs(ORIGINAL_DIR, HAPPY_PATH_DESTPATH):
		assert False

	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.decompress - Decompressing " + str(HAPPY_PATH_TARBALL) + " into " + str(HAPPY_PATH_DESTPATH)
	assert lines[1] == "[INFO] tar.decompress - Decompressed " + str(HAPPY_PATH_TARBALL) + " into " + str(HAPPY_PATH_DESTPATH)
	caplog.clear()
