import logging

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import int_to_base36
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.conf import settings


logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError('Oups, you forgot to give me an email')
        if not name:
            raise ValueError('I shall not be a horse with no name')

        user = self.model(email=email, name=name, is_staff=False,
                          is_active=True, is_superuser=False,
                          last_login=now, date_joined=now,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        user = self.create_user(email, name, password, **extra_fields)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    email = models.EmailField(
        _('Email address'),
        unique=True,
        db_index=True)
    name = models.CharField(
        _('Name'),
        max_length=64)
    position = models.CharField(
        _('Position'),
        max_length=50,
        null=True, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def send_account_activation_email(self, token, site=None):
        """Send an email with an activation link inside."""
        if not site:
            site = Site.objects.get_current()
        ctx = {
            'uidb36': int_to_base36(self.id),
            'token': token,
            'username': self.name,
            'site': site,
        }
        subject = render_to_string('registration/activation_email_subject.txt',
                                   ctx)
        # Remove new lines
        subject = ''.join(subject.splitlines())
        message = render_to_string('registration/activation_email.txt',
                                   ctx)

        logger.info('Sending welcome email to %s' % self.email)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])
