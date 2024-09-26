from rest_framework.viewsets import ViewSet
from django.contrib.auth.models import User
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, CustomUserSerializer
from rest_framework.decorators import action,permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from usuario.models import Users
from rest_framework.permissions import AllowAny ,IsAuthenticated
import random

#acuerdate de que debes usar async y await

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
    @permission_classes([AllowAny])
    def Login(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
    @permission_classes([AllowAny])
    def register(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name") 
        last_name = request.data.get("last_name")  
        
        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear el usuario en auth_user
        user = User.objects.create_user(username=email, email=email, password=password,first_name=first_name, last_name=last_name )


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
    
    @swagger_auto_schema(
            operation_description="Request a password reset code",
            request_body=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['email'],
                properties={
                    'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email to send the reset code'),
                },
            ),
            responses={
                200: openapi.Response('Password reset code sent', 
                                    openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                                    })),
                400: openapi.Response('Invalid email', 
                                    openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                                    })),
            },
            tags=["User Management"]
        )
    @action(detail=False, methods=['POST'], url_path='request-password-reset')
    @permission_classes([IsAuthenticated])
    def request_password_reset(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtener el usuario basado en el correo electrónico
            user = User.objects.get(email=email)

            # Generar un código de 6 dígitos
            reset_code = random.randint(100000, 999999)

            # Almacenar el código y la fecha en el modelo Users
            user_profile = user.users  # Asegúrate de que tienes acceso al perfil del usuario
            user_profile.reset_code = reset_code
            user_profile.reset_code_created_at = timezone.now()
            user_profile.save()

            # Enviar el correo electrónico con el código de restablecimiento
            send_mail(
                'Password Reset Code',
                f'Your password reset code is: {reset_code}',
                'noreply@yourdomain.com',  # Cambia esto por tu dirección de correo
                [email],
                fail_silently=False,
            )

            return Response({"message": "Password reset code sent"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(
        operation_description="Reset user password using a reset code",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'reset_code', 'new_password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'reset_code': openapi.Schema(type=openapi.TYPE_INTEGER, description='Reset code sent to the user'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password for the user'),
            },
        ),
        responses={
            200: openapi.Response('Password successfully reset', 
                                  openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                      'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                                  })),
            400: openapi.Response('Invalid reset code or email', 
                                  openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                      'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                                  })),
        },
        tags=["User Management"]
    )
    @action(detail=False, methods=['POST'], url_path='reset_password')
    @permission_classes([IsAuthenticated])
    def reset_password(self, request):
        email = request.data.get("email")
        reset_code = request.data.get("reset_code")
        new_password = request.data.get("new_password")
        
        try:
            # Obtener el usuario por email desde auth_user
            user = User.objects.get(email=email)
            
            # Obtener el perfil del usuario
            user_profile = Users.objects.get(authuser=user)

            # Verificar si el código de restablecimiento es correcto
            if user_profile.reset_code == reset_code:
                # Cambiar la contraseña
                user.set_password(new_password)
                user.save() 
                
                # Limpiar el código de restablecimiento
                user_profile.reset_code = None
                user_profile.save()  # Guardar los cambios en el perfil
                
                return Response({"message": "Password successfully reset"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid reset code"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)
        except Users.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Update user profile by ID",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'university': openapi.Schema(type=openapi.TYPE_STRING, description='University of the user'),
                'career': openapi.Schema(type=openapi.TYPE_STRING, description='Career of the user'),
                'cycle': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle of the user'),
                'biography': openapi.Schema(type=openapi.TYPE_STRING, description='Biography of the user'),
                'photo': openapi.Schema(type=openapi.TYPE_STRING, description='Photo URL of the user'),
                'achievements': openapi.Schema(type=openapi.TYPE_STRING, description='Achievements of the user'),
            },
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                'User profile updated successfully',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'university': openapi.Schema(type=openapi.TYPE_STRING, description='University of the user'),
                        'career': openapi.Schema(type=openapi.TYPE_STRING, description='Career of the user'),
                        'cycle': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle of the user'),
                        'biography': openapi.Schema(type=openapi.TYPE_STRING, description='Biography of the user'),
                        'photo': openapi.Schema(type=openapi.TYPE_STRING, description='Photo URL of the user'),
                        'achievements': openapi.Schema(type=openapi.TYPE_STRING, description='Achievements of the user'),
                    }
                )
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response('User not found'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Invalid input data'),
        },
        tags=["User Management"]
    )
    @action(detail=True, methods=['PUT'], url_path='update-profile')
    @permission_classes([IsAuthenticated])
    def update_user_profile(self, request, pk=None):
        try:
            # Obtener el perfil de usuario usando el ID (pk)
            user_profile = Users.objects.get(pk=pk)
        except Users.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Crea un serializador con los datos actuales del perfil y los nuevos datos enviados
        serializer = CustomUserSerializer(user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # Guarda las actualizaciones
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Delete a user and their associated auth_user entry by ID",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response('User and auth_user deleted successfully'),
            status.HTTP_404_NOT_FOUND: openapi.Response('User not found'),
        },
        tags=["User Management"]
    )
    @action(detail=True, methods=['DELETE'], url_path='delete-user')
    @permission_classes([IsAuthenticated])
    def delete_user(self, request, pk=None):
        try:
            # Buscar al usuario en la tabla Users por su ID (pk)
            user_profile = Users.objects.get(pk=pk)
            
            # Obtener el usuario en la tabla auth_user
            auth_user = user_profile.authuser  # Asumiendo que 'authuser' es una FK a User

        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Eliminar el perfil del usuario en la tabla personalizada Users
        user_profile.delete()

        # Eliminar el usuario en la tabla auth_user
        auth_user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
