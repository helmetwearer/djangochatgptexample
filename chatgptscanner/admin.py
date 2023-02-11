from django.contrib import admin
from .models import *
# Register your models here.

class ChannelAdmin(admin.ModelAdmin):

    fields = ('name', 'bots_enabled')
    list_display = ('id', 'name', 'bots_enabled',)
    search_fields = ('name',)


admin.site.register(Channel, ChannelAdmin)

class ChatServerSettingsAdmin(admin.ModelAdmin):
    pass

admin.site.register(ChatServerSettings, ChatServerSettingsAdmin)