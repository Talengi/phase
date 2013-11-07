from django.contrib.auth.models import AnonymousUser

from categories.models import Category


def navigation(request):
    """Fetches data required to render navigation menu.

    The main menu contains the list of user categories to choose.
    Here is the query to fetch them.

    """
    user = getattr(request, 'user')
    context = {}

    if not isinstance(user, AnonymousUser):
        user_categories = Category.objects \
            .filter(users=user) \
            .select_related('category_template', 'organisation') \
            .order_by('organisation__name')

        context.update({
            'user_categories': user_categories,
        })

    return context
