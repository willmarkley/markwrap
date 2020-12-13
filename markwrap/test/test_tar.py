import markwrap.tar as tar
import markwrap.test.constants as tstconst
import logging
import pytest
import os
import shutil
import subprocess
import tarfile

def diffdirs(dir1, dir2):
	completed_process = subprocess.run(["diff","-r",dir1,dir2], subprocess.PIPE, stderr=subprocess.STDOUT)
	if (completed_process.returncode != 0):
		return True
	else:
		return False


def test_compress(caplog, tmp_path):
	caplog.set_level(logging.DEBUG)
	TMP_DIR = tmp_path / "tst.resources"
	shutil.copytree(tstconst.TEST_RESOURCES_DIR, TMP_DIR)

	HAPPY_PATH_DIRS = [TMP_DIR / tstconst.EXISTING_DIR_A, TMP_DIR / tstconst.EXISTING_DIR_B, TMP_DIR / tstconst.EXISTING_DIR_C]
	HAPPY_PATH_TARBALLNAME = TMP_DIR / tstconst.NONEXISTENT_ARCHIVE

	ERROR_NON_PATHLIKEOBJECT = tstconst.NON_PATH_LIKE_OBJECT
	ERROR_EMTPY_STRING = tstconst.EMPTY_STRING
	ERROR_RELATIVE_PATH_ARCHIVE = tstconst.NONEXISTENT_ARCHIVE
	ERROR_EXISTING_FILE = TMP_DIR / tstconst.EXISTING_FILE
	ERROR_BAD_FILENAME_ENDING = TMP_DIR / tstconst.NONEXISTENT_FILE

	ERROR_RELATIVE_PATH_DIR = tstconst.EXISTING_DIR
	ERROR_NONEXISTENT_DIR = TMP_DIR / tstconst.NONEXISTENT_DIR

	ORIGINAL_DIR = TMP_DIR / tstconst.EXISTING_DIR
	TARGET_DIR = TMP_DIR / "extracted"

