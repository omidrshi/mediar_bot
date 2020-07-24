from django.contrib import admin
from .models import Chat, Media, Ad


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    pass


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    readonly_fields = ('file_name', 'file_id')


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    pass
