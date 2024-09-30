import hashlib

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        if not nickname:
            raise ValueError('O nickname é obrigatório')
        
        email = self.normalize_email(email)
        user = self.model(email=email, nickname=nickname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, nickname, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=16, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    objects = CustomUserManager()

    def __str__(self):
        return self.nickname
    
    def deactivate_account(self):
        """Desativa a conta do usuário."""
        # Gerar um hash único baseado no ID
        unique_hash = hashlib.sha256(str(self.id).encode()).hexdigest()[:8]
        self.email = f"desativado_{unique_hash}@example.com"
        self.nickname = f"usuario-desativado{unique_hash}"
        self.is_active = False
        self.save()