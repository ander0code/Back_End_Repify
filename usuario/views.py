from adrf.viewsets import ViewSet
from django.contrib.auth.models import User
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, ProjectSerializerCreate,CustomUserSerializer, ProjectSerializerAll,SolicitudSerializer,GetCollaboratorSerializer,ProjectSerializerID,CollaboratorSerializer
from rest_framework.decorators import action,permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from usuario.models import Users,Projects,Solicitudes,Collaborations
from rest_framework.permissions import AllowAny ,IsAuthenticated
import random

from asgiref.sync import sync_to_async

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
    @action(detail=False, methods=['POST'], url_path='Register', permission_classes=[AllowAny])
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
            'created_at': timezone.now().strftime('%Y-%m-%d')  # Establece la fecha de creación
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
    @action(detail=False, methods=['POST'], url_path='request-password-reset', permission_classes=[AllowAny])
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
            user_profile = Users.objects.get(authuser=user) # Asegúrate de que tienes acceso al perfil del usuario
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
    @action(detail=False, methods=['POST'], url_path='reset_password', permission_classes=[AllowAny])
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
            required=['id'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user to view'),
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
    @action(detail=False, methods=['PUT'], url_path='update-profile')
    def update_user_profile(self, request):
        user_id = request.data.get('id')
        try:
            # Obtener el perfil de usuario usando el ID (pk)
            user_profile = Users.objects.get(pk=user_id)
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
    @action(detail=False, methods=['DELETE'], url_path='delete-user')
    def delete_user(self, request):
        user_id = request.data.get('id')
        try:
            # Buscar al usuario en la tabla Users por su ID (pk)
            user_profile = Users.objects.get(pk=user_id)
            
            # Obtener el usuario en la tabla auth_user
            auth_user = user_profile.authuser  # Asumiendo que 'authuser' es una FK a User

        except Users.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Eliminar el perfil del usuario en la tabla personalizada Users
        user_profile.delete()

        # Eliminar el usuario en la tabla auth_user
        auth_user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def VerInfo():
        pass

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
                'project_type': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description="project_type to apply"),
                'priority': openapi.Schema(type=openapi.TYPE_STRING, description='Priority level of the project'),
                'detailed_description': openapi.Schema(type=openapi.TYPE_STRING, description='Detailed description of the project'),
                'expected_benefits': openapi.Schema(type=openapi.TYPE_STRING, description='Expected benefits of the project'),
                'necessary_requirements': openapi.Schema(type=openapi.TYPE_STRING, description='Necessary requirements for the project'),
                'progress': openapi.Schema(type=openapi.TYPE_INTEGER, description='Progress percentage of the project'),
                'accepting_applications': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Accepting requests for collaboration'),
                'type_aplyuni': openapi.Schema(type=openapi.TYPE_STRING, description='type_aplyuni of the project'),  
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
                            description="List of project_type"
                        ),
                        'priority': openapi.Schema(type=openapi.TYPE_STRING, description='Priority level of the project'),
                        'responsible': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user responsible for the project'),
                        'detailed_description': openapi.Schema(type=openapi.TYPE_STRING, description='Detailed description of the project'),
                        'expected_benefits': openapi.Schema(type=openapi.TYPE_STRING, description='Expected benefits of the project'),
                        'necessary_requirements': openapi.Schema(type=openapi.TYPE_STRING, description='Necessary requirements for the project'),
                        'progress': openapi.Schema(type=openapi.TYPE_INTEGER, description='Progress percentage of the project'),
                        'accepting_applications': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Accepting requests for collaboration'),
                        'type_aplyuni': openapi.Schema(type=openapi.TYPE_STRING, description='type_aplyuni'),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Invalid input data'),
        },
        tags=["CRUD Project Management"]
    )
    @action(detail=False, methods=['POST'], url_path='create_proyect', permission_classes=[IsAuthenticated])
    def create_project(self, request):
        
        responsible_user_id = request.user.id
        
        # Rellenar automáticamente el campo 'responsible' con el ID del usuario autenticado
        project_data = {
            **request.data,
            'start_date': timezone.now().strftime('%Y-%m-%d'),  # Fecha de creación
            'name_uniuser': "",
            'responsible': responsible_user_id  # Asigna el usuario autenticado como responsable
        }
    
        # Serializa los datos
        project_serializer = ProjectSerializerCreate(data=project_data)
        
        if project_serializer.is_valid():
            project_serializer.save()  # Guarda el proyecto si los datos son válidos
            return Response(project_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Update an existing project by ID",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id'],
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the project to view'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the project'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the project'),
                'end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='End date of the project'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Current status of the project'),
                'project_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of the project'),
                'priority': openapi.Schema(type=openapi.TYPE_STRING, description='Priority of the project'),
                'detailed_description': openapi.Schema(type=openapi.TYPE_STRING, description='Detailed description of the project'),
                'expected_benefits': openapi.Schema(type=openapi.TYPE_STRING, description='Expected benefits of the project'),
                'necessary_requirements': openapi.Schema(type=openapi.TYPE_STRING, description='Necessary requirements for the project'),
                'progress': openapi.Schema(type=openapi.TYPE_INTEGER, description='Progress percentage of the project'),
                'accepting_applications': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='ACCEPT REQUESTS'),
            },
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                'Project updated successfully',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the project'),
                        'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the project'),
                        'start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Start date of the project'),
                        'end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='End date of the project'),
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Current status of the project'),
                        'project_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of the project'),
                        'responsible': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the responsible user'),
                        'detailed_description': openapi.Schema(type=openapi.TYPE_STRING, description='Detailed description of the project'),
                        'expected_benefits': openapi.Schema(type=openapi.TYPE_STRING, description='Expected benefits of the project'),
                        'necessary_requirements': openapi.Schema(type=openapi.TYPE_STRING, description='Necessary requirements for the project'),
                        'progress': openapi.Schema(type=openapi.TYPE_INTEGER, description='Progress percentage of the project'),
                        'accepting_applications': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='ACCEPT REQUESTS'),
                    }
                )
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response('Project not found'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Invalid input data'),
        },
        tags=["CRUD Project Management"]
    )
    @action(detail=False, methods=['PUT'], url_path='update_project', permission_classes=[IsAuthenticated])
    def update_project(self, request):
        
        try:
            # Obtener el proyecto usando el ID (pk)
            project_id = request.data.get('id')
            project = Projects.objects.get(pk=project_id)
        except project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        # Crea un serializador con los datos actuales del proyecto y los nuevos datos enviados
        serializer = ProjectSerializerCreate(instance=project, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # Guarda las actualizaciones
            return Response(serializer.data, status=status.HTTP_200_OK)
        
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
    def delete_project(self, request):
        try:
            # Obtener el proyecto usando el ID (pk)
            project_id = request.data.get('id')
            project = Projects.objects.get(pk=project_id)
            project.delete()  # Elimina el proyecto
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
    def view_project_id(self, request):
        project_id = request.data.get('id')

        if not project_id:
            return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtener el proyecto usando el ID
            project = Projects.objects.get(pk=project_id)
        except Projects.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        # Serializa los datos del proyecto
        serializer = ProjectSerializerID(project)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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
    def view_project_all(self, request):
        # Obtener todos los proyectos en orden ascendente por start_date
        projects = Projects.objects.all().order_by('start_date')
        
        # Serializar los proyectos
        serializer = ProjectSerializerAll(projects, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
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
            status.HTTP_201_CREATED: openapi.Response('Solicitud creada exitosamente'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Error en los datos proporcionados'),
        },
        tags=["Notificacions Project Management"]
    )
    @action(detail=False, methods=['POST'], url_path='ApplyProject',permission_classes=[IsAuthenticated])
    def ApplyProject(self, request):
        project_id = request.data.get('project_id')
        user = request.user

        try:
            # Verificar si el proyecto acepta aplicaciones
            project = Projects.objects.get(id=project_id)
            if not project.accepting_applications:
                return Response({"error": "Este proyecto no está aceptando aplicaciones"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear la solicitud
            solicitud_data = {
                'id_user': user.id,
                'id_project': project_id,
                'status': 'Pendiente',
            }
            
            solicitud_serializer = SolicitudSerializer(data=solicitud_data)
            
            if solicitud_serializer.is_valid():
                solicitud_serializer.save()
                return Response(solicitud_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(solicitud_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Projects.DoesNotExist:
            return Response({"error": "Proyecto no encontrado"}, status=status.HTTP_404_NOT_FOUND)

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
    def AcceptProject(self, request):
        id_solicitud = request.data.get('id_solicitud')
        user = request.user

        try:
            solicitud = Solicitudes.objects.get(id_solicitud=id_solicitud)
            
            # Verificar si el usuario es el responsable del proyecto
            if solicitud.id_project.responsible.id != user.id:
                return Response({"error": "No tienes permiso para aceptar esta solicitud"}, status=status.HTTP_403_FORBIDDEN)

            # Cambiar el estado de la solicitud a 'Aceptada'
            solicitud.status = 'Aceptada'
            solicitud.save()

            # Crear una colaboración
            collaboration_data = {
                'user': solicitud.id_user.id,
                'project': solicitud.id_project.id,
                'status': 'Activa'
            }
            collaboration_serializer = CollaboratorSerializer(data=collaboration_data)
            
            if collaboration_serializer.is_valid():
                collaboration_serializer.save()
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
    def Denyproject(self, request):
        solicitud_id = request.data.get('solicitud_id')
        user = request.user

        try:
            solicitud = Solicitudes.objects.get(id=solicitud_id)
            
            # Verificar si el usuario es el responsable del proyecto
            if solicitud.id_project.responsible != user.id:
                return Response({"error": "No tienes permiso para negar esta solicitud"}, status=status.HTTP_403_FORBIDDEN)

            # Cambiar el estado de la solicitud a 'Negada'
            solicitud.status = 'Negada'
            solicitud.save()

            return Response({"mensaje": "Solicitud negada exitosamente"}, status=status.HTTP_200_OK)
        
        except Solicitudes.DoesNotExist:
            return Response({"error": "Solicitud no encontrada"}, status=status.HTTP_404_NOT_FOUND)
      
    @action(detail=False, methods=['POST'], url_path='project_solicitudes')
    def get_project_solicitudes(self, request):
        project_id = request.data.get('project_id')

        if not project_id:
            return Response({"error": "project_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verificar si el proyecto existe
            project = Projects.objects.get(id=project_id)
            
            # Filtrar solicitudes por proyecto
            solicitudes = Solicitudes.objects.filter(id_project=project)
            
            # Serializar las solicitudes
            serializer = SolicitudSerializer(solicitudes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Projects.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

    def view_project_usercreator():
        pass
    def view_project_usercollab():
        pass     

