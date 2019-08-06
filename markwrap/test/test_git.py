import markwrap.check as check
import markwrap.git as git
import logging
import os
import pytest

'''
Not asserting git is actually called with correct arguments.
Please manually test and verify before committing changes.
'''
def test_git_nodiff(caplog):
	## ARRANGE ##
	caplog.set_level(logging.DEBUG)

	## ACT ##
	result = git.nodiff(os.getcwd())

	## ASSERT ##
	assert result
	lines = caplog.text.splitlines()
	assert lines[0]  == "[INFO] process.run - Process started   :  /usr/local/bin/git diff origin/master"
	assert lines[1].startswith("[INFO] process.run - STDOUT: ")
	assert lines[2] == "[INFO] process.run - STDERR: "
	assert lines[3] == "[INFO] process.run - Process terminated:  /usr/local/bin/git diff origin/master"

def test_git_headHash(caplog):
	## ARRANGE ##
	caplog.set_level(logging.DEBUG)

	## ACT ##
	result = git.headHash(os.getcwd())

	## ASSERT ##
	assert result != ""
	assert len(result) == 40
	check.hexadecimal(result)
	lines = caplog.text.splitlines()
	assert lines[0]  == "[INFO] process.run - Process started   :  /usr/local/bin/git rev-parse HEAD"
	assert lines[1].startswith("[INFO] process.run - STDOUT: ")
	assert lines[2] == "[INFO] process.run - STDERR: "
	assert lines[3] == "[INFO] process.run - Process terminated:  /usr/local/bin/git rev-parse HEAD"

def test_git_headHash_badDir(caplog):
	## ARRANGE ##
	caplog.set_level(logging.DEBUG)

	## ACT & ASSERT ##
	with pytest.raises(RuntimeError):
		git.headHash("/tmp")

	lines = caplog.text.splitlines()
	assert lines[0]  == "[INFO] process.run - Process started   :  /usr/local/bin/git rev-parse HEAD"
	assert lines[1]  == "[INFO] process.run - STDOUT: "
	assert lines[2]  == "[INFO] process.run - STDERR: fatal: not a git repository (or any of the parent directories): .git"
