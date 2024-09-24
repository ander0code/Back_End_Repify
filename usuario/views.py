from rest_framework.viewsets import ViewSet
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, CustomUserSerializer
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


# Create your views here.
class LoginViewSet(ViewSet):

    @swagger_auto_schema(
        operation_description="User login",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
            },
        ),
        responses={
            200: openapi.Response('Successful login', 
                                  openapi.Schema(
                                      type=openapi.TYPE_OBJECT,
                                      properties={
                                          'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token for authentication'),
                                          'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token for obtaining new access tokens'),
                                          'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the logged-in user'),
                                      }
                                  )),
            400: openapi.Response('Invalid credentials', 
                                  openapi.Schema(
                                      type=openapi.TYPE_OBJECT,
                                      properties={
                                          'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                                      }
                                  )),
        },
        tags=["User Management"]
    )
    @action(detail=False, methods=['POST'],url_path='Login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Register a new user and return JWT tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'university', 'career', 'cycle', 'biography', 'photo', 'achievements', 'first_name', 'last_name'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the user'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the user'),
                'university': openapi.Schema(type=openapi.TYPE_STRING, description='University of the user'),
                'career': openapi.Schema(type=openapi.TYPE_STRING, description='Career of the user'),
                'cycle': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle of the user'),
                'biography': openapi.Schema(type=openapi.TYPE_STRING, description='Biography of the user'),
                'photo': openapi.Schema(type=openapi.TYPE_STRING, description='Photo URL of the user'),
                'achievements': openapi.Schema(type=openapi.TYPE_STRING, description='Achievements of the user'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name of the user'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name of the user'),
            },
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                'User registered successfully and JWT tokens returned',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT, description='User data', properties={
                            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the user'),
                            'university': openapi.Schema(type=openapi.TYPE_STRING, description='University of the user'),
                            'career': openapi.Schema(type=openapi.TYPE_STRING, description='Career of the user'),
                            'cycle': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle of the user'),
                            'biography': openapi.Schema(type=openapi.TYPE_STRING, description='Biography of the user'),
                            'photo': openapi.Schema(type=openapi.TYPE_STRING, description='Photo URL of the user'),
                            'achievements': openapi.Schema(type=openapi.TYPE_STRING, description='Achievements of the user'),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name of the user'),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name of the user'),
                        }),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Invalid input data'),
        },
        tags=["User Management"]
    )
    @action(detail=False, methods=['POST'], url_path='Register')
    def register(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear el usuario en auth_user
        user = User.objects.create_user(username=email, email=email, password=password)


        # Ahora crea la entrada en la tabla Users
        users_data = {
            **request.data,  # Copia todos los datos del request
            'authuser': user.pk,  # Asigna el objeto User recién creado
            'created_at': timezone.now()  # Establece la fecha de creación
        }
        
        users_serializer = CustomUserSerializer(data=users_data)
        
        if users_serializer.is_valid():
            users_serializer.save()  # Guarda la instancia
            
            # Generar el token JWT
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": users_serializer.data  # Retorna los datos del usuario
            }, status=status.HTTP_201_CREATED)
        
        return Response(users_serializer.errors, status=status.HTTP_400_BAD_REQUEST)