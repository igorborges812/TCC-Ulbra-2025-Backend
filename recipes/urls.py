from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from .views import (RegisterRecipeView, GetRecipesView, GetRecipeByNameView, RecipeUpdateView)


urlpatterns = [
    path('recipe/create/', RegisterRecipeView.as_view(), name='register'),
    path('recipe/', GetRecipesView.as_view(), name='get-recipes'),
    path('recipe/name/<str:title>/', GetRecipeByNameView.as_view(), name='get-recipe-by-name'),
    path('recipe/edit/<int:id>/', RecipeUpdateView.as_view(), name='recipe-update'),
]