# -*- coding: utf-8 -*-


import json

from django.views.generic import View
from django.http import HttpResponse

from rest_framework.permissions import BasePermission
from celery.result import AsyncResult

from categories.models import Category


class TaskPollView(View):
    """Display information about an ongoing task.

    This view is intended to be polled with ajax.

    Since the displayed information is not critical, and the job id is
    auto-generated, we don't perform any acl verification.

    To create a pollable task :

    >>> from celery import current_task
    >>>
    >>> @app.task
    ... def pollable_task(*args):
    ...     # do things
    ...     current_task.update_state(
    ...         state='PROGRESS',
    ...         meta={'progress': 10})
    ...     # do things
    ...     current_task.update_state(
    ...         state='PROGRESS',
    ...         meta={'progress': 50})
    ...     # do things
    ...     return 'done'

    """
    def get(self, request, job_id):
        """Return json data to describe the task."""
        job = AsyncResult(job_id)

        done = job.ready()
        success = job.successful()
        result = job.result
        if isinstance(result, dict):
            progress = result.get('progress', 0)
        else:
            progress = 100.0 if done else 0.0

        data = {
            'done': done,
            'success': success,
            'progress': progress
        }

        # in case of error
        if done and not success:
            data['error_msg'] = 'System error: {}'.format(result)

        return HttpResponse(json.dumps(data), content_type='application/json')


class CategoryPermission(BasePermission):

    def has_permission(self, request, view):
        category = view.get_category()
        if category is None:
            return False
        return request.user in category.users.all()


class CategoryAPIViewMixin(object):
    """Mixin with category code handling.

    Some api views embeds a category parameters.
    E.g /accounts/<organisation>/<category>/

    Some custom permission handling must apply, i.e the requesting user
    must have access to the given category.

    """
    _category = None

    def get_permissions(self):
        perms = super(CategoryAPIViewMixin, self).get_permissions()
        return perms + [CategoryPermission()]

    def get_category(self):
        if self._category is None:
            organisation_slug = self.kwargs.get('organisation')
            category_slug = self.kwargs.get('category')
            try:
                self._category = Category.objects.get(
                    organisation__slug=organisation_slug,
                    category_template__slug=category_slug)
            except Category.DoesNotExist:
                self._category = None

        return self._category
