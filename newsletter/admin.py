from django.contrib import admin

from .models import Newsletter, Subscription

admin.site.register(Newsletter)
admin.site.register(Subscription)
