'''
Run external processes
'''
import logging
import subprocess

def run(command):
	if not isinstance(command, type([])):
		logging.error("Command must be list: %s", command)
		raise RuntimeError()
	command_string = ' '.join(command)

	logging.info("Process started   :  %s", command_string)
	completed_process = subprocess.run(command, capture_output=True, text=True)
	logging.info("STDOUT: %s", completed_process.stdout.rstrip('\n'))
	logging.info("STDERR: %s", completed_process.stderr.rstrip('\n'))
	if (completed_process.returncode != 0):
		logging.error("Error running process [%s] (exit code %d):  %s", command_string, completed_process.returncode, completed_process)
		raise RuntimeError()
	logging.info("Process terminated:  %s", command_string)
	return completed_process.stdout

def quietRun(command):
	if not isinstance(command, type([])):
		logging.error("Command must be list: %s", command)
		raise RuntimeError()

	completed_process = subprocess.run(command, capture_output=True)
	if (completed_process.returncode != 0):
		logging.error("Error running process [%s] (exit code %d):  %s", ' '.join(command), completed_process.returncode, completed_process)
		raise RuntimeError()
