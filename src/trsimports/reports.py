# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


class TrsReport(object):
    """A report to send to a transmittal communication list."""

    def __init__(self, trs_import):
        self.trs_import = trs_import
        self.email_list = trs_import.email_list

    @property
    def body(self):
        """Generates the email body."""
        raise NotImplementedError()

    def send(self):
        """Send the report to the email list."""
        send_mail(
            self.subject,
            self.body,
            settings.DEFAULT_FROM_EMAIL,
            self.email_list
        )


class ErrorReport(TrsReport):
    subject = 'Transmittals error report'

    @property
    def body(self):
        context = {
            'basename': self.trs_import.basename,
            'errors': self.trs_import.errors,
        }
        tpl = render_to_string('reports/error.txt', context)
        return tpl
