# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.dispatch import Signal, receiver
from accounts.models import User

activity_log = Signal(
    providing_args=[
        'actor',
        'verb',
        'action_object',
        'action_type',
        'target']
)


@receiver(activity_log, dispatch_uid='activity_log_uid')
def activity_handler(verb, action_object=None, target=None, **kwargs):
    from .models import Activity, get_repr

    kwargs.pop('signal', None)

    if verb not in zip(*Activity.VERB_CHOICES)[0]:
        raise ValueError("Verb must belong to Activity verbs")

    activity = Activity()
    activity.verb = verb

    activity.target = target
    # target_str = str(target) if target else ''
    target_str = get_repr(target)
    activity.target_object_str = kwargs.get('target_object_str', None) or target_str

    actor = kwargs.pop('actor')
    if isinstance(actor, User):
        activity.actor = actor
        activity.actor_object_str = str(actor)
    elif actor in Activity.NON_DB_USERS:
        activity.actor_object_str = actor
    else:
        raise ValueError("Actor must be a user instance or belong to "
                         "Activity NON_DB_USERS")

    if action_object:
        activity.action_object = action_object

    # activity.action_object_str = kwargs.get('action_object_str', None) or str(action_object)
    activity.action_object_str = kwargs.get('action_object_str', None) or get_repr(action_object)
    activity.save()
