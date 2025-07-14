import requests
from rest_framework.permissions import BasePermission
from django.conf import settings

class IsSupabaseAuthenticated(BasePermission):
    """
    Permissão que valida tokens do Supabase.
    """

    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ')[1]

        # Valida token consultando o endpoint do Supabase
        response = requests.get(
            f'{settings.SUPABASE_URL}/auth/v1/user',
            headers={
                'apikey': settings.SUPABASE_KEY,
                'Authorization': f'Bearer {token}'
            }
        )

        return response.status_code == 200
