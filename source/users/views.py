from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema

from .serializers import *
from .lib.permission import LoginRequired



class UserView(APIView):
    permission_classes = [AllowAny]

    def get_or_create_user(self, data: dict):
        serializer = CreateUserSerializer(data=data)

        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data
        serializer.create(validated_data=user)

        return Response(data=user, status=status.HTTP_201_CREATED)

    def post(self, request):
        '''
        계정 조회 및 등록

        ---
        '''
        return self.get_or_create_user(data=request.data)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def object(self, data: dict):
        serializer = LoginSerializer(data=data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data

        return Response(data=user, status=status.HTTP_200_OK)

    def post(self, request):
        '''
        로그인

        ---
        '''
        return self.object(data=request.data)

class LogoutView(APIView):
    permission_classes = [LoginRequired]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(request_body=LogoutSerializer)
    def post(self, request):
        '''
        로그아웃

        ---
        '''
        serializer = LogoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.validated_data.blacklist()

        return Response(status=status.HTTP_200_OK)

class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RefreshTokenSerializer)
    def post(self, request):
        '''
        Access Token 재발급

        ---
        '''
        serializer = RefreshTokenSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        token = serializer.validated_data

        return Response(data=token, status=status.HTTP_201_CREATED)

class UserInfoView(APIView):
    permission_classes = [LoginRequired]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        '''
        사용자 정보 조회

        ---
        '''
        user_serializer = UserInfoSerializers(request.user)

        return Response(data=user_serializer.data, status=status.HTTP_200_OK)
