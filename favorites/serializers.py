from rest_framework import serializers
from recipes.serializers import RecipeSerializer
from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'recipe_id', 'created_at']
        read_only_fields = ('user', 'created_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Favorite.objects.create(**validated_data)


# 🔥 Serializer que retorna os dados completos da receita favoritada
class FavoriteRecipeSerializer(serializers.ModelSerializer):
    recipe_id = RecipeSerializer()

    class Meta:
        model = Favorite
        fields = ['id', 'recipe_id', 'created_at']