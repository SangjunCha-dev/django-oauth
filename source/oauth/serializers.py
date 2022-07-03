from rest_framework import serializers


class CallbackUserInfoSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=1000, required=False, help_text="접속 코드 (Web)")
    access_token = serializers.CharField(max_length=1000, required=False, help_text="토큰 (Mobile)")


class CallbackUserCSRFInfoSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=1000, required=False, help_text="접속 코드(Web)")
    state = serializers.CharField(max_length=500, required=False, help_text="웹 CSRF 방지 문자열(Web)")
    access_token = serializers.CharField(max_length=1000, required=False, help_text="토큰 (Mobile)")


class CallbackAppleInfoSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=1000, required=False, help_text="접속 코드(Web)")
