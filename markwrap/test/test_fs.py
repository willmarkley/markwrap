import markwrap.fs as fs
import markwrap.test.constants as tstconst
import logging
import pytest
import shutil
import os
import filecmp


def test_mv(caplog, tmp_path):
	caplog.set_level(logging.DEBUG)
	TMP_DIR = tmp_path / "tst.resources"
	shutil.copytree(tstconst.TEST_RESOURCES_DIR, TMP_DIR)

	HAPPY_PATH_SRC_FILE = TMP_DIR / tstconst.EXISTING_FILE
	HAPPY_PATH_DESTPATH = TMP_DIR / tstconst.EXISTING_DIR_A

	ERROR_NON_PATHLIKEOBJECT = tstconst.NON_PATH_LIKE_OBJECT
	ERROR_EMTPY_STRING = tstconst.EMPTY_STRING
	ERROR_RELATIVE_FILEPATH = tstconst.EXISTING_FILE
	ERROR_NONEXISTENT_FILE = TMP_DIR / tstconst.NONEXISTENT_FILE
	ERROR_NON_FILE = TMP_DIR / tstconst.EXISTING_DIR
	ERROR_EMPTY_FILE = TMP_DIR / tstconst.EMPTY_FILE
	ERROR_FILE_EXISTS_IN_DESTPATH = TMP_DIR / tstconst.EXISTING_FILE_2

	ERROR_RELATIVE_PATH_DIR = tstconst.EXISTING_DIR
	ERROR_NONEXISTENT_DIR = TMP_DIR / tstconst.NONEXISTENT_DIR
	ERROR_NON_DIR = TMP_DIR / tstconst.EXISTING_FILE

	HAPPY_PATH_IDENTICAL_CONTENT = TMP_DIR / tstconst.EXISTING_FILE_2
	TARGET_FILE = HAPPY_PATH_DESTPATH / tstconst.EXISTING_FILE

