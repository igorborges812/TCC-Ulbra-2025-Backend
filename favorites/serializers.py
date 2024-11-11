from rest_framework import serializers
from .models import Favorite
from rest_framework.response import Response
from rest_framework import status

class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'recipe_id', 'created_at']
        read_only_fields = ('user', 'created_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        favorite = Favorite.objects.create(**validated_data)
        favorite.save()
        return favorite

    def destroy(self):
        instance = self.get_object()
        self.delete(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)