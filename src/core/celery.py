try:
    import simplejson as json
except ImportError:
    import json
from datetime import date, datetime
from decimal import Decimal

from kombu.serialization import register
from celery import Celery

from django.conf import settings


app = Celery('phase')


# We need a custom serializer to handle date and datetime objects.
class JSONSerializer(json.JSONEncoder):
    def default(self, data):
        if isinstance(data, (date, datetime)):
            return data.isoformat()
        elif isinstance(data, Decimal):
            return float(data)
        raise TypeError("Unable to serialize %r (type: %s)" % (data, type(data)))


def my_dumps(obj):
    return json.dumps(obj, cls=JSONSerializer)


register(
    'betterjson',
    my_dumps,
    json.loads,
    content_type='application/x-myjson',
    content_encoding='utf-8')


# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
