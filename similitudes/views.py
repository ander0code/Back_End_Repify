from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, F, Value, FloatField, Case, When
from django.db.models.functions import Cast
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from usuario.models import Users
from django.contrib.auth.models import User
class SimilarUsersViewSet(ViewSet):

    @swagger_auto_schema(
        operation_summary="Obtener usuarios similares",
        operation_description=(
            "Este endpoint devuelve una lista de usuarios similares basándose en los intereses, carrera, "
            "ciclo y universidad del usuario autenticado. Excluye usuarios con menos del 10% de similitud."
        ),
        responses={
            200: openapi.Response(
                description="Lista de usuarios similares",
                examples={
                    "application/json": {
                        "status": "success",
                        "data": [
                            {
                                "user_id": 2,
                                "user_name": "John Doe",
                                "photo": "https://example.com/photo.jpg",
                                "similarity": 0.85,
                                "interests": ["Python", "Django"],
                                "career": "Ingeniería de Software",
                                "cycle": "V",
                                "university": "Universidad Autónoma"
                            },
                        
                        ]
                    }
                },
            ),
            400: openapi.Response(
                description="Error en la solicitud",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "User has no interests to compare."
                    }
                },
            ),
            404: openapi.Response(
                description="Usuario no encontrado",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Authenticated user not found in Users table."
                    }
                },
            ),
            500: openapi.Response(
                description="Error interno del servidor",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Error details here."
                    }
                },
            ),
        },
    )
    @action(detail=False, methods=['GET'], url_path='similitud_user', permission_classes=[IsAuthenticated])
    def similar_users(self, request):
        try:
            authenticated_user = request.user.id

            # Obtener al usuario autenticado desde la tabla Users
            target_user = Users.objects.select_related('authuser').get(authuser=authenticated_user)

            target_interests_count = len(target_user.interests) if target_user.interests else 0
            if target_interests_count == 0:
                return Response({"status": "error", "message": "User has no interests to compare."}, status=400)

            # Calcular similitudes y filtrar por total_similarity >= 0.1
            users = (
                Users.objects.select_related('authuser')
                .annotate(
                    interests_similarity=Cast(
                        Count('interests', filter=Q(interests__overlap=target_user.interests)), FloatField()
                    ) / Cast(Value(target_interests_count), FloatField()),

                    career_similarity=Case(
                        When(career=target_user.career, then=Value(1.0)),
                        default=Value(0.0),
                        output_field=FloatField(),
                    ),

                    cycle_similarity=Case(
                        When(cycle=target_user.cycle, then=Value(1.0)),
                        default=Value(0.0),
                        output_field=FloatField(),
                    ),

                    university_similarity=Case(
                        When(university=target_user.university, then=Value(1.0)),
                        default=Value(0.0),
                        output_field=FloatField(),
                    ),

                    total_similarity=(
                        F('interests_similarity') * 0.5
                        + F('career_similarity') * 0.2
                        + F('cycle_similarity') * 0.2
                        + F('university_similarity') * 0.1
                    ),
                )
                .filter(~Q(authuser=authenticated_user), total_similarity__gte=0.1)  
                .order_by('-total_similarity')[:10] 
            )

            response_data = [
                {
                    "user_id": user.id,
                    "user_name": user.authuser.first_name + " " + user.authuser.last_name,  
                    "photo": user.photo,  
                    "similarity": round(user.total_similarity, 2),  
                    "interests": user.interests,
                    "career": user.career,
                    "cycle": user.cycle,
                    "university": user.university,
                }
                for user in users
            ]

            return Response({"status": "success", "data": response_data}, status=200)

        except Users.DoesNotExist:
            return Response({"status": "error", "message": "Authenticated user not found in Users table."}, status=404)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)