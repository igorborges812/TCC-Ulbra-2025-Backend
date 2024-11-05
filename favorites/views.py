from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Favorite
from .serializers import FavoriteSerializer

class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

class FavoriteCreateView(generics.CreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FavoriteDeleteView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        recipe_id = self.kwargs['recipe_id']
        return Favorite.objects.get(user=self.request.user, recipe_id=recipe_id)