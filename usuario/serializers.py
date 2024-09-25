from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Users  # Asegúrate de tener bien definido tu modelo de Usuarios

class LoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        # Autenticar al usuario con email y contraseña
        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError('Credenciales incorrectas, intente nuevamente.')

        if not user.is_active:
            raise serializers.ValidationError('Esta cuenta está inactiva.')

        # Devolver los tokens JWT
        return {
            'refresh': str(RefreshToken.for_user(user)),
            'access': str(RefreshToken.for_user(user).access_token),
            'email': user.email,
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
        