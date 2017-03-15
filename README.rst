.. image:: https://travis-ci.org/enkidulan/enkiblog.svg?branch=master
    :target: https://travis-ci.org/enkidulan/enkiblog

This is a Websauna application package for enkiblog.

To run this package you need Python 3.4+, PostgresSQL and Redis.

Installation
============

This installation method assumes you the author of the enkiblog application and wish to develop it. Below are instructions to to install the package to a Python virtual environment using pip command in an editable mode.

Example::

    cd enkiblog  # This is the folder with setup.py file
    virtualenv venv
    source venv/bin/activate

    # Make sure pip itself is up-to-date
    pip install -U pip

    # Install the package and its dependencies to a currently
    # activated virtualenv from the folder with setup.py file
    pip install -e "."

Running the website
===================

Local development machine
-------------------------

Example (OSX / Homebrew)::

    # Create PostgreSQL database
    psql create enkiblog_dev

    # Write table schemas for models
    ws-sync-db enkiblog/conf/development.ini

    # Start web server
    ws-pserve enkiblog/conf/development.ini --reload

Running the test suite
======================

Example::

    # Install testing dependencies
    pip install ".[dev,test]"

    # Create database used for unit testing
    psql create enkiblog_test

    # Run test suite using py.test running
    py.test

More information
================

Please see https://websauna.org/
