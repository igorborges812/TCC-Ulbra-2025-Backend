import json

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

    class Meta:
        model = Recipe
        fields = ['id', 'user', 'title', 'ingredients', 'text_area', 'image', 'category', 'category_name']

    def to_internal_value(self, data):
        ingredients_data = data.get('ingredients')
        
        if ingredients_data is None:
            raise serializers.ValidationError({'ingredients': 'This field is required.'})
        
        if not isinstance(ingredients_data, list):
            raise serializers.ValidationError({'ingredients': 'Must be a list of ingredients.'})
        
        for ingredient in ingredients_data:
            if not all(key in ingredient for key in ('name', 'quantity', 'unit')):
                raise serializers.ValidationError({'ingredients': 'Each ingredient must have name, quantity, and unit.'})
            
        data_copy = data.copy()
        data_copy.pop('ingredients')
        ret = super().to_internal_value(data_copy)
        ret['ingredients'] = ingredients_data
        return ret

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        if isinstance(ingredients_data, dict):
            ingredients_data = [ingredients_data]
        recipe = Recipe.objects.create(**validated_data)
        recipe.ingredients = ingredients_data
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        if ingredients_data is not None:
            if isinstance(ingredients_data, dict):
                ingredients_data = [ingredients_data]
            instance.ingredients = ingredients_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance