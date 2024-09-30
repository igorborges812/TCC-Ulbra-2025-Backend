from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomUserAdmin(BaseUserAdmin):
    # Campos que aparecerão na lista de usuários no admin
    list_display = ('email', 'nickname', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser')

    # Campos para a página de edição de usuários no admin
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('nickname',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    
    # Campos exibidos no formulário de criação de novos usuários
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nickname', 'password1', 'password2'),
        }),
    )

    search_fields = ('email', 'nickname')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
