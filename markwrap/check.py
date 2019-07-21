'''
Common input validation checks

Every input must be an absolute path
'''
import logging
import os

def nonNone(obj):
	if obj == None:
		logging.error("can NOT be None: %s", obj)
		raise RuntimeError()

def absolutePath(path):
	nonNone(path)
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
	nonNone(file)
	nonNone(ending)

	if str(file)[-len(ending):] != ending:
		logging.error("file must end in %s: %s", ending, file)
		raise RuntimeError()

def hexadecimal(s):
	nonNone(s)

	try:
		int(s, 16)
	except ValueError:
		logging.error("string must be hexadecimal characters: %s",s)
		raise RuntimeError()

def sizeNonZero(file):
	isFile(file)
	if os.path.getsize(file) <= 0:
		logging.error("file size is not greater than zero: %s (%d bytes)", file, os.path.getsize(file))
		raise RuntimeError()

def noDuplicates(lst):
	nonNone(lst)
	if len(lst) != len(set(lst)):
		logging.error("duplicates found in list: %s", lst)
		raise RuntimeError()
