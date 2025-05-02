from django.urls import path
from .views import FavoriteListView, FavoriteCreateView, FavoriteDeleteView

urlpatterns = [
    path('list/', FavoriteListView.as_view(), name='favorite-list'),
    path('add/', FavoriteCreateView.as_view(), name='favorite-add'),
    path('remove/<int:id>/', FavoriteDeleteView.as_view(), name='favorite-remove'),
]
