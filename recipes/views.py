import base64
import string, random
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from .models import Recipe
from .serializers import RecipeSerializer
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.core.files.base import ContentFile


class RegisterRecipeView(generics.CreateAPIView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.sb_bucket_name = settings.SB_BUCKET_NAME
        self.sb_bucket_path = settings.SB_BUCKET_PATH
        self.sb_url = settings.SB_URL
        self.sb_key = settings.SB_KEY

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeSerializer

    @swagger_auto_schema(
        responses={201: openapi.Response(
            description="Objeto contendo dados da receita criada",
            schema=RecipeSerializer
        )},
        operation_description="Rota para registro de uma nova receita",
        operation_summary="Cria uma receita",
        tags=["Receitas"]
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        image_base64 = request.data.get('image_base64')

        if image_base64:
            try:
                image_data = ContentFile(base64.b64decode(image_base64),
                                         name=f"{''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=30))}.jpg")

                # Add the decoded image data to the request data
                request.data['image'] = image_data
            except Exception as e:
                raise ValidationError(f"Failed to decode base64 image: {str(e)}")

        return super().post(request, *args, **kwargs)

class GetRecipesView(generics.ListAPIView):
    queryset = Recipe.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RecipeSerializer

    @swagger_auto_schema(
    responses={201: openapi.Response(
            description="Lista de receitas salvas",
            schema=RecipeSerializer
        )},
    operation_description="Rota que retorna lista com todas as receitas existentes",
    operation_summary="Lista todas as receitas",
    tags=["Receitas"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class GetRecipeByIdView(generics.RetrieveAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'id'

    @swagger_auto_schema(
    responses={201: openapi.Response(
                description="Objeto JSON da receita encontrada com base no ID passado",
                schema=RecipeSerializer
            )},
    operation_description="Rota que retorna um objeto JSON de uma receita que tenha o mesmo ID que foi passado na requisição",
    operation_summary="Retorna uma receita com base no ID",
    tags=["Receitas"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class GetRecipeByNameView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
    responses={201: openapi.Response(
                description="Lista de receitas receitas que passaram pelo filtro de nome",
                schema=RecipeSerializer
            )},
    operation_description="Rota que retorna lista de receitas receitas que passaram pelo filtro de nome",
    operation_summary="Buscar receitas pelo titulo",
    tags=["Receitas"]
    )
    def get(self, request, title, *args, **kwargs):
        # Perform a case-insensitive search on the 'title' field using `__icontains`
        queryset = Recipe.objects.filter(title__icontains=title)
        if queryset.exists():
            # Serialize the data and return the results
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Não foram encontradas receitas que contém o nome utilizado."}, status=status.HTTP_404_NOT_FOUND)

class RecipeUpdateView(generics.UpdateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'

    @swagger_auto_schema(
    responses={201: openapi.Response(
                description="Receita atualizada",
                schema=RecipeSerializer
            )},
    operation_description="Rota que permite a atualização dos dados de uma receita pelo ID através do PUT",
    operation_summary="Atualiza uma receita",
    tags=["Receitas"]
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
    responses={201: openapi.Response(
                description="Receita atualizada",
                schema=RecipeSerializer
            )},
    operation_description="Rota que permite a atualização parcial dos dados de uma receita pelo ID através do PATCH",
    operation_summary="Atualiza uma receita",
    tags=["Receitas"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
