import csv

from django.http import HttpResponse


def make_csv_template(import_fields, filename):
    response = HttpResponse(content_type='text/csv')
    cd = 'attachment; filename="{}_template.csv"'.format(filename)
    response['Content-Disposition'] = cd
    fields = import_fields.values()
    writer = csv.writer(response)
    writer.writerow(fields)
    return response
