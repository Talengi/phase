Customizing document models
===========================

Phase comes with predefined document models. However, it is designed so you can create your own.



All you need to do is to create a new application with a name ending by *"_documents"*::

    mkdir myproject_app
    cd myproject_app
    django-admin.py startapp myproject_documents

You need to make sure that this application is accessible in the **PYTHONPATH**. If you use `virtualenvwrapper`_, you can use **add2virtualenv**::

    add2virtualenv myproject_app

Once this is done, add your application to the **INSTALLED_APPS** list and run **syncdb**.

Document model definition
-------------------------

Every document model is made of two classes: a base metadata class and a revision class. The base class must inherit of *documents.models.Metadata* and the revision class must inherit of *documents.models.MetadataRevision*.

Here's a basic sample:

.. code:: python


    class DemoMetadata(Metadata):

        # This field with this exact name is required
        latest_revision = models.ForeignKey(
            'DemoMetadataRevision',
            verbose_name=_('Latest revision'),
            null=True)
        title = models.CharField(
            _('Title'),
            max_length=50)
        leader = models.ForeignKey(
            User,
            verbose_name=_('Leader'),
            related_name='leading_demo_metadata',
            null=True, blank=True)

        class Meta:
            ordering = ('title',)

        # This is a custom class, required to configure the document model
        class PhaseConfig:
            # Here are the fields that fill appear in the filter form
            filter_fields = (
                'leader',
            )

            # Those fields will be searchable in the filter form
            searchable_fields = (
                'document_key', 'title'
            )
            # Column definition
            column_fields = (
                ('Document Number', 'document_key'),
                ('Title', 'title'),
                ('Rev.', 'current_revision'),
                ('Rev. Date', 'current_revision_date'),
                ('Status', 'status'),
            )

        def natural_key(self):
            return (self.document_key,)

        def generate_document_key(self):
            return slugify(self.title)


    class DemoMetadataRevision(MetadataRevision):
        STATUSES = (
            ('opened', 'Opened'),
            ('closed', 'Closed'),
        )
        native_file = RevisionFileField(
            _('Native File'),
            null=True, blank=True)
        pdf_file = RevisionFileField(
            _('PDF File'),
            null=True, blank=True)
        status = models.CharField(
            _('Status'),
            max_length=20,
            choices=STATUSES,
            null=True, blank=True)


Some fields and methods **must** be defined on the base class.

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


.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/
