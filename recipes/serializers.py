from rest_framework import serializers
from .models import Recipe


class IngredientSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    quantity = serializers.FloatField()
    unit = serializers.CharField(max_length=50)

# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'name']

class RecipeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    ingredients = IngredientSerializer(many=True)
    #category = CategorySerializer()
    class Meta:
        model = Recipe
        #fields = ['id', 'user', 'title', 'ingredients', 'text_area', 'image_url', 'category']
        fields = ['id', 'user', 'title', 'ingredients', 'text_area', 'image_url']

    # Validar que os ingredientes sigam o padrão esperado
    def validate_ingredients(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Ingredientes devem ser passados como uma lista de objetos")

        for ingredient in value:
            if not all(key in ingredient for key in ('name', 'quantity', 'unit')):
                raise serializers.ValidationError("Cada ingrediente deve ter nome, quantidade e unidade")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        recipe = Recipe.objects.create(user=user, **validated_data)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        instance.title = validated_data.get('title', instance.title)
        instance.text_area = validated_data.get('text_area', instance.text_area)
        instance.image_url = validated_data.get('image_url', instance.image_url)
        # instance.category = validated_data.get('category', instance.category)

        if ingredients_data is not None:
            instance.ingredients = ingredients_data

        instance.save()
        return instance
