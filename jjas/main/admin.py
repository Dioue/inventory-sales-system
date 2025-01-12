from django.contrib import admin
from django.contrib.auth.models import Group

# Unregister the Group model
admin.site.unregister(Group)
