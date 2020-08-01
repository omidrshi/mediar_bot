from django.contrib import admin
from .models import Chat, Media, Ad


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'chat_id')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'type_of_media', 'views_count', 'status')
    readonly_fields = ('file_name', 'file_id')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'views_count', 'status')
