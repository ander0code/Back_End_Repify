from django.contrib.auth import authenticate

import adrf
from adrf.serializers import Serializer

from rest_framework_simplejwt.tokens import RefreshToken
from .models import Users, Projects , Collaborations, Solicitudes, Notifications  # Asegúrate de tener bien definido tu modelo de Usuarios

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

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError('Invalid email or password.')

        # Generar los tokens JWT
        refresh = RefreshToken.for_user(user)
        
        try:
            custom_user = Users.objects.get(authuser=user)  
            university_name = custom_user.university  
        except Users.DoesNotExist:
            university_name = None  

        try:
            custom_user = Users.objects.get(authuser=user) 
            career_name = custom_user.career  
        except Users.DoesNotExist:
            career_name = None  

        # Retornar los tokens y los datos del usuario, incluyendo el ID
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'email': user.email,
            'id': user.id,  
            'university': university_name,
            'career':career_name
        }

class CustomUserSerializer(adrf.serializers.ModelSerializer):
    
    interests = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d")
    
    class Meta:
        model = Users
        fields = [
            'authuser',
            'university',
            'career',
            'cycle',
            'biography',
            'interests',
            'photo',
            'achievements',
            'created_at'
        ]
        extra_kwargs = {
            'id': {'read_only': True}, 
            'created_at': {'read_only': True}, 
        }

class ProjectSerializerCreate(adrf.serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField() 
    collaboration_count = serializers.SerializerMethodField()  
    collaborators = serializers.SerializerMethodField()  
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
            'creator_name', 
            'collaboration_count',  
            'collaborators'  
        ]
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def get_creator_name(self, obj):
        
        if obj.responsible and obj.responsible.authuser:
            return f"{obj.responsible.authuser.first_name} {obj.responsible.authuser.last_name}"
        return None

    def get_collaboration_count(self, obj):

        return Collaborations.objects.filter(project=obj).count()

    def get_collaborators(self, obj):
       
        collaborators = Collaborations.objects.filter(project=obj).select_related('user__authuser')
        return [
            f"{collab.user.authuser.first_name} {collab.user.authuser.last_name}"
            for collab in collaborators if collab.user and collab.user.authuser
        ]

class ProjectSerializerAll(adrf.serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField() 
    collaboration_count = serializers.SerializerMethodField() 
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
            'creator_name',  
            'collaboration_count'
        ]
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def get_creator_name(self, obj):
        
        if obj.responsible and obj.responsible.authuser:
            return f"{obj.responsible.authuser.first_name} {obj.responsible.authuser.last_name}"
        return None

    def get_collaboration_count(self, obj):
        
        return Collaborations.objects.filter(project=obj).count()
    
class ProjectSerializerID(adrf.serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField() 
    collaboration_count = serializers.SerializerMethodField()  
    project_type = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    necessary_requirements = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    has_applied = serializers.SerializerMethodField()
    
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
            'necessary_requirements',
            'progress',
            'necessary_requirements',
            'accepting_applications',
            'type_aplyuni',
            'creator_name', 
            'collaboration_count',  
            'has_applied'
        ]
        extra_kwargs = {
            'id': {'read_only': True},
        }

    def get_creator_name(self, obj):
        
        if obj.responsible and obj.responsible.authuser:
            return f"{obj.responsible.authuser.first_name} {obj.responsible.authuser.last_name}"
        return None

    def get_collaboration_count(self, obj):
       
        return Collaborations.objects.filter(project=obj).count()

    def get_collaborators(self, obj):
        
        collaborators = Collaborations.objects.filter(project=obj).select_related('user__authuser')
        return [
            f"{collab.user.authuser.first_name} {collab.user.authuser.last_name}"
            for collab in collaborators if collab.user and collab.user.authuser
        ]
    def get_has_applied(self, obj):
        # Obtener el usuario autenticado desde el contexto
        user = self.context['request'].user.id 

        # Verificar si el usuario es el responsable del proyecto
        if obj.responsible and obj.responsible.authuser and obj.responsible.authuser.id == user:
            return True

        # Si no es el responsable, verificar si el usuario ha aplicado al proyecto
        return Solicitudes.objects.filter(id_user=user, id_project=obj).exists()

class SolicitudSerializer(adrf.serializers.ModelSerializer):
    
    created_at = serializers.DateTimeField(format="%Y-%m-%d")
    
    class Meta:
        model = Solicitudes
        fields = ["id_solicitud","id_user","id_project","status","name_user","name_lider","name_project","created_at"]

class CollaboratorSerializer(adrf.serializers.ModelSerializer):
    class Meta:
        model = Collaborations
        fields = "__all__"
        
class NotificationSerializer(adrf.serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = "__all__"
        
class NotificationSerializerMS(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = ['message'] 
        
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
            'name_responsible', 
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
        
class ProfileSerializer(adrf.serializers.ModelSerializer):
    email = serializers.EmailField(source='authuser.email', read_only=True)
    first_name = serializers.CharField(source='authuser.first_name', read_only=True)
    last_name = serializers.CharField(source='authuser.last_name', read_only=True)
    date_joined = serializers.DateTimeField(source='authuser.date_joined', read_only=True)
    interests = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    
    class Meta:
        model = Users
        fields = ['university', 'career', 'cycle', 'biography','interests', 'photo', 'achievements', 'created_at', 
                  'email', 'first_name', 'last_name', 'date_joined']