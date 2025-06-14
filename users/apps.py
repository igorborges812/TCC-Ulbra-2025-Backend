import os
from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        try:
            # Protegido por variável de ambiente (opcional, remova se não quiser)
            if os.getenv("CREATE_ADMIN", "true") == "true":
                User = get_user_model()
                if not User.objects.filter(username="admin").exists():
                    User.objects.create_superuser(
                        username="admin",
                        email="admin@email.com",
                        password="admin123"
                    )
        except (OperationalError, ProgrammingError):
            # Evita erro durante migrations ou banco indisponível
            pass
