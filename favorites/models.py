from django.db import models
from recipes.models import Recipe
from users.models import CustomUser

class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipe_id = models.ForeignKey(Recipe, blank=False, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe_id')

    def __str__(self):
        return f"{self.user.nickname} - {self.recipe_id}"
