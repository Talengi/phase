#!/usr/bin/python
# -*- coding: utf-8 -*-


CORRESPONDENCE_STATUSES = [
    ('opened', 'Opened'),
    ('closed', 'Closed'),
    ('hold', 'Hold'),
]

CLASSES = [
    (classe, str(classe)) for classe in range(1, 5)
]

BOOLEANS = [(True, u"Yes"), (False, u"No")]
