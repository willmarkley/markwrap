import markwrap.brew as brew
import logging


'''
Not asserting Homebrew is actually called with correct arguments.
Please manually test and verify before committing changes.
'''
def test_brew_listFormulae(caplog):
	## ARRANGE ##
	caplog.set_level(logging.DEBUG)

	## ACT ##
	brew.listFormulae()

	## ASSERT ##
	lines = caplog.text.splitlines()
	assert len(lines) >= 4
	assert lines[0]  == "[INFO] process.run - Process started   :  /usr/local/bin/brew list --formulae -1"
	assert lines[1].startswith("[INFO] process.run - STDOUT: ")
	assert lines[-2] == "[INFO] process.run - STDERR: "
	assert lines[-1] == "[INFO] process.run - Process terminated:  /usr/local/bin/brew list --formulae -1"

def test_brew_listCasks(caplog):
	## ARRANGE ##
	caplog.set_level(logging.DEBUG)

	## ACT ##
	brew.listCasks()

	## ASSERT ##
	lines = caplog.text.splitlines()
	assert len(lines) >= 4
	assert lines[0]  == "[INFO] process.run - Process started   :  /usr/local/bin/brew list --casks -1"
	assert lines[1].startswith("[INFO] process.run - STDOUT: ")
	assert lines[-2] == "[INFO] process.run - STDERR: "
	assert lines[-1] == "[INFO] process.run - Process terminated:  /usr/local/bin/brew list --casks -1"

def test_brew_update(caplog):
	## ARRANGE ##
	caplog.set_level(logging.DEBUG)

	## ACT ##
	brew.update()

	## ASSERT ##
	lines = caplog.text.splitlines()
	assert len(lines) == 4
	assert lines[0]  == "[INFO] process.run - Process started   :  /usr/local/bin/brew update"
	assert lines[1]  == "[INFO] process.run - STDOUT: Already up-to-date."
	assert lines[-2] == "[INFO] process.run - STDERR: "
	assert lines[-1] == "[INFO] process.run - Process terminated:  /usr/local/bin/brew update"

def test_brew_upgrade(caplog):
	## ARRANGE ##
	caplog.set_level(logging.DEBUG)

	## ACT ##
	brew.upgrade()

	## ASSERT ##
	lines = caplog.text.splitlines()
	assert len(lines) == 4
	assert lines[0]  == "[INFO] process.run - Process started   :  /usr/local/bin/brew upgrade"
	assert lines[1]  == "[INFO] process.run - STDOUT: "
	assert lines[-2]  == "[INFO] process.run - STDERR: "
	assert lines[-1]  == "[INFO] process.run - Process terminated:  /usr/local/bin/brew upgrade"
