from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Users, Projects , Collaborations, Solicitudes, Notifications  # Asegúrate de tener bien definido tu modelo de Usuarios

from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class LoginSerializer(serializers.Serializer):
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
        
        # Retornar los tokens y los datos del usuario, incluyendo el ID
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'email': user.email,
            'id': user.id,  # Aquí se agrega el ID del usuario
        }

class CustomUserSerializer(serializers.ModelSerializer):
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
             
class ProjectSerializer(serializers.ModelSerializer):
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
            'expected_benefits',
            'necessary_requirements',
            'progress',
            "accepting_applications"
        ]
        extra_kwargs = {
            'id': {'read_only': True},   # Esto asegura que el ID no se puede establecer manualmente
        }

class SolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solicitudes
        fields = "__all__"


class CollaborationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collaborations
        fields = "__all__"
        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = "__all__"