from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type', 'first_name', 'last_name')


admin.site.register(Profile, ProfileAdmin)
