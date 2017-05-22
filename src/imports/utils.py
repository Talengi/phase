# -*- coding: utf-8 -*-


import csv

from django.http import HttpResponse
from openpyxl import Workbook
from .models import normal_dialect

csv.register_dialect('normal', normal_dialect)


def make_csv_template(import_fields, filename):
    response = HttpResponse(content_type='text/csv')
    cd = 'attachment; filename="{}_template.csv"'.format(filename)
    response['Content-Disposition'] = cd
    fields = list(import_fields.keys())
    writer = csv.writer(response, delimiter=b';')
    writer.writerow(fields)
    return response


def make_xlsx_template(import_fields, filename):
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.'
                     'spreadsheetml.sheet')
    cd = 'attachment; filename="{}_template.xlsx"'.format(filename)
    response['Content-Disposition'] = cd
    fields = list(import_fields.keys())
    wb = Workbook()
    ws = wb.active
    ws.append(fields)
    wb.save(response)
    return response
