# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.views.generic import View
from django.http import HttpResponse

from celery.result import AsyncResult


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
            data['error_msg'] = result.get('exc_message')

        return HttpResponse(json.dumps(data), content_type='application/json')
