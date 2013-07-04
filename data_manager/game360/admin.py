from django.contrib import admin
from game360.models import App

class AppAdmin(admin.ModelAdmin):
    list_display = ("appid", "name", )

admin.site.register(App, AppAdmin)
