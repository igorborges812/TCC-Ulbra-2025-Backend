import base64
import string, random
from io import BytesIO
from PIL import Image
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .apps import RecipesConfig
from .models import Recipe
from .serializers import RecipeSerializer
from supabase import create_client, Client
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from rest_framework.exceptions import ValidationError


class RegisterRecipeView(generics.CreateAPIView):
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
    @transaction.atomic  # Ensures the entire operation is atomic
    def post(self, request, *args, **kwargs):
        base64_image = request.data.get('image_base64')
        try:
            # Save the recipe without the image_url first
            postResponse = super().post(request, *args, **kwargs)

            if not base64_image:
                return postResponse

            # Decode and process the base64 image
            try:
                image_data = base64.b64decode(base64_image)
                image = Image.open(BytesIO(image_data)).convert('RGB')
                temp_image = BytesIO()
                image_format = 'JPEG'
                image.save(temp_image, format=image_format)
                temp_image.seek(0)
                image_name = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=30))

                # Create a SimpleUploadedFile instance for the image
                uploaded_image = SimpleUploadedFile(f"{image_name}.jpg", temp_image.read(), content_type=f"image/{image_format}")

            except Exception as e:
                raise Exception(f"[ERROR] Failed to process base64 image: {str(e)}")

            supabase: Client = create_client(RecipesConfig.sb_url, RecipesConfig.sb_key)

            response = supabase.storage.from_(RecipesConfig.sb_bucket_name).upload(
                path=f"{RecipesConfig.sb_bucket_path}{uploaded_image.name}",
                file=uploaded_image.read(),
                file_options={"content-type": f"{uploaded_image.content_type}"}
            )

            if not response.is_success:
                return Response({"error": "Image upload to remote bucket failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            image_url = str(response.url)

            # Update the database with the image_url
            recipe = Recipe.objects.get(pk=postResponse.data['id'])  # Get the saved recipe object
            recipe.image_url = image_url
            recipe.save()
            postResponse.data['image_url'] = image_url

        # If anything goes wrong, rollback the transaction
        except ValidationError as e:
            try:
                res = supabase.storage.from_(RecipesConfig.sb_bucket_name).remove(f"{RecipesConfig.sb_bucket_path}{image_name}.jpg")
                if res:
                    print(f"[INFO] Deleted image {image_name}.jpg from remote bucket")
                else:
                    print(f"[INFO] No images named {image_name}.jpg were found in remote bucket for removal")
            except:
                pass

            return Response({"error": str(e)}, status=e.status_code)

        # Catch all for unexpected exceptions
        except Exception as e:
            return Response({"error": str(e)}, status=e.status_code)

        return postResponse

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
            return Response({"error": "No recipes found matching the passed title."}, status=status.HTTP_404_NOT_FOUND)

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