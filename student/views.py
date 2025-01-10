
from rest_framework import status, viewsets
from rest_framework.response import Response
from .serializers import RegistrationSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.utils import timezone


class RegistrationViewSet(viewsets.ViewSet):

    def create(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.last_login = timezone.now()
            user.save()
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            access_token['email'] = user.email
            access_token['first_name'] = user.first_name
            access_token['last_name'] = user.last_name
            response = Response({
                "message": "User login successfully",
                "success": True,
                'access': str(access_token),
            }, status=status.HTTP_200_OK)
            cookie_max_age = 24 * 60 * 60
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=cookie_max_age,
            )

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
