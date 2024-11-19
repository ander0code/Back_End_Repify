from django.contrib.auth import authenticate
import adrf
from adrf.serializers import Serializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Users, Projects , Collaborations, Solicitudes, Notifications, Forms, Achievements, UserAchievements  # Asegúrate de tener bien definido tu modelo de Usuarios
from .models import Users, Projects , Collaborations, Solicitudes  
from rest_framework import serializers
from django.contrib.auth.models import User
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
            
        try:
            name = User.objects.get(email=user)
            full_name = name.first_name + " " + name.last_name
        except User.DoesNotExist:
            full_name = None  

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'email': user.email,
            'name': full_name,
            'id': user.id, 
            'photo' : custom_user.photo ,  
            'university': university_name,
            'career':career_name,
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
            'interests',
            'biography',
            'photo',
            'achievements',
            'created_at'
        ]
        extra_kwargs = {
            'id': {'read_only': True}, 
            'created_at': {'read_only': True}, 
        }

class ProjectSerializerCreate(adrf.serializers.ModelSerializer):
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
            'type_aplyuni'
  
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
  
class ProjectSerializerID(serializers.ModelSerializer):
    
    creator_name = serializers.SerializerMethodField() 
    collaboration_count = serializers.SerializerMethodField()  
    project_type = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    necessary_requirements = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
    has_applied = serializers.SerializerMethodField()
    objectives = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)
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
            'objectives',
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

class SolicitudSerializer(adrf.serializers.ModelSerializer):
    
    created_at = serializers.DateTimeField(format="%Y-%m-%d")
    
    class Meta:
        model = Solicitudes
        fields = ["id_solicitud","id_user","id_project","status","name_user","name_lider","message","photo","name_project","created_at"]

class CollaboratorSerializer(adrf.serializers.ModelSerializer):
    class Meta:
        model = Collaborations
        fields = "__all__"
        
class NotificationSerializer(adrf.serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = "__all__"
        
class NotificationSerializerMS(adrf.serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = ['id','message','is_read'] 
        
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

    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    interests = serializers.ListField(child=serializers.CharField(max_length=500), allow_empty=True, allow_null=True)

    class Meta:
        model = Users
        fields = ['university', 'career', 'cycle', 'biography','interests','photo', 'achievements', 'created_at', 
                  'email', 'first_name', 'last_name', 'date_joined'] 

class FormSerializer(adrf.serializers.ModelSerializer):

    created_at =  serializers.DateTimeField(format="%Y-%m-%d") 
    class Meta:
        model = Forms
        fields = ['id', 'title', 'url', 'created_at', 'user']

class AchievementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievements
        fields = ['id', 'name', 'description']

class UserAchievementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAchievements
        fields = "__all__"

