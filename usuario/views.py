from adrf.viewsets import ViewSet
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, ProjectSerializerCreate,CustomUserSerializer, ProjectSerializerAll,SolicitudSerializer,ProjectSerializerID,ProjectUpdateSerializer,CollaboratorSerializer,ProjectSerializer, NotificationSerializer,ProfileSerializer, NotificationSerializerMS, FormSerializer, UserAchievementsSerializer,AchievementsSerializer
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from usuario.models import Users,Projects,Solicitudes,Collaborations, Notifications, Forms, Achievements, UserAchievements
from rest_framework.permissions import AllowAny ,IsAuthenticated
import random
import logging
logger = logging.getLogger('your_app_name')  # Cambia esto por el nombre de tu aplicación

from asgiref.sync import sync_to_async

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
    @action(detail=False, methods=['POST'],url_path='Login', permission_classes=[AllowAny])
    async def Login(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if await sync_to_async(serializer.is_valid)(raise_exception=False):
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
                'interests': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING, maxLength=500),
                    description='List of interests of the user (optional)'
                ),
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
                            'authuser': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the associated auth user'),
                            'university': openapi.Schema(type=openapi.TYPE_STRING, description='University of the user'),
                            'career': openapi.Schema(type=openapi.TYPE_STRING, description='Career of the user'),
                            'cycle': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle of the user'),
                            'interests': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Items(type=openapi.TYPE_STRING, maxLength=500),
                                description='List of interests of the user'
                            ),
                            'biography': openapi.Schema(type=openapi.TYPE_STRING, description='Biography of the user'),
                            'photo': openapi.Schema(type=openapi.TYPE_STRING, description='Photo URL of the user'),
                            'achievements': openapi.Schema(type=openapi.TYPE_STRING, description='Achievements of the user'),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, description='Creation date of the user record', format='date'),
                        }),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Invalid input data'),
        },
        tags=["User Management"]
    )
    @action(detail=False, methods=['POST'], url_path='Register', permission_classes=[AllowAny])
    async def register(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name") 
        last_name = request.data.get("last_name")  
        
        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
  
        # Crear el usuario en auth_user
        user = await sync_to_async(User.objects.create_user)(
            username=email, email=email, password=password,first_name=first_name, last_name=last_name 
            )

        # Ahora crea la entrada en la tabla Users
        users_data = {
            **request.data,  # Copia todos los datos del request
            'authuser': user.pk,  # Asigna el objeto User recién creado
            'created_at': timezone.now().strftime('%Y-%m-%d')  # Establece la fecha de creación
        }
        
        users_serializer = CustomUserSerializer(data=users_data)
        
        if await sync_to_async(users_serializer.is_valid)(raise_exception=False):
            await sync_to_async(users_serializer.save)()  # Guarda la instancia
            
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
    @action(detail=False, methods=['POST'], url_path='request-password-reset', permission_classes=[AllowAny])
    async def request_password_reset(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtener el usuario basado en el correo electrónico
            user = await sync_to_async(User.objects.get)(email=email)

            # Generar un código de 6 dígitos
            reset_code = random.randint(100000, 999999)

            # Almacenar el código y la fecha en el modelo Users
            user_profile = await sync_to_async(Users.objects.get)(authuser=user) # Asegúrate de que tienes acceso al perfil del usuario
            user_profile.reset_code = reset_code
            user_profile.reset_code_created_at = timezone.now()
            await sync_to_async(user_profile.save)()

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
    @action(detail=False, methods=['POST'], url_path='reset_password', permission_classes=[AllowAny])
    async def reset_password(self, request):
        email = request.data.get("email")
        reset_code = request.data.get("reset_code")
        new_password = request.data.get("new_password")
        
        try:
            # Obtener el usuario por email desde auth_user
            user = await sync_to_async(User.objects.get)(email=email)
            
            # Obtener el perfil del usuario
            user_profile = await sync_to_async(Users.objects.get)(authuser=user)

            # Verificar si el código de restablecimiento es correcto
            if user_profile.reset_code == reset_code:
                # Cambiar la contraseña
                user.set_password(new_password)
                await sync_to_async(user.save)() 
                
                # Limpiar el código de restablecimiento
                user_profile.reset_code = None
                await sync_to_async(user_profile.save)()  # Guardar los cambios en el perfil
                
                return Response({"message": "Password successfully reset"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid reset code"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)
        except Users.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a user and their associated auth_user entry by ID",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user to view'),
            },
        ),
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response('User and auth_user deleted successfully'),
            status.HTTP_404_NOT_FOUND: openapi.Response('User not found'),
        },
        tags=["User Management"]
    )
    @action(detail=False, methods=['DELETE'], url_path='delete-user', permission_classes=[IsAuthenticated])
    async def delete_user(self, request):

        user_id = request.data.get('id')
        try:
            # Buscar al usuario en la tabla Users por su ID (pk)
            user_profile = await sync_to_async(Users.objects.get)(pk=user_id)
            
            # Obtener el usuario en la tabla auth_user
            auth_user = user_profile.authuser  # Asumiendo que 'authuser' es una FK a User

        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Eliminar el perfil del usuario en la tabla personalizada Users
        await sync_to_async(user_profile.delete)()

        # Eliminar el usuario en la tabla auth_user
        await sync_to_async(auth_user.delete)()

        return Response(status=status.HTTP_204_NO_CONTENT)
 
