# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from notifications.models import Notification


def notifications(request):
    """Fetches data required to render navigation menu.

    The main menu contains the list of user categories to choose.
    Here is the query to fetch them.

    """
    user = getattr(request, 'user')
    context = {}

    if not isinstance(user, AnonymousUser):
        qs = Notification.objects \
            .filter(user=user) \
            .order_by('-created_on')
        notifications = list(qs[0:settings.DISPLAY_NOTIFICATION_COUNT])

        has_new_notifications = (not notifications[0].seen)

        context.update({
            'notifications': notifications,
            'has_new_notifications': has_new_notifications,
        })
        print has_new_notifications

    return context
