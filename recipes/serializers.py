from rest_framework import serializers
from .models import Category, Recipe

SUPABASE_URL = "https://sizovghaygzecxbgvqvb.supabase.co"
SUPABASE_BUCKET = "receitas"

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
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)
    category_name = serializers.CharField(source='category.name', read_only=True)
    new_category = serializers.CharField(write_only=True, required=False)

    image_url = serializers.SerializerMethodField() 

    class Meta:
        model = Recipe
        fields = [
            'id',
            'user',
            'title',
            'ingredients',
            'text_area',
            'image_url',  
            'category',
            'category_name',
            'new_category',
        ]

    def get_image_url(self, obj):
        if obj.image:
            if obj.image.startswith("http"):
                return obj.image
            return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{obj.image}"
        return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/default_recipe.png"

    def create(self, validated_data):
        user = self.context['request'].user
        new_category_name = validated_data.pop('new_category', None)

        if new_category_name:
            category_obj, _ = Category.objects.get_or_create(name=new_category_name.strip().title())
            validated_data['category'] = category_obj

        return Recipe.objects.create(user=user, **validated_data)
