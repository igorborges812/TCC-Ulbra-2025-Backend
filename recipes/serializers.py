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
    ingredients = IngredientSerializer(many=True)
    text_area = serializers.ListField(
        child=serializers.CharField(max_length=1000)
    )

    class Meta:
        model = Recipe
        fields = ['id', 'user', 'title', 'ingredients', 'text_area', 'image', 'category', 'category_name']

    def validate_ingredients(self, value):
        """
        Valida o campo 'ingredients' para garantir que seja uma lista de ingredientes válida.
        """
        if not isinstance(value, list):
            raise serializers.ValidationError('Deve ser uma lista de ingredientes.')

        if len(value) == 0:
            raise serializers.ValidationError('A lista de ingredientes não pode estar vazia.')

        for idx, ingredient in enumerate(value):
            if not isinstance(ingredient, dict):
                raise serializers.ValidationError(f'Ingrediente na posição {idx} deve ser um objeto.')

            # Verifica se todos os campos necessários estão presentes
            required_fields = ['name', 'quantity', 'unit']
            for field in required_fields:
                if field not in ingredient:
                    raise serializers.ValidationError(f"O campo '{field}' é obrigatório no ingrediente na posição {idx}.")

            # Valida o tipo de cada campo
            if not isinstance(ingredient['name'], str) or not ingredient['name'].strip():
                raise serializers.ValidationError(f"O campo 'name' no ingrediente na posição {idx} deve ser uma string não vazia.")

            if not isinstance(ingredient['quantity'], (int, float)):
                raise serializers.ValidationError(f"O campo 'quantity' no ingrediente na posição {idx} deve ser um número.")

            if not isinstance(ingredient['unit'], str) or not ingredient['unit'].strip():
                raise serializers.ValidationError(f"O campo 'unit' no ingrediente na posição {idx} deve ser uma string não vazia.")

        return value