## INVALID INPUT
	with pytest.raises(RuntimeError):
		fs.mv(ERROR_NON_PATHLIKEOBJECT, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.mv - Parameters: source=[" + str(ERROR_NON_PATHLIKEOBJECT) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.pathlikeObject - path must be path-like object: " + str(ERROR_NON_PATHLIKEOBJECT)
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.mv(ERROR_EMTPY_STRING, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.mv - Parameters: source=[" + str(ERROR_EMTPY_STRING) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.nonEmptyString - string cannot be empty: "
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.mv(ERROR_RELATIVE_FILEPATH, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.mv - Parameters: source=[" + str(ERROR_RELATIVE_FILEPATH) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_FILEPATH)
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.mv(ERROR_NONEXISTENT_FILE, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.mv - Parameters: source=[" + str(ERROR_NONEXISTENT_FILE) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.exists - file or directory does not exist: " + str(ERROR_NONEXISTENT_FILE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.mv(ERROR_NON_FILE, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.mv - Parameters: source=[" + str(ERROR_NON_FILE) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.isFile - f is not a file: " + str(ERROR_NON_FILE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.mv(ERROR_EMPTY_FILE, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.mv - Parameters: source=[" + str(ERROR_EMPTY_FILE) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.fileSizeNonZero - file size is not greater than zero: " + str(ERROR_EMPTY_FILE) + " (0 bytes)"
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.mv(ERROR_FILE_EXISTS_IN_DESTPATH, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.mv - Parameters: source=[" + str(ERROR_FILE_EXISTS_IN_DESTPATH) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.nonexistent - file or directory already exists: " + str(HAPPY_PATH_DESTPATH / os.path.basename(ERROR_FILE_EXISTS_IN_DESTPATH))
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.mv(HAPPY_PATH_SRC_FILE, ERROR_RELATIVE_PATH_DIR)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.mv - Parameters: source=[" + str(HAPPY_PATH_SRC_FILE) + "] destination=[" + str(ERROR_RELATIVE_PATH_DIR) + "]"
	assert lines[1] == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_PATH_DIR)
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.mv(HAPPY_PATH_SRC_FILE, ERROR_NONEXISTENT_DIR)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.mv - Parameters: source=[" + str(HAPPY_PATH_SRC_FILE) + "] destination=[" + str(ERROR_NONEXISTENT_DIR) + "]"
	assert lines[1] == "[ERROR] check.exists - file or directory does not exist: " + str(ERROR_NONEXISTENT_DIR)
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.mv(HAPPY_PATH_SRC_FILE, ERROR_NON_DIR)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.mv - Parameters: source=[" + str(HAPPY_PATH_SRC_FILE) + "] destination=[" + str(ERROR_NON_DIR) + "]"
	assert lines[1] == "[ERROR] check.isDir - d is not a directory: " + str(ERROR_NON_DIR)
	caplog.clear()

## HAPPY PATH
	fs.mv(HAPPY_PATH_SRC_FILE, HAPPY_PATH_DESTPATH)

	assert not os.path.exists(HAPPY_PATH_SRC_FILE)

	assert os.path.exists(TARGET_FILE)
	assert os.path.isfile(TARGET_FILE)
	assert os.path.getsize(TARGET_FILE) > 0
	filecmp.cmp(TARGET_FILE, HAPPY_PATH_IDENTICAL_CONTENT, shallow=False)

	lines = caplog.text.splitlines()
	assert len(lines) == 3
	assert lines[0] == "[INFO] fs.mv - Parameters: source=[" + str(HAPPY_PATH_SRC_FILE) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[INFO] fs.mv - Moving " + str(HAPPY_PATH_SRC_FILE) + " to directory " + str(HAPPY_PATH_DESTPATH)
	assert lines[2] == "[INFO] fs.mv - Moved " + str(HAPPY_PATH_SRC_FILE) + " to file " + str(TARGET_FILE)
	caplog.clear()

def test_cp(caplog, tmp_path):
	caplog.set_level(logging.DEBUG)
	TMP_DIR = tmp_path / "tst.resources"
	shutil.copytree(tstconst.TEST_RESOURCES_DIR, TMP_DIR)

	HAPPY_PATH_SRC_FILE = TMP_DIR / tstconst.EXISTING_FILE
	HAPPY_PATH_DESTPATH = TMP_DIR / tstconst.EXISTING_DIR_A

	ERROR_NON_PATHLIKEOBJECT = tstconst.NON_PATH_LIKE_OBJECT
	ERROR_EMTPY_STRING = tstconst.EMPTY_STRING
	ERROR_RELATIVE_FILEPATH = tstconst.EXISTING_FILE
	ERROR_NONEXISTENT_FILE = TMP_DIR / tstconst.NONEXISTENT_FILE
	ERROR_NON_FILE = TMP_DIR / tstconst.EXISTING_DIR
	ERROR_EMPTY_FILE = TMP_DIR / tstconst.EMPTY_FILE
	ERROR_FILE_EXISTS_IN_DESTPATH = TMP_DIR / tstconst.EXISTING_FILE_2

	ERROR_RELATIVE_PATH_DIR = tstconst.EXISTING_DIR
	ERROR_NONEXISTENT_DIR = TMP_DIR / tstconst.NONEXISTENT_DIR
	ERROR_NON_DIR = TMP_DIR / tstconst.EXISTING_FILE

	TARGET_FILE = HAPPY_PATH_DESTPATH / tstconst.EXISTING_FILE

## INVALID INPUT
	with pytest.raises(RuntimeError):
		fs.cp(ERROR_NON_PATHLIKEOBJECT, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.cp - Parameters: source=[" + str(ERROR_NON_PATHLIKEOBJECT) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.pathlikeObject - path must be path-like object: " + str(ERROR_NON_PATHLIKEOBJECT)
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.cp(ERROR_EMTPY_STRING, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.cp - Parameters: source=[" + str(ERROR_EMTPY_STRING) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.nonEmptyString - string cannot be empty: "
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.cp(ERROR_RELATIVE_FILEPATH, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.cp - Parameters: source=[" + str(ERROR_RELATIVE_FILEPATH) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_FILEPATH)
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.cp(ERROR_NONEXISTENT_FILE, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.cp - Parameters: source=[" + str(ERROR_NONEXISTENT_FILE) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.exists - file or directory does not exist: " + str(ERROR_NONEXISTENT_FILE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.cp(ERROR_NON_FILE, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.cp - Parameters: source=[" + str(ERROR_NON_FILE) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.isFile - f is not a file: " + str(ERROR_NON_FILE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.cp(ERROR_EMPTY_FILE, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.cp - Parameters: source=[" + str(ERROR_EMPTY_FILE) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.fileSizeNonZero - file size is not greater than zero: " + str(ERROR_EMPTY_FILE) + " (0 bytes)"
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.cp(ERROR_FILE_EXISTS_IN_DESTPATH, HAPPY_PATH_DESTPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.cp - Parameters: source=[" + str(ERROR_FILE_EXISTS_IN_DESTPATH) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[ERROR] check.nonexistent - file or directory already exists: " + str(HAPPY_PATH_DESTPATH / os.path.basename(ERROR_FILE_EXISTS_IN_DESTPATH))
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.cp(HAPPY_PATH_SRC_FILE, ERROR_RELATIVE_PATH_DIR)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.cp - Parameters: source=[" + str(HAPPY_PATH_SRC_FILE) + "] destination=[" + str(ERROR_RELATIVE_PATH_DIR) + "]"
	assert lines[1] == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_PATH_DIR)
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.cp(HAPPY_PATH_SRC_FILE, ERROR_NONEXISTENT_DIR)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.cp - Parameters: source=[" + str(HAPPY_PATH_SRC_FILE) + "] destination=[" + str(ERROR_NONEXISTENT_DIR) + "]"
	assert lines[1] == "[ERROR] check.exists - file or directory does not exist: " + str(ERROR_NONEXISTENT_DIR)
	caplog.clear()

	with pytest.raises(RuntimeError):
		fs.cp(HAPPY_PATH_SRC_FILE, ERROR_NON_DIR)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] fs.cp - Parameters: source=[" + str(HAPPY_PATH_SRC_FILE) + "] destination=[" + str(ERROR_NON_DIR) + "]"
	assert lines[1] == "[ERROR] check.isDir - d is not a directory: " + str(ERROR_NON_DIR)
	caplog.clear()

## HAPPY PATH
	output = fs.cp(HAPPY_PATH_SRC_FILE, HAPPY_PATH_DESTPATH)

	assert os.path.exists(HAPPY_PATH_SRC_FILE)
	assert os.path.isfile(HAPPY_PATH_SRC_FILE)
	assert os.path.getsize(HAPPY_PATH_SRC_FILE) > 0

	assert output == str(TARGET_FILE)
	assert os.path.exists(TARGET_FILE)
	assert os.path.isfile(TARGET_FILE)
	assert os.path.getsize(TARGET_FILE) > 0
	filecmp.cmp(TARGET_FILE, HAPPY_PATH_SRC_FILE, shallow=False)

	lines = caplog.text.splitlines()
	assert len(lines) == 3
	assert lines[0] == "[INFO] fs.cp - Parameters: source=[" + str(HAPPY_PATH_SRC_FILE) + "] destination=[" + str(HAPPY_PATH_DESTPATH) + "]"
	assert lines[1] == "[INFO] fs.cp - Copying " + str(HAPPY_PATH_SRC_FILE) + " to directory " + str(HAPPY_PATH_DESTPATH)
	assert lines[2] == "[INFO] fs.cp - Copied " + str(HAPPY_PATH_SRC_FILE) + " to file " + str(TARGET_FILE)
	caplog.clear()
