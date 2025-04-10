from rest_framework import serializers

from .models import Category, Recipe


class IngredientSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    quantity = serializers.FloatField()
    unit = serializers.CharField(max_length=50)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class RecipeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'user', 'title', 'ingredients', 'text_area', 'image', 'category', 'category_name']

    def to_representation(self, instance):
        # Começa com a representação padrão
        representation = super().to_representation(instance)

        import json

        # Ingredientes: tenta decodificar a string JSON salva no banco
        try:
            representation['ingredients'] = json.loads(instance.ingredients)
        except Exception:
            representation['ingredients'] = []

        # Text area: idem
        try:
            representation['text_area'] = json.loads(instance.text_area)
        except Exception:
            representation['text_area'] = []

        return representation