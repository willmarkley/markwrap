import markwrap.clamav as clamav
import logging


'''
Not asserting clamav is actually called with correct arguments.
Please manually test and verify before committing changes.
'''
def test_clamav_clamscan(caplog):
	## ARRANGE ##
	caplog.set_level(logging.DEBUG)
	TEST_INPUT_DIR = '/tmp'

	## ACT ##
	clamav.clamscan(TEST_INPUT_DIR)

	## ASSERT ##
	lines = caplog.text.splitlines()
	assert len(lines) >= 4
	assert lines[0]  == "[INFO] process.run - Process started   :  /usr/local/bin/clamscan -ro --database=/var/lib/clamav --log=/var/log/clamscan.log "+TEST_INPUT_DIR
	assert lines[1].startswith("[INFO] process.run - STDOUT: ")
	assert lines[-2] == "[INFO] process.run - STDERR: "
	assert lines[-1] == "[INFO] process.run - Process terminated:  /usr/local/bin/clamscan -ro --database=/var/lib/clamav --log=/var/log/clamscan.log "+TEST_INPUT_DIR

def test_clamav_freshclam(caplog):
	## ARRANGE ##
	caplog.set_level(logging.DEBUG)

	## ACT ##
	clamav.freshclam()

	## ASSERT ##
	lines = caplog.text.splitlines()
	assert len(lines) >= 4
	assert lines[0]  == "[INFO] process.run - Process started   :  /usr/local/bin/freshclam -u _clamav"
	assert lines[1].startswith("[INFO] process.run - STDOUT: ")
	assert lines[-2] == "[INFO] process.run - STDERR: "
	assert lines[-1] == "[INFO] process.run - Process terminated:  /usr/local/bin/freshclam -u _clamav"
