import datetime as dt
import jwt

from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserModel, UserRoleModel


class CreateUserSerializer(serializers.Serializer):
    social_id = serializers.CharField(max_length=100, help_text='소셜사용자_id')
    social_type = serializers.CharField(max_length=20, help_text='소셜 타입')
    email = serializers.EmailField(max_length=100, required=False, help_text='이메일')
    phone = serializers.CharField(max_length=13, required=False, help_text='휴대폰 번호')

    def validate(self, data):
        if UserModel.objects.filter(social_id=data.get('social_id')).exists():
            raise serializers.ValidationError({'error': 'Account Already Exists'})
        return data

    def create(self, validated_data):
        validated_data['role'] = UserRoleModel.objects.get_or_create(id=2, name='user')[0]

        user = UserModel.objects.create(**validated_data)
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    social_id = serializers.CharField(max_length=100)
    email = serializers.CharField(max_length=100)
    token = serializers.CharField(max_length=256, read_only=True)

    def validate(self, data):
        user = authenticate(social_id=data.get('social_id'))
        if user is None:
            raise serializers.ValidationError({'error': 'User with given social_id does not exist'})

        try:
            token = RefreshToken.for_user(user=user)
        except:
            raise serializers.ValidationError({'error': 'Failed create Token'})

        # 사용자 email 변경된 경우 해당 email로 갱신
        if user.email != data['email']:
            user.email = data['email']

        # 최근 로그인시간 갱신
        user.last_login = dt.datetime.now()
        user.save()

        data = {
            'social_id': user.social_id,
            'access_token': f'Bearer {str(token.access_token)}',
            'refresh_token': str(token),
        }
        return data


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=512)

    def validate(self, data):
        try:
            refresh_token = RefreshToken(data['refresh_token'])
        except:
            raise serializers.ValidationError({'error': 'Invalid Token'})

        return refresh_token


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=512)

    def validate(self, data):
        # refresh_token 유저 검증
        try:
            token = jwt.decode(data['refresh_token'], key=settings.SECRET_KEY, algorithms=settings.SIMPLE_JWT['ALGORITHM'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError({'error': 'Token Signature has expired'})

        try:
            _ = UserModel.objects.get(social_id=token['social_id'])
        except UserModel.DoesNotExist:
            raise serializers.ValidationError({'error': 'Invalid User'})

        try:
            refresh_token = RefreshToken(data['refresh_token'])
        except:
            raise serializers.ValidationError({'error': 'Invalid Token'})

        data = {
            'access_token': f'Bearer {str(refresh_token.access_token)}',
            'refresh_token': str(refresh_token),
        }
        return data


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('social_id', 'social_type', 'email', 'phone', 'created_at', 'last_login')
        read_only_fields = ('social_id', 'social_type', 'email', 'created_at', 'last_login')


class UserInfoPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('phone',)
