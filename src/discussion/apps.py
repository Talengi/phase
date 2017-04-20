from django.apps.config import AppConfig


class DiscussionConfig(AppConfig):
    name = 'discussion'

    def ready(self):
        import discussion.signals  # noqa
