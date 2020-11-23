'''
Common input validation checks

Every input must be an absolute path
'''
import logging
import os

'''
Object checks
'''
def nonNone(obj):
	if obj == None:
		logging.error("can NOT be None: %s", obj)
		raise RuntimeError()

def equal(expected, actual):
	nonNone(expected)
	nonNone(actual)
	if expected != actual:
		logging.error("Expected does not equal actual: %s != %s", expected, actual)
		raise RuntimeError()

'''
String checks
'''
def isString(s):
	nonNone(s)
	if not isinstance(s, str):
		logging.error("must be string: %s", s)
		raise RuntimeError()

def nonEmptyString(s):
	isString(s)
	if len(s) <= 0:
		logging.error("string cannot be empty: %s", s)
		raise RuntimeError()

def hexadecimal(s):
	nonEmptyString(s)

	try:
		int(s, 16)
	except ValueError:
		logging.error("string must be hexadecimal characters: %s",s)
		raise RuntimeError()

'''
Number checks
'''
def isNumber(i):
	nonNone(i)
	if not isinstance(i, int):
		logging.error('must be int: %s', i)
		raise RuntimeError()

def greaterThanZero(i):
	isNumber(i)
	if i <= 0:
		logging.error("number is less than zero", i)
		raise RuntimeError()

'''
Collection checks
'''
def noDuplicates(lst):
	nonNone(lst)
	if len(lst) != len(set(lst)):
		logging.error("duplicates found in list: %s", lst)
		raise RuntimeError()

'''
Path checks
'''
def pathlikeObject(path):
	nonNone(path)

	# https://docs.python.org/3/glossary.html#term-path-like-object
	if isinstance(path, str):
		nonEmptyString(path)
	elif not isinstance(path, os.PathLike):
		logging.error("path must be path-like object: %s", path)
		raise RuntimeError()

def absolutePath(path):
	pathlikeObject(path)
	if not os.path.isabs(path):
		logging.error("path must be an absolute path: %s", path)
		raise RuntimeError()

def exists(path):
	absolutePath(path)

	if not os.path.exists(path):
		logging.error("file or directory does not exist: %s", path)
		raise RuntimeError()

def nonexistent(path):
	absolutePath(path)

	if os.path.exists(path):
		logging.error("file or directory already exists: %s", path)
		raise RuntimeError()

def isFile(f):
	exists(f)

	if not os.path.isfile(f):
		logging.error("f is not a file: %s", f)
		raise RuntimeError()

def isDir(d):
	exists(d)

	if not os.path.isdir(d):
		logging.error("d is not a directory: %s", d)
		raise RuntimeError()

def endsIn(file, ending):
	pathlikeObject(file)
	nonEmptyString(ending)

	if str(file)[-len(ending):] != ending:
		logging.error("file must end in %s: %s", ending, file)
		raise RuntimeError()

def fileSizeNonZero(file):
	isFile(file)
	if os.path.getsize(file) <= 0:
		logging.error("file size is not greater than zero: %s (%d bytes)", file, os.path.getsize(file))
		raise RuntimeError()

def fileSizeEqual(file, size):
	isFile(file)
	if os.path.getsize(file) == size:
		logging.error("file size does not equal expected bytes of %s: %s (%d bytes)", size, file, os.path.getsize(file))
		raise RuntimeError()
