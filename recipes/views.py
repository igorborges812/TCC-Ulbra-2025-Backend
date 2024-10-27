import base64
import random
import string

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser

from .models import Category, Recipe
from .serializers import CategorySerializer, RecipeSerializer


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
        request_body=RecipeSerializer,
        responses={
            201: openapi.Response(
                description="Objeto contendo dados da receita criada",
                schema=RecipeSerializer()
            ),
            400: "Erro de validação - Receita não criada",
        },
        operation_description="Rota para registro de uma nova receita",
        operation_summary="Cria uma receita",
        tags=["Receitas"]
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        image_base64 = request.data.get('image_base64')

        if image_base64:
            try:
                image_data = ContentFile(
                    base64.b64decode(image_base64),
                    name=f"{''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=30))}.jpg"
                )

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
        responses={
            200: openapi.Response(
                description="Lista de receitas salvas",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        ref='#/components/schemas/RecipeSerializer'
                    )
                )
            ),
        },
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
        responses={
            200: openapi.Response(
                description="Objeto JSON da receita encontrada com base no ID passado",
                schema=RecipeSerializer()
            ),
            404: "Receita não encontrada para o ID fornecido"
        },
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
        manual_parameters=[
            openapi.Parameter(
                'title', openapi.IN_QUERY, description="Nome ou parte do nome da receita",
                type=openapi.TYPE_STRING, required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Lista de receitas que passaram pelo filtro de nome",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        ref='#/components/schemas/RecipeSerializer'
                    )
                )
            ),
            404: "Nenhuma receita encontrada que contenha o nome utilizado"
        },
        operation_description="Rota que retorna lista de receitas que passaram pelo filtro de nome",
        operation_summary="Buscar receitas pelo título",
        tags=["Receitas"]
    )
    def get(self, request, title, *args, **kwargs):
        queryset = Recipe.objects.filter(title__icontains=title)
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Não foram encontradas receitas que contém o nome utilizado."}, status=status.HTTP_404_NOT_FOUND)


class RecipeUpdateView(generics.UpdateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'

    @swagger_auto_schema(
        request_body=RecipeSerializer,
        responses={
            200: openapi.Response(
                description="Receita atualizada",
                schema=RecipeSerializer()
            ),
            400: "Erro de validação - Receita não atualizada"
        },
        operation_description="Rota que permite a atualização dos dados de uma receita pelo ID através do PUT",
        operation_summary="Atualiza uma receita",
        tags=["Receitas"]
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=RecipeSerializer,
        responses={
            200: openapi.Response(
                description="Receita atualizada parcialmente",
                schema=RecipeSerializer()
            ),
            400: "Erro de validação - Receita não atualizada"
        },
        operation_description="Rota que permite a atualização parcial dos dados de uma receita pelo ID através do PATCH",
        operation_summary="Atualiza parcialmente uma receita",
        tags=["Receitas"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class GetCategoryView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)
    queryset = Category.objects.all()

    @swagger_auto_schema(
        operation_description="Rota que lista as categorias cadastradas na tabela auxiliar",
        operation_summary="Lista as categorias existentes",
        tags=["Receitas"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class GetRecipeByCategoryView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'category_id', openapi.IN_PATH, description="ID da categoria",
                type=openapi.TYPE_INTEGER, required=True
            ),
            openapi.Parameter(
                'title', openapi.IN_QUERY, description="Filtrar receitas pelo título dentro da categoria",
                type=openapi.TYPE_STRING, required=False
            )
        ],
        operation_description="Rota que retorna lista de receitas que pertencem a uma categoria específica",
        operation_summary="Buscar receitas por categoria",
        tags=["Receitas"]
    )
    def get(self, request, category_id, *args, **kwargs):
        # Busca receitas pela categoria
        queryset = Recipe.objects.filter(category_id=category_id)

        if not queryset.exists():
            return Response({"detail": "Nenhuma receita encontrada para essa categoria."}, status=status.HTTP_404_NOT_FOUND)

        # Caso seja fornecido um título, filtra dentro das receitas dessa categoria
        title = request.query_params.get('title')
        if title:
            queryset = queryset.filter(title__icontains=title)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SeedCategoriesAndRecipesView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="Cria 5 categorias e 10 receitas para cada categoria.",
        operation_summary="Seed de categorias e receitas",
        responses={
            201: openapi.Response(
                description="Seed de categorias e receitas criada com sucesso.",
                examples={
                    "application/json": {
                        "detail": "Seed de categorias e receitas criada com sucesso."
                    }
                }
            ),
            400: openapi.Response(
                description="Nenhum usuário encontrado para associar às receitas.",
                examples={
                    "application/json": {
                        "detail": "Nenhum usuário encontrado para associar às receitas."
                    }
                }
            )
        },
        tags=["Seed"]
    )
    def get(self, request, *args, **kwargs):
        categories = []
        for i in range(5):
            category_name = f'Categoria {i+1}'
            category, created = Category.objects.get_or_create(name=category_name)
            categories.append(category)

        user = CustomUser.objects.first()
        if not user:
            return Response({"detail": "Nenhum usuário encontrado para associar às receitas."}, status=status.HTTP_400_BAD_REQUEST)

        for category in categories:
            for j in range(10):
                recipe_title = f'Receita {j+1} da {category.name}'
                ingredients = [
                    {"name": f"Ingrediente {k+1}", "quantity": round(random.uniform(1, 5), 2), "unit": "unidade"}
                    for k in range(5)
                ]
                Recipe.objects.create(
                    user=user,
                    title=recipe_title,
                    ingredients=ingredients,
                    text_area=f'Texto da receita {j+1} da {category.name}',
                    category=category
                )

        return Response({"detail": "Seed de categorias e receitas criada com sucesso."}, status=status.HTTP_201_CREATED)
