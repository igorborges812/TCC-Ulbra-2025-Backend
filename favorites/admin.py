from django.contrib import admin
from .models import CustomUser, Favorite

admin.site.register(Favorite)