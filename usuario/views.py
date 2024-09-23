from django.shortcuts import render

# Create your views here.
class LoginViewSet(ViewSet):
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    # @swagger_auto_schema(
    #     operation_description="User login",
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         required=['email', 'password'],
    #         properties={
    #             'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
    #             'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
    #         },
    #     ),
    #     responses={200: openapi.Response('OK', UserSerializer)},
    #     tags=["User Management"]
    # )
    @action(detail=False, methods=['POST'], permission_classes=[])
    def login(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            
            if not email:
                return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not password:
                return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            user = get_object_or_404(User, email=email)
            
            if not user.check_password(password):
                return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)

            token, created = Token.objects.get_or_create(user=user)

            serializer = UserSerializer(instance=user)

            return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK)
    
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except KeyError:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
       
            print(f"Unexpected error: {str(e)}")
        return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # @swagger_auto_schema(
    #     operation_description="User registration",
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         required=['email', 'password'],
    #         properties={
    #             'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
    #             'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
    #         },
    #     ),
    #     responses={201: openapi.Response('Created', UserSerializer)},
    #     tags=["User Management"]
    # )
    @action(detail=False, methods=['POST'], permission_classes=[])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(email=serializer.data["email"])
            user.set_password(serializer.data["password"])
            user.save()
            token = Token.objects.create(user=user)
            return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @swagger_auto_schema(
    #     operation_description="Get user profile",
    #     responses={200: openapi.Response('OK', UserSerializer)},
    #     tags=["User Management"]
    # )
    @action(detail=False, methods=['GET'])
    def profile(self, request):
        serializer = UserSerializer(instance=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'])
    def Data_user(self, request):
        id_user = request.query_params.get('id_user')  # Utiliza query_params para GET requests
        
        if not id_user:
            return Response({"detail": "El parámetro 'id_user' es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data_user = Volunteers.objects.filter(user_id=id_user)
            
            if data_user.exists():
                serializer = UserDataSerializer(data_user, many=True)  # Usa UserDataSerializer aquí
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "No se encontraron voluntarios para el ID proporcionado."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        