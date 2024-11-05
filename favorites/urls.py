from django.urls import path
from .views import FavoriteListView, FavoriteCreateView, FavoriteDeleteView

urlpatterns = [
    path('favorites/', FavoriteListView.as_view(), name='favorite-list'),
    path('favorites/add/', FavoriteCreateView.as_view(), name='favorite-add'),
    path('favorites/remove/<uuid:recipe_id>/', FavoriteDeleteView.as_view(), name='favorite-remove'),
]