import csv

from django.http import HttpResponse
from .models import normal_dialect

csv.register_dialect('normal', normal_dialect)


def make_csv_template(import_fields, filename):
    response = HttpResponse(content_type='text/csv')
    cd = 'attachment; filename="{}_template.csv"'.format(filename)
    response['Content-Disposition'] = cd
    fields = import_fields.keys()
    writer = csv.writer(response)
    writer.writerow(fields)
    return response
