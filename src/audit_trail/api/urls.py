from django.conf.urls import patterns, url
from .views import AuditTrailList

urlpatterns = patterns(
    '',
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/(?P<document_key>[\w-]+)/$',
        AuditTrailList.as_view(),
        name='document_audit_trail'),
)
