from django.contrib.auth.models import AnonymousUser

import datetime

from django.core.cache import cache

from reviews.models import Review


def reviews(request):
    """Fetches data required to render reviews menu."""
    user = getattr(request, 'user')
    context = {}

    if not isinstance(user, AnonymousUser):

        context.update({
            'reviewer_count': get_step_count(request.user, 'reviewer'),
            'leader_count': get_step_count(request.user, 'leader'),
            'approver_count': get_step_count(request.user, 'approver'),
            'priorities_count': get_priorities_count(request.user),
        })

    return context


def get_step_count(user, step):
    """Get the number of pending reviews for given review step."""
    cache_key = 'review_step_count_%d_%s' % (user.id, step)
    count = cache.get(cache_key)
    if count is None:
        count = Review.objects \
            .filter(reviewer=user) \
            .filter(closed_on=None) \
            .filter(role=step) \
            .count()
        cache.set(cache_key, count, None)

    return count


def get_priorities_count(user):
    cache_key = 'review_step_count_%d_priorities' % user.id
    count = cache.get(cache_key)
    if count is None:
        delta = datetime.date.today() + datetime.timedelta(days=5)
        count = Review.objects \
            .filter(reviewer=user) \
            .filter(due_date__lte=delta) \
            .filter(closed_on=None) \
            .filter(role__in=['leader', 'approver']) \
            .filter(docclass__lte=2) \
            .count()
        cache.set(cache_key, count, None)

    return count
