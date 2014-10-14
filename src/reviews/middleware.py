from django.core.cache import cache

from reviews.models import Review


class ReviewCountMiddleware(object):
    def process_template_response(self, request, response):

        response.context_data.update({
            'reviewer_count': self.get_step_count(request.user, 'reviewer'),
            'leader_count': self.get_step_count(request.user, 'leader'),
            'approver_count': self.get_step_count(request.user, 'approver')
        })
        return response

    def get_step_count(self, user, step):
        """Get the number of pending reviews for given review step."""
        cache_key = 'review_step_count_%d_%s' % (user.id, step)
        count = cache.get(cache_key)
        if count is None:
            count = Review.objects \
                .filter(reviewer=user) \
                .filter(closed=False) \
                .filter(role=step) \
                .count()
            cache.set(cache_key, count, None)

        return count
