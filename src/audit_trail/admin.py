from django.contrib import admin

from documents.admin import NonEditableAdminMixin
from .models import Activity


class ActivityAdmin(NonEditableAdminMixin, admin.ModelAdmin):
    actions = None
    list_display = ('created_on', 'get_actor', 'verb', 'get_target', 'get_action_object')

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actor(self, obj):
        actor = obj.actor or obj.actor_object_str
        return actor
    get_actor.short_description = 'Actor'

    def get_target(self, obj):
        target = obj.target or obj.target_object_str
        return target
    get_target.short_description = 'Target'

    def get_action_object(self, obj):
        action_object = obj.action_object or obj.action_object_str
        return action_object
    get_action_object.short_description = 'Action Object'

admin.site.register(Activity, ActivityAdmin)

