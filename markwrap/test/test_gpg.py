import markwrap.gpg as gpg
import markwrap.test.constants as tstconst
import logging
import os
import pytest
import shutil
import gnupg
import filecmp

def test_encrypt(caplog, tmp_path):
	caplog.set_level(logging.DEBUG)
	TMP_DIR = tmp_path / "tst.resources"
	shutil.copytree(tstconst.TEST_RESOURCES_DIR, TMP_DIR)

	HAPPY_PATH_FILEPATH = TMP_DIR / tstconst.EXISTING_FILE
	HAPPY_PATH_RECIPIENT = tstconst.KEY_ID
	HAPPY_PATH_RECIPIENT_FINGERPRINT = tstconst.KEY_FINGERPRINT
	HAPPY_PATH_OUTPUT = str(HAPPY_PATH_FILEPATH) + "." + str(HAPPY_PATH_RECIPIENT)[-8:] + ".gpg"
	HAPPY_PATH_IDENTICAL_CONTENT = TMP_DIR / tstconst.ENCRYPTED_FILE

	ERROR_NON_PATHLIKEOBJECT = tstconst.NON_PATH_LIKE_OBJECT
	ERROR_EMTPY_STRING = tstconst.EMPTY_STRING
	ERROR_RELATIVE_FILEPATH = tstconst.EXISTING_FILE
	ERROR_NONEXISTENT_FILE = TMP_DIR / tstconst.NONEXISTENT_FILE
	ERROR_NON_FILE = TMP_DIR / tstconst.EXISTING_DIR
	ERROR_EMPTY_FILE = TMP_DIR / tstconst.EMPTY_FILE

	ERROR_INVALID_KEY_ID = tstconst.INVALID_KEY_ID
	ERROR_INVALID_KEY_FINGERPRINT = tstconst.INVALID_KEY_FINGERPRINT
	ERROR_NONEXISTENT_KEY_ID = tstconst.NONEXISTENT_KEY_ID

	gpg_setup = gnupg.GPG()
	gpg_setup.encoding = 'utf-8'
	gpg_setup.list_keys()
	with open(TMP_DIR / tstconst.KEY_FILE, "rt") as keyfile:
		gpg_setup.import_keys(keyfile.read())
	gpg_setup.trust_keys(tstconst.KEY_FINGERPRINT, 'TRUST_ULTIMATE')

