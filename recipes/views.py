import base64
import random
import string

import httpx

from django.db import transaction
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import Category, Recipe
from .serializers import CategorySerializer, RecipeSerializer

SUPABASE_URL = "https://sizovghaygzecxbgvqvb.supabase.co"
SUPABASE_BUCKET = "receitas"
SUPABASE_KEY = "SUA_CHAVE_ANON"  # Substitua por sua chave pública do Supabase

def upload_image_to_supabase(filename: str, binary_data: bytes) -> str:
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/octet-stream",
    }

    url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}"

    response = httpx.put(url, headers=headers, content=binary_data)

    if response.status_code != 200:
        raise Exception(f"Erro ao fazer upload: {response.text}")

    return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"

# ----------------------------
# CRIAÇÃO DE RECEITA
# ----------------------------

class RegisterRecipeView(generics.CreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Rota para registro de uma nova receita (pode informar categoria existente ou nova).",
        operation_summary="Cria uma receita",
        tags=["Receitas"]
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        image = request.FILES.get('image')

        if image:
            try:
                binary_data = image.read()
                filename = ''.join(random.choices(string.ascii_letters + string.digits, k=30)) + ".jpg"
                image_url = upload_image_to_supabase(filename, binary_data)
                data['image'] = image_url
            except Exception as e:
                raise ValidationError(f"Erro ao subir imagem para o Supabase: {str(e)}")

        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ----------------------------
# LISTAGEM GERAL DE RECEITAS COM FILTROS
# ----------------------------

class GetRecipesView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Busca por título, categoria ou ingrediente", type=openapi.TYPE_STRING)
        ],
        operation_description="Rota que retorna lista com todas as receitas existentes com possibilidade de filtro",
        operation_summary="Lista receitas com filtro",
        tags=["Receitas"]
    )
    def get_queryset(self):
        queryset = Recipe.objects.all()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(category__name__icontains=search) |
                Q(ingredients__icontains=search)
            )
        return queryset

# ----------------------------
# DETALHE POR ID
# ----------------------------

class GetRecipeByIdView(generics.RetrieveAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_description="Rota que retorna uma receita com base no ID",
        operation_summary="Retorna uma receita com base no ID",
        tags=["Receitas"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# ----------------------------
# BUSCA POR TÍTULO
# ----------------------------

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
        operation_description="Filtra receitas pelo título",
        operation_summary="Buscar receitas pelo título",
        tags=["Receitas"]
    )
    def get(self, request, title, *args, **kwargs):
        queryset = Recipe.objects.filter(title__icontains=title)
        if not queryset.exists():
            return Response({"detail": "Nenhuma receita encontrada com esse nome."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ----------------------------
# ATUALIZAÇÃO DE RECEITA
# ----------------------------

class RecipeUpdateView(generics.UpdateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_description="Atualiza todos os campos de uma receita (PUT)",
        operation_summary="Atualiza uma receita",
        tags=["Receitas"]
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Atualiza parcialmente uma receita (PATCH)",
        operation_summary="Atualiza parcialmente uma receita",
        tags=["Receitas"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

# ----------------------------
# LISTAR CATEGORIAS
# ----------------------------

class GetCategoryView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)
    queryset = Category.objects.all()

    @swagger_auto_schema(
        operation_description="Lista as categorias cadastradas",
        operation_summary="Lista categorias",
        tags=["Receitas"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# ----------------------------
# RECEITAS POR CATEGORIA
# ----------------------------

class GetRecipeByCategoryView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('category_id', openapi.IN_PATH, description="ID da categoria", type=openapi.TYPE_INTEGER),
            openapi.Parameter('title', openapi.IN_QUERY, description="Filtro por título", type=openapi.TYPE_STRING, required=False)
        ],
        operation_description="Lista receitas por categoria",
        operation_summary="Buscar receitas por categoria",
        tags=["Receitas"]
    )
    def get(self, request, category_id, *args, **kwargs):
        title = request.query_params.get('title')
        queryset = Recipe.objects.filter(category_id=category_id)
        if title:
            queryset = queryset.filter(title__icontains=title)

        if not queryset.exists():
            return Response({"detail": "Nenhuma receita encontrada para essa categoria."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecipeSerializer(queryset, many=True)
        return Response(serializer.data)

# ----------------------------
# SEED AUTOMÁTICO
# ----------------------------

class SeedCategoriesAndRecipesView(APIView):
    permission_classes = (IsAuthenticated,)

    NUM_CATEGORIES = 5
    NUM_RECIPES_PER_CATEGORY = 10

    @swagger_auto_schema(
        operation_description="Cria 5 categorias e 10 receitas para cada uma.",
        operation_summary="Seed de categorias e receitas",
        tags=["Seed"]
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user:
            return Response({"detail": "Nenhum usuário encontrado para associar às receitas."}, status=status.HTTP_400_BAD_REQUEST)

        categories = []
        for i in range(self.NUM_CATEGORIES):
            name = f'Categoria {i+1}'
            category, _ = Category.objects.get_or_create(name=name)
            categories.append(category)

        for category in categories:
            for j in range(self.NUM_RECIPES_PER_CATEGORY):
                title = f'Receita {j+1} da {category.name}'
                ingredients = [
                    {"name": f"Ingrediente {k+1}", "quantity": round(random.uniform(1, 5), 2), "unit": "unidade"}
                    for k in range(5)
                ]
                Recipe.objects.create(
                    user=user,
                    title=title,
                    ingredients=ingredients,
                    text_area=[f"Passo a passo da receita {j+1} da {category.name}"],
                    category=category
                )

        return Response({"detail": "Seed de categorias e receitas criada com sucesso."}, status=status.HTTP_201_CREATED)

# ----------------------------
# CRIAR NOVA CATEGORIA
# ----------------------------

class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Cria uma nova categoria de receitas.",
        operation_summary="Criar categoria",
        tags=["Receitas"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# ----------------------------
# MINHAS RECEITAS (NOVA VIEW)
# 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_recipes(request):
    user = request.user
    recipes = Recipe.objects.filter(user=user)
    serializer = RecipeSerializer(recipes, many=True)
    return Response(serializer.data)
