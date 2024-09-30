from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from .views import (CustomTokenObtainPairView, CustomTokenRefreshView,
                    DeactivateUserView, RegisterUserView, UserUpdateView)

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('edit/', UserUpdateView.as_view(), name='user_edit'),
    path('deactivate/', DeactivateUserView.as_view(), name='user_deactivate'),
]