Transmittals upload
###################

The transmittals upload feature allows a contractor to upload a bunch of
documents into a Phase instance directly from a ftp upload.

Introduction
------------

Manually creating hundreds of documents at once can be a very tedious task to
say the least. That's why Phase offers a feature to create many documents
in one shot by uploading a single file to the server.

Imported data is displayed on the Web UI and can be reviewed, validated or
rejected before the actual documents can be created.

Feature workflow
................

The whole feature workflow works like this:

#. A third-party generates a single archive with data XXX of documents. The
archive must respect certain conventions that will be detailed further or.

#. The archive file is dropped in a specific directory on the Phase server.

   Note 1: each first party gets it's own directory archive file names will never
   clash.

   Note 2: Phase does not care how the archive gets into the directory, it's
   your responsability to setup the file transfer method of your choice (ftp, ssh,
   etc.) However, we will provide instructions to setup an ftp server further on.

#. A management task will regularly parse archives and import the data (if
   valid) into Phase.

#. Phase users get an interface to review and approve / reject parsed data.

#. Once validated by the user, documents will automatically be imported into
   the appropriate category.

   Note3: Importing transmittals can be used to create new documents, create
   new revisions for existing documents, or update existing revisions.

Setting things up
.................

The transmittal import feature requires a tiny bit of settings. One has to
declare the third party allowed to drop transmittals, and which directory will
be used to store transmittals.

Here is a sample config bit::

    TRS_IMPORTS_ROOT = Path('/home/third_party_name')

    TRS_IMPORTS_CONFIG = {
        'third_party_name': {
            'INCOMING_DIR': TRS_IMPORTS_ROOT.child('incoming'),
            'REJECTED_DIR': TRS_IMPORTS_ROOT.child('rejected'),
            'TO_BE_CHECKED_DIR': TRS_IMPORTS_ROOT.child('tobechecked'),
            'ACCEPTED_DIR': TRS_IMPORTS_ROOT.child('accepted'),
            'EMAIL_LIST': ['warning@everybody.com'],
        }
    }

Please note that the listed directory have to exist and be accessible by Phase.

One also have to make sure two document categories are created.

The first category will host the final imported documents.
The second category will host the incoming transmittals.

So, for the sake of this documentation, let's create an organisation called
"Test". Then let's create a category called "Contractor deliverables" that will
host documents of type… `ContractorDeliverable`. Let's create a second category
called "Incoming transmittals" that MUST host documents of type `Transmittal`.

The two "slugs" corresponding to those categories are::

    /test/contractor-deliverables/
    /test/incoming-transmittals/

Transmittal columns
...................

The columns that will be imported in the transmittal must be defined in an
entry called `transmittal_columns` in the `PhaseConfig` class.

This field must be a dictionary mapping human readable field names to the
field django / database name.

Example::

    transmittal_columns = {
        'Document Number': 'document_key',
        'Title': 'title',
        'Contract Number': 'contract_number',
        'Originator': 'originator',
        'Unit': 'unit',
        'Discipline': 'discipline',
        'Document Type': 'document_type',
        'Sequential Number': 'sequential_number',
        'Class': 'docclass',
        'Revision': 'revision',
        'Status': 'status',
        'Received Date': 'received_date',
        'Created': 'created_on',
    }


Usage
-----

Importing transmittals
......................

The entry point for this feature is the `import_transmittals` management task.

Here is a sample usage::

    python manage.py import_transmittals third_party_name test/contractor-deliverables test/incoming-transmittals

* `third_party_name` is one of the entries in the `TRS_IMPORTS_CONFIG` settings.
* the two following parameters are the slugs of the two aforementioned categories.

This task will check and try to import all archives existing in the directory
pointed by the `INCOMING_DIR` settings entry

Transmittal format
..................

A single valid transmittal can be seen in the test directory fixtures.

https://github.com/Talengi/phase/tree/master/src/transmittals/tests/fixtures/single_correct_trs/FAC10005-CTR-CLT-TRS-00001

