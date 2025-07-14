from rest_framework import serializers
from .models import Category, Recipe

class RecipeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False)
    category_name = serializers.CharField(source='category.name', read_only=True)
    new_category = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'user',
            'title',
            'ingredients',
            'text_area',
            'image',
            'image_url',
            'category',
            'category_name',
            'new_category',
        ]
        read_only_fields = ['image_url']

    def create(self, validated_data):
        user = self.context['request'].user
        new_category_name = validated_data.pop('new_category', None)

        if new_category_name:
            category_obj, _ = Category.objects.get_or_create(name=new_category_name.strip().title())
            validated_data['category'] = category_obj

        return Recipe.objects.create(user=user, **validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        image_url = None
        if instance.image and hasattr(instance.image, 'url'):
            request = self.context.get('request', None)
            if request:
                image_url = request.build_absolute_uri(instance.image.url)
            else:
                image_url = instance.image.url

        data['image_url'] = image_url
        return data
