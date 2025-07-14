# users/permissions.py
import requests
from rest_framework.permissions import BasePermission
from django.conf import settings

class IsAuthenticatedWithSupabase(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ')[1]

        response = requests.get(
            f"{settings.SUPABASE_URL}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": settings.SUPABASE_KEY
            }
        )

        if response.status_code == 200:
            request.user_supabase = response.json()
            return True
        return False
