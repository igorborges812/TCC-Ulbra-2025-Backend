from django.db import models
from users.models import CustomUser

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name

class Recipe(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    ingredients = models.JSONField(null=False)
    text_area = models.JSONField(blank=False, null=False)

    # ✅ Armazena apenas o nome do arquivo (ex: abc123.jpg)
    image = models.CharField(max_length=255, null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return self.title
