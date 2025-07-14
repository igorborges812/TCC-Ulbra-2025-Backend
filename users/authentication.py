import requests
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import CustomUser


class SupabaseJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        # Verifica o token com o Supabase
        try:
            response = requests.get(
                f"{settings.SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.SUPABASE_KEY,
                },
            )
            if response.status_code != 200:
                raise AuthenticationFailed("Token inválido ou expirado.")

            data = response.json()
            email = data.get("email")
            nickname = data.get("user_metadata", {}).get("nickname", email.split("@")[0])

            if not email:
                raise AuthenticationFailed("Email não encontrado no token.")

            user, _ = CustomUser.objects.get_or_create(
                email=email,
                defaults={"username": nickname}
            )
            return (user, None)

        except requests.exceptions.RequestException:
            raise AuthenticationFailed("Erro ao validar token no Supabase.")
