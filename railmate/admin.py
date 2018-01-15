from django.contrib import admin

# Register your models here.

from .models import Trip, Profile, Message,Fellow_passengers


class MessageAdmin(admin.ModelAdmin):
    model = Message
    list_display = ('id', 'sender', 'content',)


admin.site.register(Message, MessageAdmin)
admin.site.register(Trip)
admin.site.register(Profile)
admin.site.register(Fellow_passengers)