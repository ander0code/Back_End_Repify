from django.contrib.auth import authenticate

import adrf
from adrf.serializers import Serializer

from rest_framework_simplejwt.tokens import RefreshToken
from .models import Users, Projects , Collaborations, Solicitudes  # Asegúrate de tener bien definido tu modelo de Usuarios
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class LoginSerializer(Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Autenticar al usuario usando el email y la contraseña
        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError('Invalid email or password.')

        # Generar los tokens JWT
        refresh = RefreshToken.for_user(user)
        
        try:
            custom_user = Users.objects.get(authuser=user)  # Buscar el usuario personalizado por el authuser
            university_name = custom_user.university  # Extraer el nombre de la universidad
        except Users.DoesNotExist:
            university_name = None  # Si no existe la relación, se devuelve None

        try:
            custom_user = Users.objects.get(authuser=user)  # Buscar el usuario personalizado por el authuser
            career_name = custom_user.career  # Extraer el nombre de la universidad
        except Users.DoesNotExist:
            career_name = None  # Si no existe la relación, se devuelve None

        # Retornar los tokens y los datos del usuario, incluyendo el ID
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'email': user.email,
            'id': user.id,  # Aquí se agrega el ID del usuario
            'university': university_name,
            'career':career_name
        }

class CustomUserSerializer(adrf.serializers.ModelSerializer):
    
    created_at = serializers.DateTimeField(format="%Y-%m-%d")
    
    class Meta:
        model = Users
        fields = [
            'authuser',
            'university',
            'career',
            'cycle',
            'biography',
            'photo',
            'achievements',
            'created_at'
        ]
        extra_kwargs = {
            'id': {'read_only': True},  # Esto asegura que el ID no se puede establecer manualmente
            'created_at': {'read_only': True},  # Esto asegura que created_at se establezca automáticamente
        }

