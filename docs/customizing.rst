Customizing document models
===========================

Phase comes with predefined document models. However, it is designed so you can create your own.

All you need to do is to create a new application with a name ending by *"_documents"*::

    mkdir myproject_app
    cd myproject_app
    django-admin.py startapp myproject_documents

You need to make sure that this application is accessible in the **PYTHONPATH**. If you use `virtualenvwrapper`_, you can use **add2virtualenv**::

    add2virtualenv myproject_app

Once this is done, add your application in the `core/settings/doc_apps.py` file
and run **migrate**.

Sample `doc_apps.py`::

    # -*- coding: utf-8 -*-
    from __future__ import unicode_literals

    DOC_APPS = (
        'epc2_documents',
        'sileo_documents',
    )

This file is listed in .gitignore and must not be commited.

Document model definition
-------------------------

Every document model is made of two classes: a base metadata class and a revision class. The base class must inherit of *documents.models.Metadata* and the revision class must inherit of *documents.models.MetadataRevision*.

Check the `default_documents.models` package for an up to date working example.

Required fields and methods
---------------------------

On the metadata base class, you must define a **latest_revision** field as a foreign key to the corresponding metadata class.

Inside this class, you also must define a **PhaseConfig** class the same way you would define a **Meta** class. This is used to configure how your document model integrates itself into Phase.

To have the full list of methods that you must implement, take a look in *documents/models.py* and check all methods that throw a *NotImplementedError*.

Document unique identifier
--------------------------

Every document in Phase have a unique identifier, stored in the *document_key* field. However, every document type must define how this field is generated.

This must be done in the *generate_document_key* method. Here is a example :

.. code:: python

    def generate_document_key(self):
        return slugify(
            u"{contract_number}-{originator}-{unit}-{discipline}-"
            u"{document_type}-{sequential_number}"
            .format(
                contract_number=self.contract_number,
                originator=self.originator,
                unit=self.unit,
                discipline=self.discipline,
                document_type=self.document_type,
                sequential_number=self.sequential_number
            )).upper()

The fields that you will use to build unique identifiers should also be listed in a *unique_together* entry in the *Meta* subclass.

Document list columns
---------------------

In *PhaseConfig*, the *column_fields* is used to define which fields will be displayed inside columns.

.. code:: python

    column_fields = (
        ('Document Number', 'document_key', 'document_key'),
        ('Title', 'title', 'title'),
        ('Rev.', 'current_revision', 'latest_revision.revision'),
        ('Rev. Date', 'current_revision_date', 'latest_revision.revision_date'),
        ('Status', 'status', 'latest_revision.status'),
    )

Each entry is composed of three elements:

#. The name that will be displayed in the column header.
#. The class that will be given to the column.
#. The accessor to get the column value. You can use a field name or a property.

Search and filter form
----------------------

In the document list, a document filter form is displayed to search and filter documents. Which field will be used is also defined in *PhaseConfig*.

.. code:: python

    # Here are the fields that fill appear in the filter form
    filter_fields = ('leader',)

    # Those fields will be searchable in the filter form
    # You can use fields from the base document or the revision
    searchable_fields = ('document_key', 'title')


Import fields
-------------

In *PhaseConfig*, the optionnal *import_fields* is used to define how to retrieve foreign keys
when importing documents and how to generate import templates.

.. code:: python

    import_fields = OrderedDict(('document_key', {}),
        ('title', {}),
        ('originator', {
            'model': 'accounts.Entity',
            'lookup_field': 'trigram'}),
        ('discipline', {}),
        ('document_type', {}),
        ('vd_code', {}),
        ('received_date', {}),
        ('docclass', {}),
        ('client_document_number', {}),
        ('status_idc_planned_date', {}),
        ('status_ifr_planned_date', {}),
        ('status_afc_planned_date', {}),
        # Revision fields
        ('revision', {}),
        ('status', {}),
        ('created_on', {}),
        ('purpose_of_issue', {}),)


Simple fields like *title* or *vd_code* are populated by inserted the imported value.
For foreign key, like *originator*, we specifiy a dcit conatining the referenced model (here *'accounts.Entity'*) and
the lookup field (*'trigram'*).


.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/
