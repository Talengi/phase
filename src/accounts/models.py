# -*- coding: utf-8 -*-


import logging

from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.conf import settings

from model_utils import Choices


logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def create_user(self, email, name, username=None, password=None, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError('Oups, you forgot to give me an email')
        if not name:
            raise ValueError('I shall not be a horse with no name')

        if not username:
            username = email.split('@')[0]

        user = self.model(email=email, name=name, username=username,
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, username=None, password=None, **extra_fields):
        user = self.create_user(email, name, username, password, **extra_fields)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, email):
        return self.get(email=email)


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    email = models.EmailField(
        _('Email address'),
        unique=True,
        db_index=True)
    name = models.CharField(
        _('Name'),
        max_length=64)
    username = models.SlugField(
        _('Username'),
        unique=True,
        db_index=True,
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
    is_external = models.BooleanField(
        _('External User'),
        default=False,
        help_text=_('Used to tell apart regular users and externals ones'
                    ' (contractors).'))
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now)

    send_closed_reviews_mails = models.BooleanField(
        _('Send mails when reviews are closed'),
        default=True)
    send_pending_reviews_mails = models.BooleanField(
        _('Send pending reviews reminders'),
        default=True)
    send_trs_reminders_mails = models.BooleanField(
        _('Send reminders for outgoing transmittals with missing '
          'acknowledgement of receipt'),
        default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        app_label = 'accounts'

    def __str__(self):
        return self.name

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def send_account_activation_email(self, token, site=None):
        """Send an email with an activation link inside."""
        if not site:
            site = Site.objects.get_current()
        ctx = {
            'uidb64': urlsafe_base64_encode('{}'.format(self.id).encode()),
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


class EntityManager(models.Manager):
    def get_by_natural_key(self, trigram):
        return self.get(trigram=trigram)


class Entity(models.Model):
    """Defines a contractual third party."""
    TYPES = Choices(
        ('contractor', _('Contractor')),
        ('supplier', _('Supplier')),
        ('originator', _('Originator')),
        ('other', _('Other')),
    )
    objects = EntityManager()

    name = models.CharField(
        _('name'),
        max_length=80,
        unique=True)
    trigram = models.CharField(
        _('Trigram'),
        max_length=3,
        unique=True)
    type = models.CharField(
        _('Type'),
        max_length=80,
        choices=TYPES,
        default=TYPES.contractor)
    users = models.ManyToManyField(
        User,
        verbose_name=_('Users'),
        blank=True)

    class Meta:
        verbose_name = _('Entity')
        verbose_name_plural = _('Entities')

    def __str__(self):
        return '{} - {}'.format(self.trigram, self.name)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Entity, self).save(force_insert, force_update, using,
                                 update_fields)
        # Clear `entities_pk` cache
        clear_entities_cache()


def get_entities(user):
    """Put the entities list in cache if user belongs to one or several of
    them (if he is a contractor)."""
    cache_key_pk = 'entities_pk_%d' % user.id
    entities_pk = cache.get(cache_key_pk)
    if entities_pk is None:
        entities = Entity.objects.filter(users=user)
        entities_pk = entities.values_list('pk', flat=True)
        cache.set(cache_key_pk, entities_pk, None)
    return list(entities_pk)


def clear_entities_cache():
    users_pk = User.objects.values_list('pk', flat=True)
    cache.delete_many(['entities_pk_%d' % pk for pk in users_pk])
