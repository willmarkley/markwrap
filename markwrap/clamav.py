'''
Python wrapper for the clamav commands

Please manually test and verify before committing changes.
'''

import logging
import pwd
import shutil
from . import process
from . import check

FRESHCLAM="/usr/local/bin/freshclam"
CLAMSCAN="/usr/local/bin/clamscan"
DATABASES="/var/lib/clamav"
CLAMSCAN_LOG_FILE="/var/log/clamscan.log"

logging.debug("Validating freshclam install at %s", FRESHCLAM)
validate_result = shutil.which(FRESHCLAM)
if (validate_result is None):
	logging.error("freshclam not found with shutil at %s", FRESHCLAM)
	raise RuntimeError()
logging.debug("freshclam found at %s", FRESHCLAM)
process.quietRun([FRESHCLAM,"--version"])
logging.debug("Validated freshclam install at %s", FRESHCLAM)

logging.debug("Validating clamscan install at %s", CLAMSCAN)
validate_result = shutil.which(CLAMSCAN)
if (validate_result is None):
	logging.error("clamscan not found with shutil at %s", CLAMSCAN)
	raise RuntimeError()
logging.debug("clamscan found at %s", CLAMSCAN)
process.quietRun([CLAMSCAN,"--version"])
logging.debug("Validated clamscan install at %s", CLAMSCAN)

logging.debug("Validating _clamav user exists on system")
try:
	pwd.getpwnam('_clamav')
except KeyError:
	logging.debug("_clamav user does not exist on system")
	raise
logging.debug("Validated _clamav user exists on system")

logging.debug("Validating database directory exists at %s")
check.isDir(DATABASES)
logging.debug("Validated database directory exists at %s")

logging.debug("Validating log file exists at %s", CLAMSCAN_LOG_FILE)
check.isFile(CLAMSCAN_LOG_FILE)
logging.debug("Validated log file exists at %s", CLAMSCAN_LOG_FILE)

def clamscan(dir):
	check.isDir(dir)
	process.run([CLAMSCAN,"-ro","--database="+DATABASES,"--log="+CLAMSCAN_LOG_FILE,dir])

def freshclam():
	process.run([FRESHCLAM, "-u","_clamav"])
