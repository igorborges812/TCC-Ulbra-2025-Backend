from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .serializers import (CustomTokenObtainPairSerializer,
                          UserRegistrationSerializer, UserSerializer,
                          UserUpdateSerializer)

User = get_user_model()

class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="Usuário registrado com sucesso",
                schema=UserSerializer()
            ),
            400: "Erro de validação - Usuário não registrado",
        },
        operation_description="Rota para registro de um novo usuário",
        operation_summary="Registrar um novo usuário",
        tags=["Usuários"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        responses={
            200: "Token JWT obtido com sucesso",
            401: "Credenciais inválidas"
        },
        operation_description="Rota para obter o token JWT",
        operation_summary="Obter Token JWT",
        tags=["Autenticação"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        responses={
            200: "Token JWT atualizado com sucesso",
            401: "Token inválido ou expirado"
        },
        operation_description="Rota para atualizar o token JWT",
        operation_summary="Atualizar Token JWT",
        tags=["Autenticação"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Dados do usuário atualizados com sucesso",
                schema=UserUpdateSerializer()
            ),
            400: "Erro de validação - Dados não atualizados"
        },
        operation_description="Rota que permite atualizar os dados do usuário autenticado",
        operation_summary="Atualizar dados do usuário",
        tags=["Usuários"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Dados do usuário atualizados parcialmente com sucesso",
                schema=UserUpdateSerializer()
            ),
            400: "Erro de validação - Dados não atualizados"
        },
        operation_description="Rota que permite atualização parcial dos dados do usuário autenticado",
        operation_summary="Atualizar parcialmente dados do usuário",
        tags=["Usuários"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class DeactivateUserView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @swagger_auto_schema(
        responses={
            204: "Conta desativada com sucesso",
            400: "Erro ao desativar a conta"
        },
        operation_description="Rota que permite desativar a conta do usuário autenticado",
        operation_summary="Desativar conta do usuário",
        tags=["Usuários"]
    )
    def post(self, request, *args, **kwargs):
        user = self.request.user
        user.deactivate_account()
        return Response({"detail": "Conta desativada com sucesso."}, status=status.HTTP_204_NO_CONTENT)