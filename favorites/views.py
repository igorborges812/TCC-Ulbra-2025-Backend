from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Favorite
from .serializers import FavoriteSerializer

class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Rota que retorna lista com todas as receitas favoritas de um usuário",
        operation_summary="Lista as receitas favoritas de um usuário",
        tags=["Favoritos"]
    )
    def get(self, request, *args, **kwargs):
        queryset = Favorite.objects.filter(user=self.request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FavoriteCreateView(generics.CreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Rota para registro de uma receita nos favoritos de um usuário",
        operation_summary="Adiciona uma receita aos favoritos de um usuário",
        tags=["Favoritos"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class FavoriteDeleteView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Rota para remoção de uma receita dos favoritos de um usuário",
        operation_summary="Remove uma receita dos favoritos de um usuário",
        tags=["Favoritos"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
