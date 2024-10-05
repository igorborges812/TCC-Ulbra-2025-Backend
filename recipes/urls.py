from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from .views import (RegisterRecipe, GetRecipes, GetRecipeByName)


urlpatterns = [
    path('recipe/create/', RegisterRecipe.as_view(), name='register'),
    path('recipe/', GetRecipes.as_view(), name='get-recipes'),
    path('recipe/<str:title>/', GetRecipeByName.as_view(), name='get-recipe-by-name'),
]