import os
from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        try:
            if os.getenv("CREATE_ADMIN", "true") == "true":
                User = get_user_model()
                if not User.objects.filter(email="admin@email.com").exists():
                    User.objects.create_superuser(
                        email="admin@email.com",
                        password="admin123",
                        nickname="Admin"
                    )
        except (OperationalError, ProgrammingError):
            pass
