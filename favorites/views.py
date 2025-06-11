from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import Favorite
from .serializers import FavoriteSerializer, FavoriteRecipeSerializer


class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


class FavoriteCreateView(generics.CreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Adiciona uma receita aos favoritos",
        operation_summary="Adicionar favorito",
        tags=["Favoritos"]
    )
    def post(self, request, *args, **kwargs):
        recipe_id = request.data.get('recipe_id')
        if Favorite.objects.filter(user=request.user, recipe_id=recipe_id).exists():
            return Response(
                {"detail": "Essa receita já está nos favoritos."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().post(request, *args, **kwargs)


class FavoriteDeleteView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
