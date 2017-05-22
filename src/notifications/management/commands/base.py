# -*- coding: utf-8 -*-


from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.utils import translation
from django.conf import settings


class EmailCommand(BaseCommand):
    """Base command to send email notifications."""
    text_template = None
    html_template = None

    def execute(self, *args, **options):

        if not settings.SEND_EMAIL_REMINDERS:
            raise CommandError('Reminders are disabled')

        translation.activate(settings.LANGUAGE_CODE)
        self.text_template = get_template(self.text_template)
        self.html_template = get_template(self.html_template)
        self.site = Site.objects.get_current()

        super(EmailCommand, self).execute(*args, **options)

    def send_notification(self, **kwargs):
        """Send a single email (eventually to several users at once)."""
        email = EmailMultiAlternatives(
            self.get_subject(**kwargs),
            self.get_text(**kwargs),
            settings.DEFAULT_FROM_EMAIL,
            self.get_recipient_list(**kwargs))
        email.attach_alternative(self.get_html(**kwargs), 'text/html')
        attachment = self.get_attachment(**kwargs)
        if attachment:
            email.attach_file(attachment)

        email.send()

    def get_attachment(self, **kwargs):
        return None

    def get_recipient_list(self, **kwargs):
        return []

    def get_subject(self, **kwargs):
        return 'Phase - reminder'

    def get_text(self, **kwargs):
        data = {'site': self.site}
        data.update(kwargs)
        return self.text_template.render(data)

    def get_html(self, **kwargs):
        data = {'site': self.site}
        data.update(kwargs)
        return self.html_template.render(data)
