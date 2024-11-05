from django.db import models
from django.conf import settings

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    recipe_id = models.UUIDField()  # ID da receita favorita
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe_id')

    def __str__(self):
        return f"{self.user.nickname} - {self.recipe_id}"
