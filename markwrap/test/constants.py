import os

TEST_CONSTANTS_FILE = os.path.abspath(__file__)
TEST_DIR = os.path.dirname(TEST_CONSTANTS_FILE)
TEST_RESOURCES_DIR = TEST_DIR + "/tst.resources"


EXISTING_DIR = "dirs"
EXISTING_DIR_A = "dirs/a"
EXISTING_DIR_B = "dirs/b"
EXISTING_DIR_C = "dirs/c"
EXISTING_FILE  = "file.txt"
EXISTING_ARCHIVE = "archive.tar.gz"

NONEXISTENT_DIR = "new"
NONEXISTENT_FILE = "new.txt"
NONEXISTENT_ARCHIVE = "new.tar.gz"
