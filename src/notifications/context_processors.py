from django.contrib.auth.models import AnonymousUser

from notifications.models import Message


def notifications(request):
    """Fetches data required to render navigation menu.

    The main menu contains the list of user categories to choose.
    Here is the query to fetch them.

    """
    user = getattr(request, 'user')
    context = {}

    if not isinstance(user, AnonymousUser):
        notifications = Message.objects \
            .filter(user=user) \
            .filter(seen=False) \
            .order_by('-created_on')

        context.update({
            'notifications': notifications,
        })

    return context
