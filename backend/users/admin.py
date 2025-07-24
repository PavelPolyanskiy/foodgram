from django.contrib import admin
from .models import Follow, User

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
