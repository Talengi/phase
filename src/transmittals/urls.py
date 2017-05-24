from django.conf.urls import url

from transmittals.views import (
    TransmittalList, TransmittalDiff, TransmittalRevisionDiff,
    TransmittalDownload, PrepareTransmittal, CreateTransmittal,
    AckOfTransmittalReceipt, BatchAckOfTransmittalReceipt)

urlpatterns = [
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/prepare/$',
        PrepareTransmittal.as_view(),
        name="transmittal_prepare"),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/create/$',
        CreateTransmittal.as_view(),
        name="transmittal_create"),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/ack/$',
        BatchAckOfTransmittalReceipt.as_view(),
        name="transmittal_batch_ack_of_receipt"),
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/(?P<document_key>[\w-]+)/ack/$',
        AckOfTransmittalReceipt.as_view(),
        name="transmittal_ack_of_receipt"),

    # Incoming transmittal urls
    url(r'^incoming/$',
        TransmittalList.as_view(),
        name="transmittal_list"),
    url(r'^incoming/(?P<transmittal_pk>\d+)/(?P<document_key>[\w-]+)/$',
        TransmittalDiff.as_view(),
        name='transmittal_diff'),
    url(r'^incoming/(?P<transmittal_pk>\d+)/(?P<document_key>[\w-]+)/download/$',
        TransmittalDownload.as_view(),
        name='transmittal_download'),
    url(r'^incoming/(?P<transmittal_pk>\d+)/(?P<document_key>[\w-]+)/(?P<revision_document_key>[\w-]+)/(?P<revision>\d+)/$',
        TransmittalRevisionDiff.as_view(),
        name='transmittal_revision_diff'),
]