## INVALID INPUT
	with pytest.raises(RuntimeError):
		gpg.encrypt(ERROR_NON_PATHLIKEOBJECT, HAPPY_PATH_RECIPIENT)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.encrypt - Parameters: filepath=[" + str(ERROR_NON_PATHLIKEOBJECT) + "] recipient=[" + str(HAPPY_PATH_RECIPIENT) + "]"
	assert lines[1] == "[ERROR] check.pathlikeObject - path must be path-like object: " + str(ERROR_NON_PATHLIKEOBJECT)
	caplog.clear()

	with pytest.raises(RuntimeError):
		gpg.encrypt(ERROR_EMTPY_STRING, HAPPY_PATH_RECIPIENT)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.encrypt - Parameters: filepath=[" + str(ERROR_EMTPY_STRING) + "] recipient=[" + str(HAPPY_PATH_RECIPIENT) + "]"
	assert lines[1] == "[ERROR] check.nonEmptyString - string cannot be empty: "
	caplog.clear()

	with pytest.raises(RuntimeError):
		gpg.encrypt(ERROR_RELATIVE_FILEPATH, HAPPY_PATH_RECIPIENT)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.encrypt - Parameters: filepath=[" + str(ERROR_RELATIVE_FILEPATH) + "] recipient=[" + str(HAPPY_PATH_RECIPIENT) + "]"
	assert lines[1] == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_FILEPATH)
	caplog.clear()

	with pytest.raises(RuntimeError):
		gpg.encrypt(ERROR_NONEXISTENT_FILE, HAPPY_PATH_RECIPIENT)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.encrypt - Parameters: filepath=[" + str(ERROR_NONEXISTENT_FILE) + "] recipient=[" + str(HAPPY_PATH_RECIPIENT) + "]"
	assert lines[1] == "[ERROR] check.exists - file or directory does not exist: " + str(ERROR_NONEXISTENT_FILE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		gpg.encrypt(ERROR_NON_FILE, HAPPY_PATH_RECIPIENT)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.encrypt - Parameters: filepath=[" + str(ERROR_NON_FILE) + "] recipient=[" + str(HAPPY_PATH_RECIPIENT) + "]"
	assert lines[1] == "[ERROR] check.isFile - f is not a file: " + str(ERROR_NON_FILE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		gpg.encrypt(ERROR_EMPTY_FILE, HAPPY_PATH_RECIPIENT)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.encrypt - Parameters: filepath=[" + str(ERROR_EMPTY_FILE) + "] recipient=[" + str(HAPPY_PATH_RECIPIENT) + "]"
	assert lines[1] == "[ERROR] check.fileSizeNonZero - file size is not greater than zero: " + str(ERROR_EMPTY_FILE) + " (0 bytes)"
	caplog.clear()

	with pytest.raises(RuntimeError):
		gpg.encrypt(HAPPY_PATH_FILEPATH, None)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.encrypt - Parameters: filepath=[" + str(HAPPY_PATH_FILEPATH) + "] recipient=[" + str(None) + "]"
	assert lines[1] == "[ERROR] check.nonNone - can NOT be None: None"
	caplog.clear()

	with pytest.raises(RuntimeError):
		gpg.encrypt(HAPPY_PATH_FILEPATH, ERROR_INVALID_KEY_ID)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.encrypt - Parameters: filepath=[" + str(HAPPY_PATH_FILEPATH) + "] recipient=[" + str(ERROR_INVALID_KEY_ID) + "]"
	assert lines[1] == "[ERROR] check.hexadecimal - string must be hexadecimal characters: " + str(ERROR_INVALID_KEY_ID)
	caplog.clear()

	with pytest.raises(RuntimeError):
		gpg.encrypt(HAPPY_PATH_FILEPATH, ERROR_INVALID_KEY_FINGERPRINT)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.encrypt - Parameters: filepath=[" + str(HAPPY_PATH_FILEPATH) + "] recipient=[" + str(ERROR_INVALID_KEY_FINGERPRINT) + "]"
	assert lines[1] == "[ERROR] check.hexadecimal - string must be hexadecimal characters: " + str(ERROR_INVALID_KEY_FINGERPRINT)
	caplog.clear()

	caplog.set_level(logging.INFO)
	with pytest.raises(RuntimeError):
		gpg.encrypt(HAPPY_PATH_FILEPATH, ERROR_NONEXISTENT_KEY_ID)
	lines = caplog.text.splitlines()
	assert len(lines) == 3
	assert lines[0] == "[INFO] gpg.encrypt - Parameters: filepath=[" + str(HAPPY_PATH_FILEPATH) + "] recipient=[" + str(ERROR_NONEXISTENT_KEY_ID) + "]"
	assert lines[1] == "[WARNING] gnupg._collect_output - gpg returned a non-zero error code: 2"
	assert lines[2] == "[ERROR] gpg.encrypt - Recipient does not exist in gpg: " + str(ERROR_NONEXISTENT_KEY_ID)
	caplog.clear()

	open(HAPPY_PATH_OUTPUT, 'a').close()
	with pytest.raises(RuntimeError):
		gpg.encrypt(HAPPY_PATH_FILEPATH, HAPPY_PATH_RECIPIENT)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.encrypt - Parameters: filepath=[" + str(HAPPY_PATH_FILEPATH) + "] recipient=[" + str(HAPPY_PATH_RECIPIENT) + "]"
	assert lines[1] == "[ERROR] check.nonexistent - file or directory already exists: " + str(HAPPY_PATH_OUTPUT)
	caplog.clear()
	os.remove(HAPPY_PATH_OUTPUT)

## HAPPY PATH
	output = gpg.encrypt(HAPPY_PATH_FILEPATH, HAPPY_PATH_RECIPIENT)
	assert output == HAPPY_PATH_OUTPUT

	lines = caplog.text.splitlines()
	assert len(lines) == 3
	assert lines[0] == "[INFO] gpg.encrypt - Parameters: filepath=[" + str(HAPPY_PATH_FILEPATH) + "] recipient=[" + str(HAPPY_PATH_RECIPIENT) + "]"
	assert lines[1] == "[INFO] gpg.encrypt - Encrypting " + str(HAPPY_PATH_FILEPATH) + " with recipient " + str(HAPPY_PATH_RECIPIENT) + " into " + str(HAPPY_PATH_OUTPUT)
	assert lines[2] == "[INFO] gpg.encrypt - Encrypted " + str(HAPPY_PATH_FILEPATH) + " with recipient " + str(HAPPY_PATH_RECIPIENT) + " into " + str(HAPPY_PATH_OUTPUT)
	caplog.clear()

	## diff against "good" encrypted by same key
	filecmp.cmp(output, HAPPY_PATH_IDENTICAL_CONTENT, shallow=False)
	os.remove(HAPPY_PATH_OUTPUT)

## HAPPY PATH #2
	output = gpg.encrypt(HAPPY_PATH_FILEPATH, HAPPY_PATH_RECIPIENT_FINGERPRINT)
	assert output == HAPPY_PATH_OUTPUT

	lines = caplog.text.splitlines()
	assert len(lines) == 3
	assert lines[0] == "[INFO] gpg.encrypt - Parameters: filepath=[" + str(HAPPY_PATH_FILEPATH) + "] recipient=[" + str(HAPPY_PATH_RECIPIENT_FINGERPRINT) + "]"
	assert lines[1] == "[INFO] gpg.encrypt - Encrypting " + str(HAPPY_PATH_FILEPATH) + " with recipient " + str(HAPPY_PATH_RECIPIENT_FINGERPRINT) + " into " + str(HAPPY_PATH_OUTPUT)
	assert lines[2] == "[INFO] gpg.encrypt - Encrypted " + str(HAPPY_PATH_FILEPATH) + " with recipient " + str(HAPPY_PATH_RECIPIENT_FINGERPRINT) + " into " + str(HAPPY_PATH_OUTPUT)
	caplog.clear()

	## diff against "good" encrypted by same key
	filecmp.cmp(output, HAPPY_PATH_IDENTICAL_CONTENT, shallow=False)

def test_decrypt(caplog, tmp_path):
	caplog.set_level(logging.DEBUG)
	TMP_DIR = tmp_path / "tst.resources"
	shutil.copytree(tstconst.TEST_RESOURCES_DIR, TMP_DIR)

	HAPPY_PATH_FILEPATH = TMP_DIR / tstconst.ENCRYPTED_FILE
	HAPPY_PATH_OUTPUT = TMP_DIR / (tstconst.ENCRYPTED_FILE[:-13])
	HAPPY_PATH_IDENTICAL_CONTENT = TMP_DIR / tstconst.EXISTING_FILE

	ERROR_RELATIVE_FILEPATH = tstconst.EXISTING_FILE
	ERROR_NONEXISTENT_FILE = TMP_DIR / tstconst.NONEXISTENT_FILE
	ERROR_NON_FILE = TMP_DIR / tstconst.EXISTING_DIR
	ERROR_EMPTY_FILE = TMP_DIR / tstconst.EMPTY_FILE
	ERROR_NON_GPG_FILE = TMP_DIR / tstconst.EXISTING_FILE
	ERROR_GPG_FILE_INVALID_NAME = TMP_DIR / tstconst.GPG_FILE_INVALID_NAME

	ERROR_GPG_FILE_KEYID_INVALID = TMP_DIR / tstconst.GPG_FILE_KEYID_INVALID
	ERROR_GPG_FILE_KEYID_NONEXISTENT = TMP_DIR / tstconst.GPG_FILE_KEYID_NONEXISTENT

## INVALID INPUT
	with pytest.raises(RuntimeError):
		gpg.decrypt(ERROR_RELATIVE_FILEPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.decrypt - Parameters: filepath=[" + str(ERROR_RELATIVE_FILEPATH) + "]"
	assert lines[1] == "[ERROR] check.absolutePath - path must be an absolute path: " + str(ERROR_RELATIVE_FILEPATH)
	caplog.clear()

	with pytest.raises(RuntimeError):
		gpg.decrypt(ERROR_NONEXISTENT_FILE)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.decrypt - Parameters: filepath=[" + str(ERROR_NONEXISTENT_FILE) + "]"
	assert lines[1] == "[ERROR] check.exists - file or directory does not exist: " + str(ERROR_NONEXISTENT_FILE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		gpg.decrypt(ERROR_NON_FILE)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.decrypt - Parameters: filepath=[" + str(ERROR_NON_FILE) + "]"
	assert lines[1] == "[ERROR] check.isFile - f is not a file: " + str(ERROR_NON_FILE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		gpg.decrypt(ERROR_EMPTY_FILE)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.decrypt - Parameters: filepath=[" + str(ERROR_EMPTY_FILE) + "]"
	assert lines[1] == "[ERROR] check.fileSizeNonZero - file size is not greater than zero: " + str(ERROR_EMPTY_FILE) + " (0 bytes)"
	caplog.clear()

	with pytest.raises(RuntimeError):
		gpg.decrypt(ERROR_NON_GPG_FILE)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.decrypt - Parameters: filepath=[" + str(ERROR_NON_GPG_FILE) + "]"
	assert lines[1] == "[ERROR] check.endsIn - file must end in .gpg: " + str(ERROR_NON_GPG_FILE)
	caplog.clear()

	with pytest.raises(RuntimeError):
		gpg.decrypt(ERROR_GPG_FILE_INVALID_NAME)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.decrypt - Parameters: filepath=[" + str(ERROR_GPG_FILE_INVALID_NAME) + "]"
	assert lines[1] == "[ERROR] gpg.decrypt - Filepath must end in .KEY___ID.gpg: " + str(ERROR_GPG_FILE_INVALID_NAME)
	caplog.clear()

	open(HAPPY_PATH_OUTPUT, 'a').close()
	with pytest.raises(RuntimeError):
		gpg.decrypt(HAPPY_PATH_FILEPATH)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.decrypt - Parameters: filepath=[" + str(HAPPY_PATH_FILEPATH) + "]"
	assert lines[1] == "[ERROR] check.nonexistent - file or directory already exists: " + str(HAPPY_PATH_OUTPUT)
	caplog.clear()
	os.remove(HAPPY_PATH_OUTPUT)

	with pytest.raises(RuntimeError):
		gpg.decrypt(ERROR_GPG_FILE_KEYID_INVALID)
	lines = caplog.text.splitlines()
	assert len(lines) == 2
	assert lines[0] == "[INFO] gpg.decrypt - Parameters: filepath=[" + str(ERROR_GPG_FILE_KEYID_INVALID) + "]"
	assert lines[1] == "[ERROR] check.hexadecimal - string must be hexadecimal characters: " + str(ERROR_GPG_FILE_KEYID_INVALID)[:-4][-8:]
	caplog.clear()

	caplog.set_level(logging.INFO)
	with pytest.raises(RuntimeError):
		gpg.decrypt(ERROR_GPG_FILE_KEYID_NONEXISTENT)
	lines = caplog.text.splitlines()
	assert len(lines) == 3
	assert lines[0] == "[INFO] gpg.decrypt - Parameters: filepath=[" + str(ERROR_GPG_FILE_KEYID_NONEXISTENT) + "]"
	assert lines[1] == "[WARNING] gnupg._collect_output - gpg returned a non-zero error code: 2"
	assert lines[2] == "[ERROR] gpg.decrypt - Recipient does not exist in gpg: " + str(ERROR_GPG_FILE_KEYID_NONEXISTENT)[:-4][-8:]
	caplog.clear()

## HAPPY PATH
	output = gpg.decrypt(HAPPY_PATH_FILEPATH)
	assert output == str(HAPPY_PATH_OUTPUT)

	lines = caplog.text.splitlines()
	assert len(lines) == 3
	assert lines[0] == "[INFO] gpg.decrypt - Parameters: filepath=[" + str(HAPPY_PATH_FILEPATH) + "]"
	assert lines[1] == "[INFO] gpg.decrypt - Decrypting " + str(HAPPY_PATH_FILEPATH) + " into " + str(HAPPY_PATH_OUTPUT)
	assert lines[2] == "[INFO] gpg.decrypt - Decrypted " + str(HAPPY_PATH_FILEPATH) + " into " + str(HAPPY_PATH_OUTPUT)
	caplog.clear()

	# diff against decrypted original
	filecmp.cmp(output, HAPPY_PATH_IDENTICAL_CONTENT, shallow=False)