## INVALID INPUT
	with pytest.raises(RuntimeError):
		tar.compress(HAPPY_PATH_DIRS, ERROR_NON_PATHLIKEOBJECT)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.compress - Parameters: dirs=[" + str(HAPPY_PATH_DIRS) + "] tarballName=[" + str(ERROR_NON_PATHLIKEOBJECT) + "]"
	assert lines[1] == "[ERROR] check.pathlikeObject - path must be path-like object: " + str(ERROR_NON_PATHLIKEOBJECT)
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.compress(HAPPY_PATH_DIRS, ERROR_EMTPY_STRING)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.compress - Parameters: dirs=[" + str(HAPPY_PATH_DIRS) + "] tarballName=[" + str(ERROR_EMTPY_STRING) + "]"
	assert lines[1] == "[ERROR] check.nonEmptyString - string cannot be empty: "
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.compress(HAPPY_PATH_DIRS, ERROR_RELATIVE_PATH_ARCHIVE)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.compress - Parameters: dirs=[" + str(HAPPY_PATH_DIRS) + "] tarballName=[" + str(ERROR_RELATIVE_PATH_ARCHIVE) + "]"
	assert lines[1] == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_PATH_ARCHIVE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.compress(HAPPY_PATH_DIRS, ERROR_EXISTING_FILE)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.compress - Parameters: dirs=[" + str(HAPPY_PATH_DIRS) + "] tarballName=[" + str(ERROR_EXISTING_FILE) + "]"
	assert lines[1] == "[ERROR] check.nonexistent - file or directory already exists: " + str(ERROR_EXISTING_FILE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.compress(HAPPY_PATH_DIRS, ERROR_BAD_FILENAME_ENDING)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.compress - Parameters: dirs=[" + str(HAPPY_PATH_DIRS) + "] tarballName=[" + str(ERROR_BAD_FILENAME_ENDING) + "]"
	assert lines[1] == "[ERROR] check.endsIn - file must end in .tar.gz: " + str(ERROR_BAD_FILENAME_ENDING)
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.compress([ERROR_RELATIVE_PATH_DIR], HAPPY_PATH_TARBALLNAME)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.compress - Parameters: dirs=[" + str([ERROR_RELATIVE_PATH_DIR]) + "] tarballName=[" + str(HAPPY_PATH_TARBALLNAME) + "]"
	assert lines[1] == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_PATH_DIR)
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.compress([ERROR_NONEXISTENT_DIR], HAPPY_PATH_TARBALLNAME)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.compress - Parameters: dirs=[" + str([ERROR_NONEXISTENT_DIR]) + "] tarballName=[" + str(HAPPY_PATH_TARBALLNAME) + "]"
	assert lines[1] == "[ERROR] check.exists - file or directory does not exist: " + str(ERROR_NONEXISTENT_DIR)
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.compress([ERROR_EXISTING_FILE], HAPPY_PATH_TARBALLNAME)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.compress - Parameters: dirs=[" + str([ERROR_EXISTING_FILE]) + "] tarballName=[" + str(HAPPY_PATH_TARBALLNAME) + "]"
	assert lines[1] == "[ERROR] check.isDir - d is not a directory: " + str(ERROR_EXISTING_FILE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.compress([HAPPY_PATH_DIRS[0], HAPPY_PATH_DIRS[0]], HAPPY_PATH_TARBALLNAME)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.compress - Parameters: dirs=[" + str([HAPPY_PATH_DIRS[0], HAPPY_PATH_DIRS[0]]) + "] tarballName=[" + str(HAPPY_PATH_TARBALLNAME) + "]"
	assert lines[1] == "[ERROR] check.noDuplicates - duplicates found in list: " + str([os.path.basename(HAPPY_PATH_DIRS[0]), os.path.basename(HAPPY_PATH_DIRS[0])])
	caplog.clear()

## HAPPY PATH
	tar.compress(HAPPY_PATH_DIRS, HAPPY_PATH_TARBALLNAME)

	with tarfile.open(HAPPY_PATH_TARBALLNAME, "r:gz") as tarball:
		tarball.extractall(TARGET_DIR)

	if diffdirs(ORIGINAL_DIR, TARGET_DIR):
		assert False

	lines = caplog.text.splitlines()
	assert len(lines) == 3
	assert lines[0] == "[INFO] tar.compress - Parameters: dirs=[" + str(HAPPY_PATH_DIRS) + "] tarballName=[" + str(HAPPY_PATH_TARBALLNAME) + "]"
	assert lines[1] == "[INFO] tar.compress - Compressing " + str(HAPPY_PATH_DIRS) + " into " + str(HAPPY_PATH_TARBALLNAME)
	assert lines[2] == "[INFO] tar.compress - Compressed " + str(HAPPY_PATH_DIRS) + " into " + str(HAPPY_PATH_TARBALLNAME)
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
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.decompress - Parameters: tarball=[" + str(ERROR_RELATIVE_PATH_ARCHIVE) + "] destinationPath=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_PATH_ARCHIVE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.decompress(ERROR_NONEXISTENT_FILE, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.decompress - Parameters: tarball=[" + str(ERROR_NONEXISTENT_FILE) + "] destinationPath=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.exists - file or directory does not exist: " + str(ERROR_NONEXISTENT_FILE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.decompress(ERROR_EXISTING_DIR, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.decompress - Parameters: tarball=[" + str(ERROR_EXISTING_DIR) + "] destinationPath=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.isFile - f is not a file: " + str(ERROR_EXISTING_DIR)
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.decompress(ERROR_NONTARBALL, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.decompress - Parameters: tarball=[" + str(ERROR_NONTARBALL) + "] destinationPath=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] tar.decompress - tarball must be a tar file: " + str(ERROR_NONTARBALL)
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.decompress(HAPPY_PATH_TARBALL, ERROR_RELATIVE_PATH_DIR)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.decompress - Parameters: tarball=[" + str(HAPPY_PATH_TARBALL) + "] destinationPath=[" + str(ERROR_RELATIVE_PATH_DIR) + "]"
	assert lines[1] == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_PATH_DIR)
	caplog.clear()

	with pytest.raises(RuntimeError):
		tar.decompress(HAPPY_PATH_TARBALL, ERROR_EXISTING_DIR)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] tar.decompress - Parameters: tarball=[" + str(HAPPY_PATH_TARBALL) + "] destinationPath=[" + str(ERROR_EXISTING_DIR) + "]"
	assert lines[1] == "[ERROR] check.nonexistent - file or directory already exists: " + str(ERROR_EXISTING_DIR)
	caplog.clear()

## HAPPY PATH
	tar.decompress(HAPPY_PATH_TARBALL, HAPPY_PATH_DESTPATH)

	if diffdirs(ORIGINAL_DIR, HAPPY_PATH_DESTPATH):
		assert False

	lines = caplog.text.splitlines()
	assert len(lines) == 3
	assert lines[0] == "[INFO] tar.decompress - Parameters: tarball=[" + str(HAPPY_PATH_TARBALL) + "] destinationPath=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[INFO] tar.decompress - Decompressing " + str(HAPPY_PATH_TARBALL) + " into " + str(HAPPY_PATH_DESTPATH)
	assert lines[2] == "[INFO] tar.decompress - Decompressed " + str(HAPPY_PATH_TARBALL) + " into " + str(HAPPY_PATH_DESTPATH)
	caplog.clear()
