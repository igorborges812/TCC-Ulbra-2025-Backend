import re

from django.core.exceptions import ValidationError


def validate_password_strength(value):
    if len(value) < 8 or len(value) > 16:
        raise ValidationError('A senha deve conter entre 8 e 16 caracteres')
    if not re.search(r'[A-Z]', value):
        raise ValidationError('A senha deve conter pelo menos uma letra maiúscula')
    if not re.search(r'\d', value):
        raise ValidationError('A senha deve conter pelo menos um número')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError('A senha deve conter pelo menos um caractere especial')