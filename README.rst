========
markwrap
========

.. image:: https://travis-ci.org/willmarkley/markwrap.svg?branch=master
    :target: https://travis-ci.org/willmarkley/markwrap

Python wrappers around common dependencies


Goals
=====

The goal of this Python package is to simplify calling common dependencies.  Each module of the package wraps the calls of a dependency.  Additionally, each module:

- logs every stage of the dependency call, as well as an errors that occur
- rigoriously validates the input before passing it to a dependency
- liberally raises exceptions

A client of this package should be confident that no silent error has occured.  Additionally, if an error occurs, the client should be able to easily trace it in the logs.  Finally, if no error is brought to attend, then the client should be confident the functionality of the dependency correctly occured.



Dependencies
============

- Python dependencies:

  - See `setup.py`_ for runtime dependencies
  - See `requirements.txt`_ for all dependencies
  - To install: ``pip install -r requirements.txt``

- Non-python dependencies:

  - `Homebrew`_
  - See `Brewfile`_
  - To install: ``brew bundle``


Testing
=======

::

    gpg --import markwrap/test/tst.resources/4C7798F2.asc
    echo -e "5\ny\n" | gpg --command-fd 0 --edit-key 4C7798F2 trust
    pytest --log-format="[%(levelname)s] %(module)s.%(funcName)s - %(message)s"


**Warning**: the 4C7798F2 will be added to your default gpg keyring on whichever system this command is run

*Note*: the 4C7798F2 was a publically available key retrieved from the `python-gnupg`_ `test_secring.gpg`_


.. _setup.py: setup.py
.. _requirements.txt: requirements.txt
.. _Homebrew: https://brew.sh/
.. _Brewfile: Brewfile
.. _python-gnupg: https://pypi.org/project/python-gnupg/
.. _test_secring.gpg: https://bitbucket.org/vinay.sajip/python-gnupg/src/default/test_secring.gpg
