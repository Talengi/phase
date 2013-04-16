Welcome to EDMS's documentation!
================================

Introduction
------------

**TODO Talengi**


Installation
------------

Steps to initialize the project on a local machine::

    $ git clone https://github.com/Talengi/EDMS.git repository
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r repository/requirements/local.txt
    $ cd repository
    $ python EDMS/manage.py syncdb --noinput --settings=EDMS.settings.local
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


User stories completed
----------------------

* As a Document Controler, I want to browse paginated documents so that I can consult many documents (6000+).
* As a Document Controler, I want to sort documents by column so that I can access to recent documents.
* As a Document Controler, I want to search for documents (globally and per column) so that I can access to a given document or type of document.
* As a Document Controler, I want to create new documents so that I can browse more documents.
* As a Document Controler, I want to upload files to documents so that I can enrich documents.
* As a Document Controler, I want to display document details so that I can check all metadata and download attached files.

The repository has been tagged for each completed US.


Colophon
--------

* Django: https://www.djangoproject.com/
* Bootstrap: http://twitter.github.io/bootstrap/
* DataTables: http://www.datatables.net/
* Two Scoops of Django template: https://django.2scoops.org/
* Sphinx: http://sphinx-doc.org/
* Datepicker for Bootstrap: http://www.eyecon.ro/bootstrap-datepicker/
* File upload for Bootstrap: http://jasny.github.io/bootstrap/javascript.html#fileupload
