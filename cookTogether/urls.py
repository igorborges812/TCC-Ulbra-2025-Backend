from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
   openapi.Info(
      title="CookTogether API",
      default_version='v1',
      description="Documentação da API para o projeto de receitas",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="suporte@cooktogether.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   authentication_classes=[],
)

urlpatterns = [
   path('admin/', admin.site.urls),
   path('api/users/', include('users.urls')),
   path('api/recipes/', include('recipes.urls')),
   path('api/favorites/', include('favorites.urls')),

   # Rotas para documentação Swagger e Redoc
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Adiciona suporte a media files no ambiente de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