class ProjectSerializerCreate(adrf.serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()  # Nombre completo del creador
    collaboration_count = serializers.SerializerMethodField()  # Cantidad de colaboradores
    collaborators = serializers.SerializerMethodField()  # Nombres de los colaboradores
    project_type = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    objectives = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    necessary_requirements = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    
    class Meta:
        model = Projects
        fields = [
            'name',
            'description',
            'start_date',
            'end_date',
            'status',
            'project_type',
            'priority',
            'responsible',
            'detailed_description',
            'objectives',
            'necessary_requirements',
            'progress',
            'name_uniuser',
            'accepting_applications',
            'type_aplyuni',
            'creator_name',  # Nombre completo del creador
            'collaboration_count',  # Cantidad de colaboradores
            'collaborators'  # Lista de nombres de los colaboradores
        ]
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def get_creator_name(self, obj):
        # Acceder a los campos de first_name y last_name del responsable desde auth_user
        if obj.responsible and obj.responsible.authuser:
            return f"{obj.responsible.authuser.first_name} {obj.responsible.authuser.last_name}"
        return None

    def get_collaboration_count(self, obj):
        # Contar la cantidad de colaboradores relacionados con el proyecto
        return Collaborations.objects.filter(project=obj).count()

    def get_collaborators(self, obj):
        # Obtener los nombres completos de los colaboradores asociados al proyecto
        collaborators = Collaborations.objects.filter(project=obj).select_related('user__authuser')
        return [
            f"{collab.user.authuser.first_name} {collab.user.authuser.last_name}"
            for collab in collaborators if collab.user and collab.user.authuser
        ]

class ProjectSerializerAll(adrf.serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()  # Nombre completo del creador
    collaboration_count = serializers.SerializerMethodField()  # Cantidad de colaboradores
    project_type = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)

    class Meta:
        model = Projects
        fields = [
            'id',
            'name',
            'description',
            'start_date',
            'end_date',
            'status',
            'project_type',
            'priority',
            'responsible',
            'name_uniuser',
            'detailed_description',
            'progress',
            'accepting_applications',
            'type_aplyuni',
            'creator_name',  # Nombre completo del creador
            'collaboration_count'  # Cantidad de colaboradores
        ]
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def get_creator_name(self, obj):
        # Acceder a los campos de first_name y last_name del responsable desde auth_user
        if obj.responsible and obj.responsible.authuser:
            return f"{obj.responsible.authuser.first_name} {obj.responsible.authuser.last_name}"
        return None

    def get_collaboration_count(self, obj):
        # Contar la cantidad de colaboradores relacionados con el proyecto
        return Collaborations.objects.filter(project=obj).count()

class ProjectSerializerID(adrf.serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()  # Nombre completo del creador
    collaboration_count = serializers.SerializerMethodField()  # Cantidad de colaboradores
    project_type = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    objectives = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    necessary_requirements = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
        
    class Meta:
        model = Projects
        fields = [
            'id',
            'name',
            'description',
            'start_date',
            'end_date',
            'status',
            'project_type',
            'priority',
            'responsible',
            'name_uniuser',
            'detailed_description',
            'objectives',
            'progress',
            'necessary_requirements',
            'accepting_applications',
            'type_aplyuni',
            'creator_name',  # Nombre completo del creador
            'collaboration_count',  # Cantidad de colaboradores
        ]
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def get_creator_name(self, obj):
        # Acceder a los campos de first_name y last_name del responsable desde auth_user
        if obj.responsible and obj.responsible.authuser:
            return f"{obj.responsible.authuser.first_name} {obj.responsible.authuser.last_name}"
        return None

    def get_collaboration_count(self, obj):
        # Contar la cantidad de colaboradores relacionados con el proyecto
        return Collaborations.objects.filter(project=obj).count()

    def get_collaborators(self, obj):
        # Obtener los nombres completos de los colaboradores asociados al proyecto
        collaborators = Collaborations.objects.filter(project=obj).select_related('user__authuser')
        return [
            f"{collab.user.authuser.first_name} {collab.user.authuser.last_name}"
            for collab in collaborators if collab.user and collab.user.authuser
        ]

class SolicitudSerializer(adrf.serializers.ModelSerializer):
    
    created_at = serializers.DateTimeField(format="%Y-%m-%d")
    
    class Meta:
        model = Solicitudes
        fields = ["id_solicitud","id_user","id_project","status","name_user","name_lider","name_project","created_at"]

class CollaboratorSerializer(adrf.serializers.ModelSerializer):
    class Meta:
        model = Collaborations
        fields = "__all__"

class ProjectSerializer(adrf.serializers.ModelSerializer):
    objectives = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    necessary_requirements = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    collaboration_count = serializers.SerializerMethodField()
    collaborators = serializers.SerializerMethodField()
    name_responsible = serializers.SerializerMethodField()

    class Meta:
        model = Projects
        fields = [
            'id',
            'name',
            'description',
            'start_date',
            'end_date',
            'status',
            'project_type',
            'priority',
            'responsible',
            'name_responsible',  # Agregar el nombre del responsable
            'detailed_description',
            'type_aplyuni',
            'objectives',
            'necessary_requirements',
            'progress',
            'accepting_applications',
            'name_uniuser',
            'collaboration_count',
            'collaborators'
        ]
    
    def get_name_responsible(self, obj):
        # Obtener el nombre completo del responsable (creador) del proyecto
        return f"{obj.responsible.authuser.first_name} {obj.responsible.authuser.last_name}"
    
    def get_collaboration_count(self, obj):
        return Collaborations.objects.filter(project=obj).count()

    def get_collaborators(self, obj):
        collaborators = Collaborations.objects.filter(project=obj).select_related('user__authuser')
        return [
            f"{collab.user.authuser.first_name} {collab.user.authuser.last_name}"
            for collab in collaborators if collab.user and collab.user.authuser
        ]
        
        
class ProjectUpdateSerializer(adrf.serializers.ModelSerializer):
    objectives = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    necessary_requirements = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)

    class Meta:
        model = Projects
        fields = [
            'name', 
            'description', 
            'start_date', 
            'end_date', 
            'status', 
            'project_type', 
            'priority', 
            'responsible', 
            'detailed_description', 
            'type_aplyuni', 
            'objectives', 
            'necessary_requirements', 
            'progress', 
            'accepting_applications', 
            'name_uniuser'
        ]