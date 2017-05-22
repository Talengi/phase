# -*- coding: utf-8 -*-


from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


def get_repr(obj):
    if not obj:
        return ''
    method = getattr(obj, 'audit_trail_repr', None)
    if not method:
        return str(obj)
    return method()


class Activity(models.Model):

    VERB_CREATED = 'created'
    VERB_EDITED = 'edited'
    VERB_DELETED = 'deleted'
    VERB_JOINED = 'joined'
    VERB_STARTED_REVIEW = 'started_review'
    VERB_CANCELLED_REVIEW = 'cancelled_review'
    VERB_REVIEWED = 'reviewed'
    VERB_CLOSED_REVIEWER_STEP = 'closed_reviewer_step'
    VERB_CLOSED_LEADER_STEP = 'closed_leader_step'
    VERB_CLOSED_APPROVER_STEP = 'closed_approver_step'
    VERB_SENT_BACK_TO_LEADER_STEP = 'sent_back_to_leader_step'

    VERB_CHOICES = (
        (VERB_CREATED, _("created")),
        (VERB_EDITED, _("edited")),
        (VERB_DELETED, _("deleted")),
        (VERB_JOINED, _("joined Phase")),
        (VERB_STARTED_REVIEW, _("started review on")),
        (VERB_CANCELLED_REVIEW, _("cancelled review on")),
        (VERB_REVIEWED, _("reviewed")),
        (VERB_CLOSED_REVIEWER_STEP, _("closed reviewer step on")),
        (VERB_CLOSED_LEADER_STEP, _("closed leader step on")),
        (VERB_CLOSED_APPROVER_STEP, _("closed approver step on")),
        (VERB_SENT_BACK_TO_LEADER_STEP, _("sent review back to leader")),
    )

    SYSTEM_USER = _("System")
    NON_DB_USERS = (SYSTEM_USER,)

    # The object that performed the activity.
    actor_content_type = models.ForeignKey(
        ContentType, related_name='actor', blank=True, null=True)
    actor_object_id = models.PositiveIntegerField(blank=True, null=True)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')
    actor_object_str = models.CharField(
        verbose_name=_("Actor identifier"),
        max_length=254,
        blank=True,
        null=True)

    verb = models.CharField(
        _("Verb"), choices=VERB_CHOICES, default=VERB_JOINED, max_length=128)

    # The object linked to the action itself.
    action_object_content_type = models.ForeignKey(
        ContentType,
        related_name='action_object',
        blank=True,
        null=True)
    action_object_object_id = models.PositiveIntegerField(
        blank=True, null=True)
    action_object = GenericForeignKey(
        'action_object_content_type', 'action_object_object_id')
    action_object_str = models.CharField(max_length=255, blank=True)

    # The object to which the activity was performed.
    target_content_type = models.ForeignKey(
        ContentType, related_name='target', blank=True, null=True)
    target_object_id = models.PositiveIntegerField(blank=True, null=True)
    target = GenericForeignKey(
        'target_content_type', 'target_object_id')
    target_object_str = models.CharField(max_length=255, blank=True)

    created_on = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'audit_trail'
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')
        ordering = ['-created_on']

    def __str__(self):
        ctx = {
            'actor': self.actor or self.actor_object_str,
            'verb': self.get_verb_display(),
            'action_object': get_repr(self.action_object) or self.action_object_str,
            'target': get_repr(self.target) or self.target_object_str
        }
        if ctx['action_object'] and ctx['target']:
            return _('{actor} {verb} {action_object} on {target}').format(**ctx)
        elif ctx['action_object']:
            return _('{actor} {verb} {action_object}').format(**ctx)
        elif ctx['target']:
            return _('{actor} {verb} {target}').format(**ctx)
        return _('{actor} {verb}').format(**ctx)
