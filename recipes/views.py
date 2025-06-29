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
from .serializers import RecipeSerializer

from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

SUPABASE_URL = "https://sizovghaygzecxbgvqvb.supabase.co"
SUPABASE_BUCKET = "receitas"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpem92Z2hheWd6ZWN4Ymd2cXZiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTYwODYxMywiZXhwIjoyMDY1MTg0NjEzfQ.ErTX-Bj568patz2nDz9DMVsZ-x-DJrTLxDl9OkBPEPI"

def upload_image_to_supabase(filename: str, binary_data: bytes) -> str:
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/octet-stream",
    }
    url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/recipe_images/{filename}"
    response = httpx.put(url, headers=headers, content=binary_data)
    if response.status_code not in (200, 201):
        raise Exception(f"Erro ao fazer upload: {response.text}")
    return f"recipe_images/{filename}"

class RegisterRecipeView(generics.CreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Rota para registro de uma nova receita.",
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
                extension = image.content_type.split("/")[-1] or "jpg"
                filename = ''.join(random.choices(string.ascii_letters + string.digits, k=30)) + f".{extension}"
                stored_path = upload_image_to_supabase(filename, binary_data)
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{stored_path}"
                data['image'] = public_url
            except Exception as e:
                raise ValidationError(f"Erro ao subir imagem para o Supabase: {str(e)}")
        else:
            data['image'] = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/recipe_images/default.png"

        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class GetRecipesView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Busca por título, categoria ou ingrediente", type=openapi.TYPE_STRING)
        ],
        operation_description="Lista receitas com filtro",
        operation_summary="Lista receitas",
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

class GetRecipeByIdView(generics.RetrieveAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_description="Retorna uma receita com base no ID",
        operation_summary="Receita por ID",
        tags=["Receitas"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class GetRecipeByNameView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_QUERY, description="Nome ou parte do nome", type=openapi.TYPE_STRING, required=True)
        ],
        operation_description="Busca receitas pelo título",
        operation_summary="Busca por nome",
        tags=["Receitas"]
    )
    def get(self, request, title, *args, **kwargs):
        queryset = Recipe.objects.filter(title__icontains=title)
        if not queryset.exists():
            return Response({"detail": "Nenhuma receita encontrada com esse nome."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RecipeUpdateView(generics.UpdateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_description="Atualiza todos os campos da receita (PUT)",
        operation_summary="Atualizar receita (PUT)",
        tags=["Receitas"]
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Atualiza parcialmente uma receita (PATCH)",
        operation_summary="Atualizar receita (PATCH)",
        tags=["Receitas"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

class GetCategoryView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)
    queryset = Category.objects.all()

    @swagger_auto_schema(
        operation_description="Lista as categorias cadastradas",
        operation_summary="Listar categorias",
        tags=["Receitas"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class GetRecipeByCategoryView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('category_id', openapi.IN_PATH, description="ID da categoria", type=openapi.TYPE_INTEGER),
            openapi.Parameter('title', openapi.IN_QUERY, description="Filtro por título", type=openapi.TYPE_STRING, required=False)
        ],
        operation_description="Busca receitas por categoria",
        operation_summary="Receitas por categoria",
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

class SeedCategoriesAndRecipesView(APIView):
    permission_classes = (IsAuthenticated,)
    NUM_CATEGORIES = 5
    NUM_RECIPES_PER_CATEGORY = 10

    @swagger_auto_schema(
        operation_description="Cria categorias e receitas fictícias.",
        operation_summary="Criar dados fictícios",
        tags=["Seed"]
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user:
            return Response({"detail": "Usuário não encontrado."}, status=status.HTTP_400_BAD_REQUEST)

        categories = []
        for i in range(self.NUM_CATEGORIES):
            name = f'Categoria {i+1}'
            category, _ = Category.objects.get_or_create(name=name)
            categories.append(category)

        for category in categories:
            for j in range(self.NUM_RECIPES_PER_CATEGORY):
                title = f'Receita {j+1} - {category.name}'
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
        return Response({"detail": "Seed criada com sucesso."}, status=status.HTTP_201_CREATED)

class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Cria uma nova categoria.",
        operation_summary="Criar categoria",
        tags=["Receitas"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_recipes(request):
    user = request.user
    recipes = Recipe.objects.filter(user=user)
    serializer = RecipeSerializer(recipes, many=True)
    return Response(serializer.data)
