import base64
import string, random
from io import BytesIO
from PIL import Image
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .apps import RecipesConfig
from .models import Recipe
from .serializers import RecipeSerializer, IngredientSerializer
from supabase import create_client, Client
from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.files.uploadedfile import SimpleUploadedFile


class RegisterRecipe(generics.CreateAPIView):
    queryset = Recipe.objects.all()
    # TODO, mudar para IsAuthenticated
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
    def post(self, request, *args, **kwargs):
        # Get base64 string from the request
        base64_image = request.data.get('image_base64')
        if base64_image:
            # Decode the base64 string and create an image file
            try:
                image_data = base64.b64decode(base64_image)
                image = Image.open(BytesIO(image_data)).convert('RGB')
                temp_image = BytesIO()
                #image_format = image.format if image.format else 'PNG' # Default to PNG if format is not provided
                image_format = 'JPEG'
                image.save(temp_image, format=image_format)
                temp_image.seek(0)

                image_name = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=20))
                # Create a SimpleUploadedFile instance for the image
                uploaded_image = SimpleUploadedFile(f"{image_name}.jpg", temp_image.read(), content_type=f"image/{image_format}")

            except Exception as e:
                return Response({"error": f"Failed to process base64 image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Initialize Supabase client
            supabase: Client = create_client(RecipesConfig.supabase_url, RecipesConfig.supabase_key)

            # Upload the image to Supabase storage
            response = supabase.storage.from_("recipes").upload(
                path=f"recipes/{uploaded_image.name}",
                file=uploaded_image.read(),
                file_options={"content-type": f"{uploaded_image.content_type}"}
            )

            if not response.is_success:
                return Response({"error": "Image upload failed"}, status=status.HTTP_400_BAD_REQUEST)

            image_url = str(response.url)
            request.data['image_url'] = image_url
        return super().post(request, *args, **kwargs)

class GetRecipes(generics.ListAPIView):
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

class GetRecipeByName(generics.ListAPIView):
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
            return Response({"error": "No recipes found matching the passed title."}, status=status.HTTP_404_NOT_FOUND)