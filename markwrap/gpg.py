'''
Python wrapper for the gpg command
'''

import gnupg
import logging
import shutil
from . import process
from . import check

GPG_LOC = "/usr/local/bin/gpg"

logging.debug("Validating gpg install at %s", GPG_LOC)
validate_result = shutil.which(GPG_LOC)
if (validate_result is None):
	logging.error("gpg not found with shutil at %s", GPG_LOC)
	raise RuntimeError()
logging.debug("gpg found at %s", GPG_LOC)
process.quietRun([GPG_LOC,"--version"])
logging.debug("Validated gpg install at %s", GPG_LOC)

try:
	gpgTest = gnupg.GPG()
except OSError as error:
	if str(error) == "Unable to run gpg (gpg) - it may not be available.":
		logging.error("module gnupg cannot find gpg install")
		raise RuntimeError()
	else:
		raise OSError() from error
logging.debug("Validated module gnupg can locate gpg install")


gpg = gnupg.GPG()

def encrypt(filepath, recipient):
	check.absolutePath(filepath)
	check.exists(filepath)
	check.isFile(filepath)

	check.nonNone(recipient)
	check.hexadecimal(recipient)
	key = gpg.list_keys(keys=recipient)
	if len(key) != 1:
		logging.error("Recipient does not exist in gpg: %s", recipient)
		raise RuntimeError()

	targetFile = str(filepath) + "." + str(recipient)[-8:] + ".gpg"
	check.nonexistent(targetFile)

	logging.info("Encrypting %s with recipient %s into %s", filepath, recipient, targetFile)
	with open(filepath, "rb") as file:
		result = gpg.encrypt_file(file, recipient, armor=False, output=targetFile)
		if not result.ok:
			logging.error("Encryption of %s with key %s failed: %s", filepath, recipient, result.status)
			raise RuntimeError()

	check.exists(targetFile)
	check.isFile(targetFile)
	check.sizeNonZero(targetFile)
	logging.info("Encrypted %s with recipient %s into %s", filepath, recipient, targetFile)

	return targetFile

def decrypt(filepath):
	check.absolutePath(filepath)
	check.exists(filepath)
	check.isFile(filepath)
	check.endsIn(filepath, ".gpg")
	if str(filepath)[-13] != ".":
		logging.error("Filepath must end in .KEY___ID.gpg: %s", filepath)
		raise RuntimeError()

	targetFile = str(filepath)[:-13]
	check.nonexistent(targetFile)

	recipient = str(filepath)[:-4][-8:]
	check.hexadecimal(recipient)
	key = gpg.list_keys(keys=recipient)
	if len(key) != 1:
		logging.error("Recipient does not exist in gpg: %s", recipient)
		raise RuntimeError()

	logging.info("Decrypting %s into %s", filepath, targetFile)
	with open(filepath, "rb") as file:
		result = gpg.decrypt_file(file, output=targetFile)
		if not result.ok:
			logging.error("Decryption of %s failed: %s", filepath, result.status)
			raise RuntimeError()

	check.exists(targetFile)
	check.isFile(targetFile)
	check.sizeNonZero(targetFile)
	logging.info("Decrypted %s into %s", filepath, targetFile)

	return targetFile
