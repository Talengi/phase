# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def navigation(request):
    """Fetches data required to render navigation menu.

    The main menu contains the list of user categories to choose.
    Here is the query to fetch them.

    """
    context = {}
    if hasattr(request, 'user_categories'):
        context.update({
            'user_categories': request.user_categories,
        })
    return context
