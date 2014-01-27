Getting started
###############

Introduction
------------

Phase is a document management system specifically designed for the needs of engineering and construction projects to manage the documentation of oil & gas, water treatment, nuclear, solar and wind facilities.

Phase offers the following characteristics:

* Management of document and data lists containing thousands of items
* Management of multiple metadata related to engineering, review, schedule, etc.
* Spreadsheet like filtering/search capabilities
* Document and data versioning
* Management of relationships between documents and data

Phase is intended to be used on projects where:

* Thousands of documents are generated
* Documents have to be produced, exchanged, reviewed, revised and used all along the project phases by multiple parties (owner/operator, contractors, vendors, partners, authorities, etc.)


Installation
------------

Steps to initialize the project on a local machine::

    $ git clone https://github.com/Talengi/phase.git repository
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r repository/requirements/local.txt
    $ npm -g install yuglify
    $ cd repository
    $ python phase/manage.py syncdb --noinput --settings=core.settings.local
    $ fab runserver


Available fabric commands
-------------------------

Check the list of available commands directly in your shell::

    $ fab -l
    Available commands:

        check      Checks that everything is fine, useful before deploying.
        deploy     Deploys the project against staging.
        docs       Generates sphinx documentation for the project.
        errors     Displays error.log file from staging.
        log        Displays access.log file from staging.
        runserver  Runs the local Django server.
        test       Launches tests for the whole project.


Apache configuration
--------------------

Here is a sample Apache virtual host configuration file.

.. literalinclude:: vhost_example