class PerfilViewSet(ViewSet):
    
    @swagger_auto_schema(
        method='post',
        operation_summary="Retrieve Profile Data",
        operation_description="Retrieve the profile data of the authenticated user.",
        responses={
            200: openapi.Response(
                description="Successful response with user profile data.",
                schema=ProfileSerializer()
            ),
            404: openapi.Response(description="User profile not found.")
        },
        tags = ["Profile Management"]
    )
    @action(detail=False, methods=['POST'], url_path='profile', permission_classes=[IsAuthenticated])
    async def profile_data(self, request):
        user_id = request.user.id

        try:
            user_profile = await sync_to_async(Users.objects.get)(authuser_id=user_id)
            auth_user = request.user

            # Reunir los datos para serializar
            profile_data = {
                "university": user_profile.university,
                "career": user_profile.career,
                "cycle": user_profile.cycle,
                "biography": user_profile.biography,
                "interests": user_profile.interests,
                "photo": user_profile.photo,
                "achievements": user_profile.achievements,
                "created_at": user_profile.created_at,
                # Datos de authuser
                "email": auth_user.email,
                "first_name": auth_user.first_name,
                "last_name": auth_user.last_name,
                "date_joined": auth_user.date_joined,
            }

            serializer = ProfileSerializer(profile_data)
            return Response(serializer.data, status=200)

        except Users.DoesNotExist:
            return Response({"error": "User profile not found"}, status=404)

    @swagger_auto_schema(
        operation_description="Update user profile by ID. Accepts various fields such as university, career, cycle, biography, interests, photo, achievements, and created_at.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user to view'),
                'university': openapi.Schema(type=openapi.TYPE_STRING, description='University of the user'),
                'career': openapi.Schema(type=openapi.TYPE_STRING, description='Career of the user'),
                'cycle': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle of the user'),
                'biography': openapi.Schema(type=openapi.TYPE_STRING, description='Biography of the user'),
                'interests': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING, maxLength=500),
                    description='List of user interests (maximum 500 characters each)'
                ),
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
                        'interests': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING, maxLength=500),
                            description='List of user interests'
                        ),
                        'photo': openapi.Schema(type=openapi.TYPE_STRING, description='Photo URL of the user'),
                        'achievements': openapi.Schema(type=openapi.TYPE_STRING, description='Achievements of the user'),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, description='Profile creation date, format YYYY-MM-DD')
                    }
                )
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response('User not found'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Invalid input data'),
        },
        tags=["Profile Management"]
    )
    @action(detail=False, methods=['PUT'], url_path='update-profile',permission_classes=[IsAuthenticated])
    async def update_user_profile(self, request):

        user_id = request.data.get('id')
        try:
            # Obtener el perfil de usuario usando el ID (pk)
            user_profile = await sync_to_async(Users.objects.get)(pk=user_id)
        except Users.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Crea un serializador con los datos actuales del perfil y los nuevos datos enviados
        serializer = CustomUserSerializer(user_profile, data=request.data, partial=True)

        if await sync_to_async(serializer.is_valid)():
            await sync_to_async(serializer.save)()  # Guarda las actualizaciones
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PublicacionViewSet(ViewSet):
     
    @swagger_auto_schema(
        operation_description="Create a new project",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'description', 'project_type', 'priority'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the project'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the project'),
                'end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='End date of the project'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Current status of the project'),
                'project_type': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="List of project types"
                ),
                'priority': openapi.Schema(type=openapi.TYPE_STRING, description='Priority level of the project'),
                'detailed_description': openapi.Schema(type=openapi.TYPE_STRING, description='Detailed description of the project'),
                'objectives': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description='List of objectives for the project'
                ),
                'necessary_requirements': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description='List of necessary requirements for the project'
                ),
                'progress': openapi.Schema(type=openapi.TYPE_INTEGER, description='Progress percentage of the project'),
                'accepting_applications': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indicates if the project is accepting applications'),
                'type_aplyuni': openapi.Schema(type=openapi.TYPE_STRING, description='Specifies application type (e.g., university-restricted or open to all)'),
            },
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                'Project created successfully',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the created project'),
                        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the project'),
                        'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the project'),
                        'start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Start date of the project'),
                        'end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='End date of the project'),
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Current status of the project'),
                        'project_type': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            description="List of project types"
                        ),
                        'priority': openapi.Schema(type=openapi.TYPE_STRING, description='Priority level of the project'),
                        'responsible': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user responsible for the project'),
                        'detailed_description': openapi.Schema(type=openapi.TYPE_STRING, description='Detailed description of the project'),
                        'objectives': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            description='List of objectives for the project'
                        ),
                        'necessary_requirements': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            description='List of necessary requirements for the project'
                        ),
                        'progress': openapi.Schema(type=openapi.TYPE_INTEGER, description='Progress percentage of the project'),
                        'accepting_applications': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indicates if the project is accepting applications'),
                        'type_aplyuni': openapi.Schema(type=openapi.TYPE_STRING, description='Application type for the project'),
                        'creator_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the project creator'),
                        'collaboration_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Count of collaborations on the project'),
                        'collaborators': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            description="List of collaborator names"
                        ),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Invalid input data'),
        },
        tags=["CRUD Project Management"]
    )
    @action(detail=False, methods=['POST'], url_path='create_proyect', permission_classes=[IsAuthenticated])
    async def create_project(self, request):
        responsible_user_id = request.user.id
        logger.debug("Creating project for user ID: %s", responsible_user_id)

        # Obtener el perfil del usuario de manera asíncrona
        try:
            custom_user = await sync_to_async(Users.objects.get)(authuser=responsible_user_id)
            logger.debug("User profile retrieved: %s", custom_user)
        except Users.DoesNotExist:
            logger.error("User profile not found for user ID: %s", responsible_user_id)
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Crear el proyecto con los datos del request
        project_data = request.data
        project_data['start_date'] = timezone.now().strftime('%Y-%m-%d')
        project_data['name_uniuser'] = custom_user.university if custom_user.university else ""
        project_data['responsible'] = responsible_user_id

        # Serializar y validar los datos del proyecto
        project_serializer = ProjectSerializerCreate(data=project_data)
        if await sync_to_async(project_serializer.is_valid)():
            project = await sync_to_async(project_serializer.save)()
            logger.debug("Project created successfully: %s", project)

            # Calcular creator_name de forma asíncrona
            creator_name = await self.get_creator_name_create_project(responsible_user_id)

            # Contar las colaboraciones de forma asíncrona
            collaboration_count = await self.count_collaborations(project)

            # Obtener los nombres de los colaboradores de forma asíncrona
            collaborators = await self.get_collaborators(project)

            # Construir la respuesta final
            response_data = {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'start_date': project.start_date.isoformat(),
                'end_date': project.end_date.isoformat() if project.end_date else None,
                "status": project.status,
                "project_type": project.project_type ,
                "priority":project.priority,
                "detailed_description":project.detailed_description,
                "accepting_applications":project.accepting_applications,
                "objectives":project.objectives,
                "necessary_requirements":project.necessary_requirements,
                "progress":project.progress,
                "type_aplyuni":project.type_aplyuni,
                'name_uniuser': project.name_uniuser,
                'responsible': responsible_user_id,
                'creator_name': creator_name,
                'collaboration_count': collaboration_count,
                'collaborators': collaborators,
                'status': project.status,
            }
            

            logger.debug("Response data for created project: %s", response_data)
            return Response(response_data, status=status.HTTP_201_CREATED)

        logger.error("Project serializer errors: %s", project_serializer.errors)
        return Response(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    async def get_creator_name_create_project(self, responsible_user_id):
        try:
            auth_user = await sync_to_async(User.objects.get)(id=responsible_user_id)
            return f"{auth_user.first_name} {auth_user.last_name}"
        except User.DoesNotExist:
            logger.error("Auth user not found for ID: %s", responsible_user_id)
            return "Unknown"

    async def count_collaborations(self, project):
        count = await sync_to_async(Collaborations.objects.filter(project=project).count)()
        logger.debug("Collaboration count for project ID %s: %d", project.id, count)
        return count

    async def get_collaborators(self, project):
        collaborators_qs = await sync_to_async(lambda: list(Collaborations.objects.filter(project=project).select_related('user__authuser')))()
        collaborators = [
            f"{collab.user.authuser.first_name} {collab.user.authuser.last_name}"
            for collab in collaborators_qs if collab.user and collab.user.authuser
        ]
        logger.debug("Collaborators retrieved for project ID %s: %s", project.id, collaborators)
        return collaborators

    @swagger_auto_schema(
        operation_description="Actualizar un proyecto específico pasando el ID y los datos del proyecto en el cuerpo de la solicitud",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'project_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del proyecto'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del proyecto'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción del proyecto'),
                'start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='Fecha de inicio del proyecto'),
                'end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='Fecha de finalización del proyecto'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Estado actual del proyecto'),
                'project_type': openapi.Schema(type=openapi.TYPE_STRING, description='Tipo de proyecto'),
                'priority': openapi.Schema(type=openapi.TYPE_STRING, description='Nivel de prioridad del proyecto'),
                'responsible': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del usuario responsable del proyecto'),
                'detailed_description': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción detallada del proyecto'),
                'type_aplyuni': openapi.Schema(type=openapi.TYPE_STRING, description='Tipo de aplicación (universidad restringida o abierta)'),
                'objectives': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description='Lista de objetivos del proyecto'
                ),
                'necessary_requirements': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description='Lista de requisitos necesarios para el proyecto'
                ),
                'progress': openapi.Schema(type=openapi.TYPE_INTEGER, description='Porcentaje de progreso del proyecto'),
                'accepting_applications': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indica si el proyecto acepta solicitudes'),
                'name_uniuser': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de la universidad del usuario responsable'),
            },
            required=['project_id']
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                'Proyecto actualizado correctamente',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'project_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del proyecto actualizado'),
                        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del proyecto'),
                        'description': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción del proyecto'),
                        'start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='Fecha de inicio'),
                        'end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='Fecha de finalización'),
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Estado del proyecto'),
                        'project_type': openapi.Schema(type=openapi.TYPE_STRING, description='Tipo de proyecto'),
                        'priority': openapi.Schema(type=openapi.TYPE_STRING, description='Prioridad del proyecto'),
                        'responsible': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del usuario responsable'),
                        'detailed_description': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción detallada'),
                        'type_aplyuni': openapi.Schema(type=openapi.TYPE_STRING, description='Tipo de aplicación'),
                        'objectives': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            description='Lista de objetivos'
                        ),
                        'necessary_requirements': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            description='Lista de requisitos necesarios'
                        ),
                        'progress': openapi.Schema(type=openapi.TYPE_INTEGER, description='Porcentaje de progreso del proyecto'),
                        'accepting_applications': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indica si se aceptan solicitudes'),
                        'name_uniuser': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de la universidad asociada al usuario responsable'),
                    },
                ),
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response('Proyecto no encontrado'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Datos inválidos'),
        },
        tags=["CRUD Project Management"]
    )
    @action(detail=False, methods=['PUT'], url_path='update-project', permission_classes=[IsAuthenticated])
    async def update_project(self, request):
        # Extraer el ID del proyecto del cuerpo de la solicitud
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({"message": "ID del proyecto es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener la instancia del usuario autenticado
        user_instance = request.user.id

        # Buscar el proyecto por su ID y verificar que el responsable es el usuario autenticado
        project = await sync_to_async(get_object_or_404)(Projects, id=project_id, responsible=user_instance)

        # Serializar los datos de actualización
        serializer = ProjectUpdateSerializer(project, data=request.data, partial=True)
        if await sync_to_async(serializer.is_valid)():
            await sync_to_async(serializer.save)()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a project by ID",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the project to view'),
            },
        ),
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response('Project deleted successfully'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Project not found'),
        },
        tags=["CRUD Project Management"]
    )
    @action(detail=False, methods=['delete'], url_path='delete_project', permission_classes=[IsAuthenticated])
    async def delete_project(self, request):
        try:
            # Obtener el proyecto usando el ID (pk)
            project_id = request.data.get('id')
            project = await sync_to_async(Projects.objects.get)(pk=project_id)
            await sync_to_async(project.delete)()  # Elimina el proyecto
            return Response(status=status.HTTP_204_NO_CONTENT)  # Respuesta sin contenido
        except Projects.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_description="View project details by ID",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the project to view'),
            },
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                'Project details retrieved successfully',
                ProjectSerializerID,
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response('Project not found'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Invalid input data'),
        },
        tags=["CRUD Project Management"]
    )
    @action(detail=False, methods=['POST'], url_path='view_project_id', permission_classes=[IsAuthenticated])
    async def view_project_id(self, request):

        project_id = request.data.get('id')
        user_id = request.user.id  # Obtiene el ID del usuario autenticado

        if not project_id:

            return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
        try:
            project = await sync_to_async(Projects.objects.get)(pk=project_id)
        except Projects.DoesNotExist:

            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        creator_name = await self.get_creator_name_view_project_id(project)
        collaboration_count = await self.get_collaboration_count_view_project_id(project)
        has_applied = await self.get_has_applied(user_id, project)

        response_data = {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'start_date': project.start_date.isoformat(),
            'end_date': project.end_date.isoformat() if project.end_date else None,
            'status': project.status,
            'project_type': project.project_type,
            'priority': project.priority,
            'responsible': project.responsible.id if project.responsible else None,
            'name_uniuser': project.name_uniuser,
            'detailed_description': project.detailed_description,
            'necessary_requirements': project.necessary_requirements,
            'progress': project.progress,
            'objectives': project.objectives,
            'accepting_applications': project.accepting_applications,
            'type_aplyuni': project.type_aplyuni,
            'creator_name': creator_name,
            'collaboration_count': collaboration_count,
            'has_applied': has_applied,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    async def get_creator_name_view_project_id(self, obj):

        if obj.responsible_id: 
            authuser = await sync_to_async(User.objects.get)(id=obj.responsible_id)
            if authuser:
                return f"{authuser.first_name} {authuser.last_name}"
        return None

    async def get_collaboration_count_view_project_id(self, obj):
        count = await sync_to_async(Collaborations.objects.filter(project=obj).count)()
        return count
    
    async def get_has_applied(self, user_id, project):
        try:
            project_responsible = await sync_to_async(lambda: project.responsible)()
        except Exception:
            return False
        if project_responsible is not None:
            try:
                responsible_user = await sync_to_async(Users.objects.get)(id=project_responsible)
                if responsible_user and responsible_user.authuser is not None:
                    responsible_user_id = responsible_user.authuser.id
                    return responsible_user_id == user_id
            except Users.DoesNotExist:
                return False
            except Exception:
                return False
    
    @swagger_auto_schema(
        operation_description="Retrieve all projects in ascending order by start date",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="List of projects in ascending order",
                schema=ProjectSerializerAll(many=True)
            ),
            status.HTTP_400_BAD_REQUEST: "Invalid request",
        },
        tags=["CRUD Project Management"]
    )
    @action(detail=False, methods=['GET'], url_path='view_project_all', permission_classes=[IsAuthenticated])
    async def view_project_all(self, request):
        try:
            # Obtener todos los proyectos de forma asíncrona
            projects = await sync_to_async(list)(Projects.objects.all().order_by('-id'))

            project_data = []
            for project in projects:
                # Obtiene el nombre del creador y el conteo de colaboraciones de forma asíncrona
                creator_name = await self.get_creator_name(project)

                collaboration_count = await self.get_collaboration_count(project)

                # Agrega los datos al diccionario
                project_dict = {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'start_date': project.start_date,
                    'end_date': project.end_date,
                    'status': project.status,
                    'project_type': project.project_type,
                    'priority': project.priority,
                    'responsible': project.responsible_id,
                    'name_uniuser': project.name_uniuser,
                    'detailed_description': project.detailed_description,
                    'progress': project.progress,
                    'accepting_applications': project.accepting_applications,
                    'type_aplyuni': project.type_aplyuni,
                    'creator_name': creator_name,
                    'collaboration_count': collaboration_count,
                }
                project_data.append(project_dict)

            return Response(project_data, status=status.HTTP_200_OK)

        except Exception as e:

            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Retrieve the 3 most recent projects in descending order by start date",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="List of the 3 most recent projects",
                schema=ProjectSerializerAll(many=True)
            ),
            status.HTTP_400_BAD_REQUEST: "Invalid request",
        },
        tags=["CRUD Project Management"]
    )
    @action(detail=False, methods=['GET'], url_path='view_recent_projects', permission_classes=[IsAuthenticated])
    async def view_recent_projects(self, request):
 
        try:
            # Obtener todos los proyectos de forma asíncrona
            projects = await sync_to_async(list)(Projects.objects.all().order_by('-id')[:3])

            project_data = []
            for project in projects:
                # Obtiene el nombre del creador y el conteo de colaboraciones de forma asíncrona
                creator_name = await self.get_creator_name(project)

                collaboration_count = await self.get_collaboration_count(project)

                # Agrega los datos al diccionario
                project_dict = {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'start_date': project.start_date,
                    'end_date': project.end_date,
                    'status': project.status,
                    'project_type': project.project_type,
                    'priority': project.priority,
                    'responsible': project.responsible_id,
                    'name_uniuser': project.name_uniuser,
                    'detailed_description': project.detailed_description,
                    'progress': project.progress,
                    'accepting_applications': project.accepting_applications,
                    'type_aplyuni': project.type_aplyuni,
                    'creator_name': creator_name,
                    'collaboration_count': collaboration_count,
                }
                project_data.append(project_dict)

            return Response(project_data, status=status.HTTP_200_OK)

        except Exception as e:

            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
           
    async def get_creator_name(self, obj):
        if obj.responsible_id: 
            authuser = await sync_to_async(User.objects.get)(id=obj.responsible_id)
            if authuser:
                return f"{authuser.first_name} {authuser.last_name}"
        return None

    async def get_collaboration_count(self, obj):
        count = await sync_to_async(Collaborations.objects.filter(project=obj).count)()
        return count
                   
           
    @swagger_auto_schema(
        operation_description="Aplicar a un proyecto",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['project_id'],
            properties={
                'project_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del proyecto'),
                
            }
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                'Solicitud y notificación creadas exitosamente',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'solicitud': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id_user': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del usuario que aplicó'),
                                'id_project': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del proyecto'),
                                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Estado de la solicitud'),
                            }
                        ),
                        'notificación': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del usuario que recibe la notificación'),
                                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de la notificación'),
                                'is_read': openapi.Schema(type=openapi.TYPE_INTEGER, description='Estado de lectura de la notificación (0 o 1)'),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Fecha de creación de la notificación'),
                            }
                        )
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Error en los datos proporcionados'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Proyecto no encontrado'),
        },
        tags=["Notificacions Project Management"]
    )
    @action(detail=False, methods=['POST'], url_path='ApplyProject', permission_classes=[IsAuthenticated])
    async def ApplyProject(self, request):
        project_id = request.data.get('project_id')
        user = request.user
        

        try:
            # Verificar si el proyecto acepta aplicaciones
            project = await sync_to_async(Projects.objects.get)(id=project_id)
            if not project.accepting_applications:
                return Response({"error": "Este proyecto no está aceptando aplicaciones"}, status=status.HTTP_400_BAD_REQUEST)

            # Verificar si ya existe una solicitud para este proyecto y usuario
            existing_solicitud = await sync_to_async(Solicitudes.objects.filter(id_user=user.id, id_project=project_id).first)()
            if existing_solicitud:
                return Response({"error": "Ya has aplicado a este proyecto."}, status=status.HTTP_400_BAD_REQUEST)

            # Obtener el ID del líder del proyecto (responsible)
            lider_id = project.responsible_id  # Suponiendo que el campo 'responsible' es un ForeignKey

            # Conectar con la tabla auth_user para obtener los datos del líder
            lider = await sync_to_async(User.objects.get)(id=lider_id)  # auth_user se mapea al modelo 'User' de Django

            # Obtener el nombre completo del líder
            name_lider = f"{lider.first_name} {lider.last_name}"

            # Crear la solicitud
            solicitud_data = {
                'id_user': user.id,
                'name_lider': name_lider,
                'created_at': timezone.now().strftime('%Y-%m-%d'),
                'id_project': project.id,
                'status': 'Pendiente',
                'name_project': project.name,
                'name_user': f"{user.first_name} {user.last_name}",
            }

            solicitud_serializer = SolicitudSerializer(data=solicitud_data)

            if await sync_to_async(solicitud_serializer.is_valid)():
                await sync_to_async(solicitud_serializer.save)()
             
                # Crear la notificación para el propietario del proyecto
                notification_data = {
                    'sender': user.id,  
                    'message': f"{user.first_name} {user.last_name} aplico al proyecto '{project.name}' ",
                    'is_read': 0,
                    'created_at': timezone.now(),
                    'user_id': lider_id
                }
                notification_serializer = NotificationSerializer(data=notification_data)
                
                if await sync_to_async(notification_serializer.is_valid)():
                    await sync_to_async(notification_serializer.save)()
                else:
                    return Response(notification_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                return Response(solicitud_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(solicitud_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Projects.DoesNotExist:
            return Response({"error": "Proyecto no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "Líder del proyecto no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Aceptar solicitud de un proyecto",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id_solicitud'],
            properties={
                'id_solicitud': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de la solicitud'),
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Response('Solicitud aceptada exitosamente'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Error en los datos proporcionados'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Solicitud no encontrada'),
        },
        tags=["Notificacions Project Management"]
    )
    @action(detail=False, methods=['POST'], url_path='AcceptProject',permission_classes=[IsAuthenticated])
    async def AcceptProject(self, request):
        id_solicitud = request.data.get('id_solicitud')
        user = request.user
        try:
            solicitud = await sync_to_async(Solicitudes.objects.select_related('id_project', 'id_user').get)(id_solicitud=id_solicitud)

            project_responsible_id = solicitud.id_project

            project_responsible_user_id = await sync_to_async(lambda: project_responsible_id.responsible)()

            if project_responsible_user_id.id != user.id:
                return Response({"error": "No tienes permiso para aceptar esta solicitud"}, status=status.HTTP_403_FORBIDDEN)
            
            solicitud.status = 'Aceptada'
            await sync_to_async(solicitud.save)()

            collaboration_data = {
                'user': solicitud.id_user.id,
                'project': solicitud.id_project.id,
                'status': 'Activa'
            }
            collaboration_serializer = CollaboratorSerializer(data=collaboration_data)
            
            if await sync_to_async(collaboration_serializer.is_valid)():
                await sync_to_async(collaboration_serializer.save)()
                # Crear la notificación para el usuario que aplicó al proyecto
                notification_data = {
                    'sender': user.id,  # El usuario que acepta la solicitud
                    'message': f"Tu solicitud al proyecto '{solicitud.id_project.name}' ha sido aceptada.",
                    'is_read': 0,
                    'created_at': timezone.now(),
                    'user_id': solicitud.id_user.id  # Usuario que aplicó al proyecto
                }
                notification_serializer = NotificationSerializer(data=notification_data)
                
                if await sync_to_async(notification_serializer.is_valid)():
                    await sync_to_async(notification_serializer.save)()
                else:
                    return Response(notification_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({"mensaje": "Solicitud aceptada y colaboración creada exitosamente"}, status=status.HTTP_200_OK)
            else:
                return Response(collaboration_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Solicitudes.DoesNotExist:
            return Response({"error": "Solicitud no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Negar solicitud de un proyecto",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['solicitud_id'],
            properties={
                'solicitud_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de la solicitud'),
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Response('Solicitud negada exitosamente'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Error en los datos proporcionados'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Solicitud no encontrada'),
        },
        tags=["Notificacions Project Management"]
    )
    @action(detail=False, methods=['POST'], url_path='Denyproject',permission_classes=[IsAuthenticated])
    async def Denyproject(self, request):
        solicitud_id = request.data.get('solicitud_id')
        user = request.user
        try:
            solicitud = await sync_to_async(Solicitudes.objects.select_related('id_project', 'id_user').get)(id_solicitud=solicitud_id)

            project_responsible_id = solicitud.id_project

            project_responsible_user_id = await sync_to_async(lambda: project_responsible_id.responsible)()

            if project_responsible_user_id.id != user.id:
                return Response({"error": "No tienes permiso para aceptar esta solicitud"}, status=status.HTTP_403_FORBIDDEN)
            
            # Cambiar el estado de la solicitud a 'Negada'
            solicitud.status = 'Rechazado'
            await sync_to_async(solicitud.save)()
            
             # Crear la notificación para el usuario que aplicó al proyecto
            notification_data = {
                'sender': user.id,  # Usuario responsable del proyecto que rechaza la solicitud
                'message': f"Tu solicitud al proyecto '{solicitud.id_project.name}' ha sido rechazada.",
                'is_read': 0,
                'created_at': timezone.now(),
                'user_id': solicitud.id_user.id  # Usuario que aplicó al proyecto
            }
            notification_serializer = NotificationSerializer(data=notification_data)
            
            if await sync_to_async(notification_serializer.is_valid)():
                await sync_to_async(notification_serializer.save)()
            else:
                return Response(notification_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"mensaje": "Solicitud negada exitosamente"}, status=status.HTTP_200_OK)
        
        except Solicitudes.DoesNotExist:
            return Response({"error": "Solicitud no encontrada"}, status=status.HTTP_404_NOT_FOUND)  
    
    @swagger_auto_schema(
        operation_description="Obtener todas las notificaciones del usuario logueado",
        responses={
            status.HTTP_200_OK: openapi.Response('Lista de notificaciones obtenida exitosamente'),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('Usuario no autorizado'),
        },
        tags=["Notificacions  Management"]
    )
    @action(detail=False, methods=['GET'], url_path='GetNotifications', permission_classes=[IsAuthenticated])
    async def GetNotifications(self, request):
        user = request.user
        
        try:
            # Obtener todas las notificaciones del usuario logueado
            notifications = await sync_to_async(list)(Notifications.objects.filter(user_id=user.id).order_by('-id'))

            # Serializar solo los mensajes de las notificaciones
            serializer = NotificationSerializerMS(notifications, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Notifications.DoesNotExist:
            return Response({"error": "No se encontraron notificaciones"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Retrieve all applications (solicitudes) submitted by the logged-in user.",
        responses={
            status.HTTP_200_OK: openapi.Response(
                'User applications retrieved successfully',
                openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_OBJECT, description="List of applications for the user.", properties={
                        'id_solicitud': openapi.Schema(type=openapi.TYPE_INTEGER, description='Solicitud ID'),
                        'id_project': openapi.Schema(type=openapi.TYPE_INTEGER, description='Project ID'),
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Current status of the application'),
                        # Agrega otros campos relevantes aquí
                    })
                )
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response('No applications found for this user'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal server error')
        },
        tags=["Notificacions Management"]
    )
    @action(detail=False, methods=['GET'], url_path='solicitudes_user', permission_classes=[IsAuthenticated])
    async def get_solicitudes_user(self, request):
        user = request.user.id  
        
        try:
                # Filtrar todas las solicitudes hechas por el usuario autenticado
                solicitudes = await sync_to_async(list)(Solicitudes.objects.filter(id_user=user).order_by("-id_solicitud"))

                # Verificar si el usuario tiene solicitudes
                if not solicitudes:
                    return Response({"message": "No solicitudes found for this user"}, status=status.HTTP_404_NOT_FOUND)

                # Serializar las solicitudes
                serializer = await sync_to_async(SolicitudSerializer)(solicitudes, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @swagger_auto_schema(
    operation_description="Retrieve all applications (solicitudes) for a specific project.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['project_id'],
        properties={
            'project_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the project")
        }
    ),
    responses={
        status.HTTP_200_OK: openapi.Response(
            'Project applications retrieved successfully',
            openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_OBJECT, description="List of applications for the project.")
            )
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response('project_id is required'),
        status.HTTP_404_NOT_FOUND: openapi.Response('Project not found'),
        status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response('Internal server error')
    },
    tags=["Notificacions  Management"]
    )        
    @action(detail=False, methods=['POST'], url_path='solicitudes_project', permission_classes=[IsAuthenticated])
    async def get_solicitudes_project(self, request):
        project_id = request.data.get('project_id')

        if not project_id:
            return Response({"error": "project_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verificar si el proyecto existe
            project = await sync_to_async(Projects.objects.get)(id=project_id)
            
            # Filtrar solicitudes por proyecto
            solicitudes = await sync_to_async(list)(Solicitudes.objects.filter(id_project=project).order_by("-id_solicitud"))
            
            # Serializar las solicitudes
            serializer = await sync_to_async(SolicitudSerializer)(solicitudes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Projects.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['DELETE'], url_path='delete_solicitud', permission_classes=[IsAuthenticated])
    async def delete_solicitud(self, request):
        solicitud_id = request.data.get('solicitud_id')
        user = request.user.id  

        if not solicitud_id:
            return Response({"error": "solicitud_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verificar si la solicitud existe y pertenece al usuario autenticado
            solicitud = await sync_to_async(Solicitudes.objects.get)(id_solicitud=solicitud_id, id_user=user)

            # Verificar si la solicitud ha sido rechazada o no
            if solicitud.status in ['Rechazado', 'Pendiente']:
                # Si la solicitud está pendiente o ha sido rechazada, se permite eliminarla
                await sync_to_async(solicitud.delete)()
                return Response({"message": "Solicitud deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Cannot delete a solicitud that has been accepted or is in another status"}, status=status.HTTP_400_BAD_REQUEST)

        except Solicitudes.DoesNotExist:
            return Response({"error": "Solicitud not found or does not belong to the user"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #--------------------------------------------

    @swagger_auto_schema(
        operation_description="Obtener proyectos creados por el usuario autenticado",
        responses={
            status.HTTP_200_OK: openapi.Response('Lista de proyectos creados por el usuario'),
            status.HTTP_404_NOT_FOUND: openapi.Response('No se encontraron proyectos'),
        },
        tags=["CRUD Project Management"]
    )
    @action(detail=False, methods=['GET'], url_path='my-projects', permission_classes=[IsAuthenticated])
    async def view_project_usercreator(self, request):
        user_id = request.user.id  

        projects = await sync_to_async(list)(Projects.objects.filter(responsible=user_id))

        if projects:
            response_data = []
            for project in projects:
                collaboratorsall = await sync_to_async(list)(Collaborations.objects.filter(project=project).select_related('user__authuser'))
                
                collaborators_info = await self.get_collaborators_info_proyect(collaboratorsall)

                name_responsible = await self.get_responsible_name_proyect(project)

                collaboration_count = await self.get_collaboration_count_proyect(project)

                project_data = {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'start_date': project.start_date,
                    'end_date': project.end_date,
                    'status': project.status,
                    'project_type': project.project_type,
                    'priority': project.priority,
                    'responsible': project.responsible_id,  
                    'name_responsible': name_responsible,
                    'detailed_description': project.detailed_description,
                    'type_aplyuni': project.type_aplyuni,
                    'objectives': project.objectives,
                    'necessary_requirements': project.necessary_requirements,
                    'progress': project.progress,
                    'accepting_applications': project.accepting_applications,
                    'name_uniuser': project.name_uniuser,
                    'collaboration_count': collaboration_count,
                    'collaborators': collaborators_info,
                }
                response_data.append(project_data)

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No se encontraron proyectos"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Obtener el proyecto más reciente creado por el usuario autenticado",
        responses={
            status.HTTP_200_OK: openapi.Response('Proyecto más reciente creado por el usuario'),
            status.HTTP_404_NOT_FOUND: openapi.Response('No se encontraron proyectos'),
        },
        tags=["Project Management"]
    )
    @action(detail=False, methods=['GET'], url_path='my-latest-project', permission_classes=[IsAuthenticated])
    async def view_latest_project_usercreator(self, request):
        # Get the authenticated user ID
        user_instance = request.user.id

        # Filter the latest project created by the user, ordered by ID
        latest_project = await sync_to_async(lambda: Projects.objects.filter(responsible=user_instance).order_by('-id').first())()

        if latest_project:
            # Manually construct the response data
            project_data = {
                'id': latest_project.id,
                'name': latest_project.name,
                'description': latest_project.description,
                'start_date': latest_project.start_date,
                'end_date': latest_project.end_date,
                'status': latest_project.status,
                'project_type': latest_project.project_type,
                'priority': latest_project.priority,
                'responsible': latest_project.responsible_id,
                'detailed_description': latest_project.detailed_description,
                'type_aplyuni': latest_project.type_aplyuni,
                'objectives': latest_project.objectives,
                'necessary_requirements': latest_project.necessary_requirements,
                'progress': latest_project.progress,
                'accepting_applications': latest_project.accepting_applications,
                'name_uniuser': latest_project.name_uniuser,
                # Add any additional fields as needed
            }

            return Response(project_data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No se encontraron proyectos"}, status=status.HTTP_404_NOT_FOUND)
    

    #PARA LA CONFIGURACION DEL PROYECTO
    @swagger_auto_schema(
        operation_description="Obtener un proyecto específico pasando el ID del proyecto en el cuerpo de la solicitud",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'project_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del proyecto'),
            },
            required=['project_id']
        ),
        responses={
            status.HTTP_200_OK: openapi.Response('Proyecto encontrado'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Proyecto no encontrado'),
        },
        tags=["CRUD Project Management"]
    )
    @action(detail=False, methods=['POST'], url_path='get-project-id', permission_classes=[IsAuthenticated])
    async def get_project_id(self, request):
        project_id = request.data.get('id_project')
        if not project_id:
            return Response({"message": "ID del proyecto es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        projects = await sync_to_async(Projects.objects.filter(id=project_id).first)()
        
        if projects:

                collaboratorsall = await sync_to_async(list)(Collaborations.objects.filter(project=projects).select_related('user__authuser'))
                collaborators_info = await self.get_collaborators_info_proyect(collaboratorsall)

                name_responsible = await self.get_responsible_name_proyect(projects)

                collaboration_count = await self.get_collaboration_count(projects)

                project_data = {
                    'id': projects.id,
                    'name': projects.name,
                    'description': projects.description,
                    'start_date': projects.start_date,
                    'end_date': projects.end_date,
                    'status': projects.status,
                    'project_type': projects.project_type,
                    'priority': projects.priority,
                    'responsible': projects.responsible_id,  
                    'name_responsible': name_responsible,
                    'detailed_description': projects.detailed_description,
                    'type_aplyuni': projects.type_aplyuni,
                    'objectives': projects.objectives,
                    'necessary_requirements': projects.necessary_requirements,
                    'progress': projects.progress,
                    'accepting_applications': projects.accepting_applications,
                    'name_uniuser': projects.name_uniuser,
                    'collaboration_count': collaboration_count,
                    'collaborators': collaborators_info,
                }

                return Response(project_data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No se encontraron proyectos"}, status=status.HTTP_404_NOT_FOUND)
        
    @swagger_auto_schema(
        method='get',
        operation_summary="Retrieve Collaborated Projects",
        operation_description="Retrieve the list of projects the authenticated user has collaborated on.",
        responses={
            200: openapi.Response(
                description="Successful response with list of projects.",
                schema=ProjectSerializer(many=True)
            ),
            404: openapi.Response(description="No projects found for the collaborations.")
        },
        tags=["Collab Management"]
    )
    @action(detail=False, methods=['GET'], url_path='my-collaborated-projects', permission_classes=[IsAuthenticated])
    async def view_project_usercollab(self, request):
        # Obtener la instancia del usuario autenticado
        user_instance = request.user.id  # Ajusta esto si tu relación es diferente

        # Filtrar colaboraciones del usuario de forma asíncrona
        collaborations = await sync_to_async(list)(Collaborations.objects.filter(user=user_instance))

        # Obtener los proyectos relacionados a las colaboraciones de forma asíncrona
        if collaborations:
            
            project_ids = await sync_to_async(lambda: [collab.project_id for collab in collaborations])()
            projects = await sync_to_async(list)(Projects.objects.filter(id__in=project_ids))

            if projects:
    
                response_data = []
                for project in projects:
                    collaboratorsall = await sync_to_async(list)(Collaborations.objects.filter(project=project).select_related('user__authuser'))
                    
                    collaborators_info = await self.get_collaborators_info_proyect(collaboratorsall)

                    name_responsible = await self.get_responsible_name_proyect(project)

                    collaboration_count = await self.get_collaboration_count_proyect(project)

                    project_data = {
                        'id': project.id,
                        'name': project.name,
                        'description': project.description,
                        'start_date': project.start_date,
                        'end_date': project.end_date,
                        'status': project.status,
                        'project_type': project.project_type,
                        'priority': project.priority,
                        'responsible': project.responsible_id,  
                        'name_responsible': name_responsible,
                        'detailed_description': project.detailed_description,
                        'type_aplyuni': project.type_aplyuni,
                        'objectives': project.objectives,
                        'necessary_requirements': project.necessary_requirements,
                        'progress': project.progress,
                        'accepting_applications': project.accepting_applications,
                        'name_uniuser': project.name_uniuser,
                        'collaboration_count': collaboration_count,
                        'collaborators': collaborators_info,
                    }
                    response_data.append(project_data)

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No se encontraron proyectos"}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"message": "No se encontraron colaboraciones."}, status=status.HTTP_404_NOT_FOUND)
        
    @swagger_auto_schema(
        operation_description="Obtener los dos proyectos más recientes en los que el usuario está colaborando",
        responses={
            status.HTTP_200_OK: openapi.Response('Lista de los dos proyectos más recientes en los que el usuario colabora'),
            status.HTTP_404_NOT_FOUND: openapi.Response('No se encontraron proyectos'),
        },
        tags=["Project Management"]
    )
    @action(detail=False, methods=['GET'], url_path='my-latest-two-collaborated-projects', permission_classes=[IsAuthenticated])
    async def view_latest_two_collaborated_projects(self, request):
    
        user_instance = request.user.id
            
        collaborations = await sync_to_async(list)(Collaborations.objects.filter(user=user_instance))

        if collaborations:
            
            project_ids = await sync_to_async(lambda: [collab.project_id for collab in collaborations])()
            projects = await sync_to_async(list)(Projects.objects.filter(id__in=project_ids))

            if projects:
        
                response_data = []
                for project in projects:
                    collaboratorsall = await sync_to_async(list)(Collaborations.objects.filter(project=project).select_related('user__authuser'))
                        
                    collaborators_info = await self.get_collaborators_info_proyect(collaboratorsall)

                    name_responsible = await self.get_responsible_name_proyect(project)

                    collaboration_count = await self.get_collaboration_count_proyect(project)

                    project_data = {
                            'id': project.id,
                            'name': project.name,
                            'description': project.description,
                            'start_date': project.start_date,
                            'end_date': project.end_date,
                            'status': project.status,
                            'project_type': project.project_type,
                            'priority': project.priority,
                            'responsible': project.responsible_id,  
                            'name_responsible': name_responsible,
                            'detailed_description': project.detailed_description,
                            'type_aplyuni': project.type_aplyuni,
                            'objectives': project.objectives,
                            'necessary_requirements': project.necessary_requirements,
                            'progress': project.progress,
                            'accepting_applications': project.accepting_applications,
                            'name_uniuser': project.name_uniuser,
                            'collaboration_count': collaboration_count,
                            'collaborators': collaborators_info,
                        }
                    response_data.append(project_data)

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No se encontraron proyectos"}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"message": "No se encontraron colaboraciones."}, status=status.HTTP_404_NOT_FOUND)
            
    async def get_collaboration_count_proyect(self, project):
        return await sync_to_async(lambda: Collaborations.objects.filter(project=project).count())()

    async def get_collaborators_info_proyect(self, collaborators):
        collaborator_info = []
        for collab in collaborators:
            if collab.user and collab.user.authuser:
                user_info = {
                    "id": collab.user.id,
                    "name": f"{collab.user.authuser.first_name} {collab.user.authuser.last_name}"
                }
                collaborator_info.append(user_info)
        return collaborator_info

    async def get_responsible_name_proyect(self, obj):
        
        if obj.responsible_id: 
            authuser = await sync_to_async(User.objects.get)(id=obj.responsible_id)
            if authuser:
                return f"{authuser.first_name} {authuser.last_name}"    
           
        
        
    @swagger_auto_schema(
        method='delete',
        operation_summary="Delete Collaborator",
        operation_description="Delete a collaborator from a project.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'project_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the project"),
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the user to remove from project")
            },
            required=['project_id', 'user_id']
        ),
        responses={
            204: openapi.Response(description="Collaborator deleted successfully"),
            400: openapi.Response(description="Both project_id and user_id are required"),
            404: openapi.Response(description="Project/User/Collaboration not found"),
            500: openapi.Response(description="Internal server error")
        },
        tags=["Collab Management"]
    )
    @action(detail=False, methods=['DELETE'], url_path='delete_collaborator', permission_classes=[IsAuthenticated])
    async def delete_collaborator(self, request):
        project_id = request.data.get('project_id')
        user_id = request.data.get('user_id')

        if not project_id or not user_id:
            return Response({"error": "Both project_id and user_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verificar que el proyecto y el usuario existen
            project = await sync_to_async(Projects.objects.get)(id=project_id)
            user = await sync_to_async(Users.objects.get)(id=user_id)

            # Verificar que la colaboración existe
            collaboration = await sync_to_async(Collaborations.objects.filter)(project=project, user=user)
            collaboration_instance = await sync_to_async(collaboration.first)()
            if not collaboration_instance:
                return Response({"error": "Collaboration not found"}, status=status.HTTP_404_NOT_FOUND)

            # Eliminar la colaboración
            await sync_to_async(collaboration_instance.delete)()

            # Eliminar la solicitud asociada al proyecto y usuario
            solicitud = await sync_to_async(Solicitudes.objects.filter)(id_project=project, id_user=user)
            solicitud_instance = await sync_to_async(solicitud.first)()
            if solicitud_instance:
                await sync_to_async(solicitud_instance.delete)()

            # Crear la notificación para el usuario eliminado
            notification_data = {
                'sender': request.user.id,  # Usuario autenticado (quien realiza la eliminación)
                'message': f"Has sido eliminado como colaborador del proyecto '{project.name}'.",
                'is_read': 0,
                'created_at': timezone.now().strftime('%Y-%m-%d'),
                'user_id': user.id  # Usuario eliminado del proyecto
            }
            notification_serializer = NotificationSerializer(data=notification_data)

            if await sync_to_async(notification_serializer.is_valid)():
                await sync_to_async(notification_serializer.save)()
            else:
                return Response(notification_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Collaborator deleted and notified successfully"}, status=status.HTTP_204_NO_CONTENT)

        except Projects.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FormsViewSet(ViewSet):
    @swagger_auto_schema(
        operation_description="Crear un nuevo formulario",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'url', 'created_end'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Título del formulario'),
                'url': openapi.Schema(type=openapi.TYPE_STRING, description='URL del formulario'),
            },
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                'Formulario creado exitosamente',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del formulario creado'),
                        'title': openapi.Schema(type=openapi.TYPE_STRING, description='Título del formulario'),
                        'url': openapi.Schema(type=openapi.TYPE_STRING, description='URL del formulario'),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Fecha de creación del formulario'),
                        'created_end': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Fecha de finalización del formulario'),
                        'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del usuario que creó el formulario'),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Datos inválidos en la solicitud'),
        },
        tags=["Form Management"]
    )
    @action(detail=False, methods=['POST'], url_path='create_form', permission_classes=[IsAuthenticated])
    async def create_form(self, request):
        # ID del usuario autenticado
        user_id = request.user.id

        # Datos del formulario
        form_data = {
            **request.data,
            'created_at': timezone.now().strftime('%Y-%m-%d'),  # Fecha de creación
            'user': user_id,  # Asigna el usuario autenticado como creador del formulario
        }

        # Serializa los datos
        form_serializer = FormSerializer(data=form_data)

        # Verifica si los datos son válidos y guarda de manera asincrónica
        if await sync_to_async(form_serializer.is_valid)():
            await sync_to_async(form_serializer.save)()
            return Response(form_serializer.data, status=status.HTTP_201_CREATED)

        return Response(form_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Obtener todos los formularios con los nombres de los usuarios",
        responses={
            status.HTTP_200_OK: openapi.Response(
                'Lista de formularios',
                openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del formulario'),
                            'title': openapi.Schema(type=openapi.TYPE_STRING, description='Título del formulario'),
                            'url': openapi.Schema(type=openapi.TYPE_STRING, description='URL del formulario'),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Fecha de creación del formulario'),
                            'created_end': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Fecha de finalización del formulario'),
                            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del usuario que creó el formulario'),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del usuario'),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Apellido del usuario'),
                        },
                    ),
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Error en la solicitud'),
        },
        tags=["Form Management"]
    )
    @action(detail=False, methods=['GET'], url_path='get_all_forms', permission_classes=[IsAuthenticated])
    async def get_all_forms(self, request):
        # Obtener todos los formularios de forma asincrónica
        forms = await self.get_forms()
        data = []

        for form in forms:
            form_data = FormSerializer(form).data
            user = await self.get_user(form.user_id)
            form_data['first_name'] = user.first_name
            form_data['last_name'] = user.last_name
            data.append(form_data)

        return Response(data, status=status.HTTP_200_OK)

    async def get_forms(self):
        return await sync_to_async(list)(Forms.objects.all().order_by('-created_at'))

    async def get_user(self, user_id):
        return await sync_to_async(User.objects.get)(id=user_id)

class UserAchievementsViewSet(ViewSet):

    @swagger_auto_schema(
        operation_description="Validar logros de un usuario y almacenarlos",
        responses={
            status.HTTP_200_OK: openapi.Response('Logros validados y almacenados'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Error en la solicitud'),
        },
        tags=["User Achievements"]
    )
    @action(detail=False, methods=['POST'],  url_path='validate_achievements', permission_classes=[IsAuthenticated])
    def validate_achievements(self, request):
        user = request.user  # Esto ya es la instancia del modelo 'Users'
        unlocked_achievements = []

        try:
            achievements = Achievements.objects.all()
            for achievement in achievements:
                unlocked = False

                # Aquí evalúa los criterios para desbloquear logros
                if achievement.id == 1:  # Primera Gran Misión
                    unlocked = Projects.objects.filter(responsible=user.id).exists()
                elif achievement.id == 2:  # Manos a la Obra
                    unlocked = Projects.objects.filter(status='En progreso', responsible=user.id).count() >= 2
                elif achievement.id == 3:  # Incansable Constructor
                    unlocked = Projects.objects.filter(status='completado', responsible=user.id).count() >= 5
                elif achievement.id == 4:  # Siempre al Liderazgo
                    unlocked = Projects.objects.filter(responsible=user.id).count() >= 3
                elif achievement.id == 5:  # Compromiso sin Fronteras
                    user_instance = Users.objects.get(authuser=user)
                    unlocked = Collaborations.objects.filter(user=user_instance.id).select_related('project').values('project__responsible__university').distinct().count() >= 3
                elif achievement.id == 6:  # Multitasker
                    unlocked = Projects.objects.filter(status='En progreso', responsible=user.id).count() >= 3
                elif achievement.id == 7:  # Colaborador Compulsivo
                    unlocked = Collaborations.objects.filter(user=user.id).count() >= 10
                elif achievement.id == 8:  # Maestro de Roles
                    # Verifica si el usuario tiene más de una colaboración única en proyectos
                    collaborations_count = Collaborations.objects.filter(user=user.id).values('project').annotate(unique_roles=Count('role')).count()
                    projects_count = Projects.objects.filter(responsible=user.id).count()
                    # Desbloquea el logro si hay colaboraciones y es responsable de al menos un proyecto
                    unlocked = collaborations_count > 0 and projects_count > 0
                elif achievement.id == 9:  # Líder Experto
                    unlocked = Projects.objects.filter(status='completado', responsible=user.id).count() >= 5
                elif achievement.id == 10:  # Desarrollador Incansable
                    unlocked = Projects.objects.filter(status='completado', project_type__contains=['Desarrollo de Software'], responsible=user.id).count() >= 3
                elif achievement.id == 11:  # Investigador Académico
                    unlocked = Projects.objects.filter(status='completado', project_type__contains=['Investigación Académica'], responsible=user.id).count() >= 2
                elif achievement.id == 12:  # Creador Ecológico
                    unlocked = Projects.objects.filter(status='completado', project_type__contains=['Ambiental'], responsible=user.id).count() >= 3
                elif achievement.id == 13:  # Analista de Datos
                    unlocked = Projects.objects.filter(status='completado', project_type__contains=['Análisis de Datos'], responsible=user.id).count() >= 2
                elif achievement.id == 14:  # Planificador Estratégico
                    unlocked = Projects.objects.filter(status='completado', project_type__contains=['Planificación y Gestión'], responsible=user.id).count() >= 1
                elif achievement.id == 15:  # Innovador del Futuro
                    unlocked = Projects.objects.filter(status='completado', project_type__contains=['Innovación o Emprendimiento'], responsible=user.id).count() >= 2

                if unlocked:
                # Verificar si el logro ya ha sido desbloqueado por el usuario
                    if not UserAchievements.objects.filter(user=user.id, achievement=achievement).exists():
                        unlocked_achievements.append(achievement.id)

                        # Guardar en UserAchievements
                        user_achievement_data = {
                            'user': user.id,  # Asignar el ID del usuario autenticado
                            'achievement': achievement.id,  # Asignar el ID del logro
                            'unlocked': True,  # Estado de desbloqueo
                        }

                        # Serializa los datos
                        user_achievement_serializer = UserAchievementsSerializer(data=user_achievement_data)

                        # Guarda si los datos son válidos
                        if user_achievement_serializer.is_valid():
                            user_achievement_serializer.save()
                        else:
                            return Response(user_achievement_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'unlocked_achievements': unlocked_achievements}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    @swagger_auto_schema(
        operation_description="Obtener todos los logros del usuario",
        responses={
            status.HTTP_200_OK: openapi.Response(
                'Lista de logros',
                openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del logro del usuario'),
                            'achievement': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del logro correspondiente'),
                            'unlocked': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Estado del logro (desbloqueado o no)'),
                            'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del usuario al que pertenece el logro'),
                        },
                    ),
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Error en la solicitud'),
        },
        tags=["User Achievements"]
    )
    @action(detail=False, methods=['GET'], url_path='list_user_achievements', permission_classes=[IsAuthenticated])
    def list_user_achievements(self, request):
        user = request.user
        user_achievements = UserAchievements.objects.filter(user=user.id)

        serializer = UserAchievementsSerializer(user_achievements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
    