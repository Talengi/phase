from django.apps.config import AppConfig


class ReviewsConfig(AppConfig):
    name = 'reviews'

    def ready(self):
        import reviews.signals  # noqa
