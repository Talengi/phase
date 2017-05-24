from django.conf.urls import url
from .views import AuditTrailList

urlpatterns = [
    url(r'^(?P<organisation>[\w-]+)/(?P<category>[\w-]+)/(?P<document_key>[\w-]+)/$',
        AuditTrailList.as_view(),
        name='document_audit_trail'),
]