As a summary, this transmittal is made of the following elements:

- `FAC10005-CTR-CLT-TRS-00001/`: the enclosing directory, named after the transmittal.
  - `FAC10005-CTR-CLT-TRS-00001.csv`: the transmittal content, named after the transmittal
    with a `.csv` extension.
  - `FAC10005-CTR-000-EXP-LAY-4891_01.pdf`: the pdf file corresponding to one of the
    documents listed in the transmittal.
  - `FAC10005-CTR-000-EXP-LAY-4891_04.doc`: the native file corresponding to
    one of the file listed in the transmittal.

CSV file content
................

The csv file is structured as followed:

- One header line with the name of the different fields.
- One line for each document / revision to import.

Here is a sample header line::

    Document Number;Title;Contract Number;Originator;Unit;Discipline;Document Type;Sequential Number;Class;Revision;Status;Received Date;Created

Note that you must use the human-readable field names, corresponding to the ones
displayed in the "Document list" or "Document form" pages.

Here is a sample document line::

    FAC10005-CTR-000-EXP-LAY-4891;Cause & Effect Chart;FAC10005;CTR;000;EXP;LAY;4891;1;01;SPD;2014-09-24;2015-10-10


Data validation and format customization
........................................

The transmitted data is heavily validated at every stage of the process to ensure
that only clean and valid data will be imported.

The list of performed validations can be [found in this file](https://github.com/Talengi/phase/blob/master/src/transmittals/validation.py).

Note that there are two kinds of validators.

#. One set of validators applies [a set of rule to the entire transmittal](https://github.com/Talengi/phase/blob/master/src/transmittals/validation.py#L293)
to make sure the global data is valid, e.g the csv file is present and named correctly, etc.

#. One set of validators is [applied to each and every line of the csv file](https://github.com/Talengi/phase/blob/master/src/transmittals/validation.py#L272).

The import task allows you to pass custom validators so you can add your own
set of rules to the transmittal validation.

Here is a sample validator that checks that the `leader` and `approver` fields
are present and valid::

.. literalinclude:: trs_validators_example.py

You would use those using the following command::

    python manage.py import_transmittals third_party_name test/contractor-deliverables test/incoming-transmittals --csv-file-validador=myorg.validation.MyCsvLineValidator


Sending transmittals to the server
----------------------------------

Note that Phase doesn't care how the files are transmitted to the server (ftp,
ssh, nfs, etc.) so this section is for information only.

Here are the instructions to install and configure the ftp server to activate
this feature.

Ftp server installation and configuration
.........................................

We will use the proftpd server to handle ftp communication, and configure the
server to only accept ftps (ftp over ssl) connexions.

First, install the `proftpd` ftp server::


    aptitude install proftpd

Choose the "standalone" start method.

Create the ssl certificates for the TLS connection.

::

    openssl req -x509 -newkey rsa:2048 \
         -keyout /etc/ssl/private/proftpd.key -out /etc/ssl/certs/proftpd.crt \
         -nodes -days 365
    chmod 0600 /etc/ssl/private/proftpd.key
    chmod 0640 /etc/ssl/private/proftpd.key

Configure the server, using those examples files as starting points.

`/etc/proftpd/proftpd.conf`:

.. literalinclude:: proftpd.conf.example

`/etc/proftpd/tls.conf`:

.. literalinclude:: proftpd.tls.example

`/etc/proftpd/users.conf`:

.. literalinclude:: proftpd.users.example


User creation
.............

Let's create a unix user "test_ctr" for the contractor, and configure the
directory permissions.

::

    adduser test_ctr --disabled-password --ingroup=phase --shell=/bin/false
    chmod g+rwX /home/test_ctr
    echo "umask 002" >> /home/test_ctr/.profile

Note that for safety reasons, the list authorized users are explicitely
declared in the `/etc/proftpd/users.conf` file.
