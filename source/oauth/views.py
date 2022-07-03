import requests
import jwt
import time

from django.conf import settings
from django.shortcuts import redirect
from django.middleware.csrf import get_token
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from users.models import UserModel
from users.views import LoginView, UserView


def login_api(social_type: str, social_id: str, email: str=None, phone: str=None):
    '''
    회원가입 및 로그인
    '''
    login_view = LoginView()
    try:
        UserModel.objects.get(social_id=social_id)
        data = {
            'social_id': social_id,
            'email': email,
        }
        response = login_view.object(data=data)

    except UserModel.DoesNotExist:
        data = {
            'social_type': social_type,
            'social_id': social_id,
            'email': email,
        }
        user_view = UserView()
        login = user_view.get_or_create_user(data=data)

        response = login_view.object(data=data) if login.status_code == 201 else login

    return response


kakao_login_uri = "https://kauth.kakao.com/oauth/authorize"
kakao_token_uri = "https://kauth.kakao.com/oauth/token"
kakao_profile_uri = "https://kapi.kakao.com/v2/user/me"

class KakaoLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        '''
        kakao code 요청

        ---
        '''
        client_id = settings.KAKAO_REST_API_KEY
        redirect_uri = settings.KAKAO_REDIRECT_URI
        uri = f"{kakao_login_uri}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        
        res = redirect(uri)
        return res


class KakaoCallbackView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(query_serializer=CallbackUserInfoSerializer)
    def get(self, request):
        '''
        kakao access_token 및 user_info 요청

        ---
        '''
        data = request.query_params

        # access_token 발급 요청
        code = data.get('code')
        if not code:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        request_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.KAKAO_REST_API_KEY,
            'redirect_uri': settings.KAKAO_REDIRECT_URI,
            'client_secret': settings.KAKAO_CLIENT_SECRET_KEY,
            'code': code,
        }
        token_headers = {
            'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        token_res = requests.post(kakao_token_uri, data=request_data, headers=token_headers)

        token_json = token_res.json()
        access_token = token_json.get('access_token')

        if not access_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        access_token = f"Bearer {access_token}"  # 'Bearer ' 마지막 띄어쓰기 필수

        # kakao 회원정보 요청
        auth_headers = {
            "Authorization": access_token,
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        user_info_res = requests.get(kakao_profile_uri, headers=auth_headers)
        user_info_json = user_info_res.json()

        social_type = 'kakao'
        social_id = f"{social_type}_{user_info_json.get('id')}"

        kakao_account = user_info_json.get('kakao_account')
        if not kakao_account:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user_email = kakao_account.get('email')

        # 회원가입 및 로그인
        res = login_api(social_type=social_type, social_id=social_id, email=user_email)
        return res


naver_login_url = "https://nid.naver.com/oauth2.0/authorize"
naver_token_url = "https://nid.naver.com/oauth2.0/token"
naver_profile_url = "https://openapi.naver.com/v1/nid/me"

class NaverLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        '''
        naver code 요청

        ---
        '''
        client_id = settings.NAVER_CLIENT_ID
        redirect_uri = settings.NAVER_REDIRECT_URI
        state = settings.STATE
        # state = get_token(request)

        uri = f"{naver_login_url}?client_id={client_id}&redirect_uri={redirect_uri}&state={state}&response_type=code"
        res = redirect(uri)
        return res


class NaverCallbackView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(query_serializer=CallbackUserCSRFInfoSerializer)
    def get(self, request):
        '''
        naver access_token 및 user_info 요청

        ---
        '''
        data = request.query_params

        # access_token 발급 요청
        code = data.get('code')
        user_state = data.get('state')
        if (not code) or (user_state != settings.STATE):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        request_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.NAVER_CLIENT_ID,
            'client_secret': settings.NAVER_CLIENT_SECRET,
            'code': code,
            'state': user_state,
        }
        token_headers = {
            'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        token_res = requests.post(naver_token_url, data=request_data, headers=token_headers)

        token_json = token_res.json()
        access_token = token_json.get('access_token')

        if not access_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        access_token = f"Bearer {access_token}"  # 'Bearer ' 마지막 띄어쓰기 필수

        # naver 회원정보 요청
        auth_headers = {
            "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
            "Authorization": access_token,
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        user_info_res = requests.get(naver_profile_url, headers=auth_headers)
        user_info_json = user_info_res.json()
        user_info = user_info_json.get('response')
        if not user_info:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        social_type = 'naver'
        social_id = f"{social_type}_{user_info.get('id')}"
        user_email = user_info.get('email')

        # 회원가입 및 로그인
        res = login_api(social_type=social_type, social_id=social_id, email=user_email)
        return res


google_login_url = "https://accounts.google.com/o/oauth2/v2/auth"
google_scope = "https://www.googleapis.com/auth/userinfo.email"
google_token_url = "https://oauth2.googleapis.com/token"
google_profile_url = "https://www.googleapis.com/oauth2/v2/tokeninfo"

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        '''
        google code 요청

        ---
        '''
        client_id = settings.GOOGLE_CLIENT_ID
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        uri = f"{google_login_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope={google_scope}&response_type=code"

        res = redirect(uri)
        return res


class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(query_serializer=CallbackUserInfoSerializer)
    def get(self, request):
        '''
        google access_token 및 user_info 요청

        ---
        '''
        data = request.query_params

        # access_token 발급 요청
        code = data.get('code')
        if not code:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        request_data = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        }
        token_res = requests.post(google_token_url, data=request_data)

        token_json = token_res.json()
        access_token = token_json['access_token']

        if not access_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # google 회원정보 요청
        query_string = {
            'access_token': access_token
        }
        user_info_res = requests.get(google_profile_url, params=query_string)
        user_info_json = user_info_res.json()
        if (user_info_res.status_code != 200) or (not user_info_json):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        social_type = 'google'
        social_id = f"{social_type}_{user_info_json.get('user_id')}"
        user_email = user_info_json.get('email')

        # 회원가입 및 로그인
        res = login_api(social_type=social_type, social_id=social_id, email=user_email)
        return res


facebook_graph_url = "https://graph.facebook.com/v12.0"
facebook_login_url = "https://www.facebook.com/v12.0/dialog/oauth"
facebook_token_url = f"{facebook_graph_url}/oauth/access_token"  
facebook_debug_token_url = "https://graph.facebook.com/debug_token"
facebook_profile_url = f"{facebook_graph_url}/me"  # 사용자 정보 요청

class FacebookLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, reqeust):
        '''
        facebook code 요청

        ---
        '''
        client_id = settings.FACEBOOK_APP_ID
        redirect_uri = settings.FACEBOOK_REDIRECT_URI
        state = settings.STATE

        uri = f"{facebook_login_url}?client_id={client_id}&redirect_uri={redirect_uri}&state={state}&response_type=code&scope=email%20public_profile"

        res = redirect(uri)
        return res


class FacebookCallbackView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(query_serializer=CallbackUserInfoSerializer)
    def get(self, request):
        '''
        facebook access_token 및 user_info 요청

        ---
        '''
        data = request.query_params

        code = data.get('code')
        if not code:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        query_string = {
            'client_id': settings.FACEBOOK_APP_ID,
            'redirect_uri': settings.FACEBOOK_REDIRECT_URI,
            'client_secret': settings.FACEBOOK_APP_SECRET,
            'code': code,
        }
        token_res = requests.get(facebook_token_url, params=query_string)

        token_json = token_res.json()
        access_token = token_json.get('access_token')

        if not access_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # 엑세스 토큰 검사 및 계정 정보 조회
        query_string = {
            'input_token': access_token,
            'access_token': f"{settings.FACEBOOK_APP_ID}|{settings.FACEBOOK_APP_SECRET}",
        }
        user_info_res = requests.get(facebook_debug_token_url, params=query_string)
        user_info_json = user_info_res.json()

        facebook_account = user_info_json.get('data')
        if (not facebook_account) or (not facebook_account.get('is_valid')):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_id = facebook_account.get('user_id')

        query_string = {
            'fields': 'email', # email,name 형식으로 사용가능
            'access_token': access_token,
        }
        user_profile_res = requests.get(facebook_profile_url, params=query_string)
        user_profile_json = user_profile_res.json()

        social_type = 'facebook'
        social_id = f"{social_type}_{user_id}"
        user_email = user_profile_json.get('email')

        # 회원가입 및 로그인
        res = login_api(social_type=social_type, social_id=social_id, email=user_email)
        return res


apple_base_url = "https://appleid.apple.com"
apple_auth_url = f"{apple_base_url}/auth/authorize"
apple_token_url = f"{apple_base_url}/auth/token"

class AppleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, reqeust):
        '''
        apple code 요청

        ---
        '''
        # APPLE_CLIENT_ID는 모바일 로그인시 Bundle ID, 웹 로그인시 Service ID를 사용한다.
        client_id = settings.APPLE_CLIENT_ID
        redirect_uri = settings.APPLE_REDIRECT_URI

        uri = f"{apple_auth_url}?client_id={client_id}&&redirect_uri={redirect_uri}&response_type=code"

        res = redirect(uri)
        return res


class AppleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get_key_and_secret(self):
        '''
        CLIENT_SECRET 생성
        '''
        headers = {
            'alg': 'ES256',
            'kid': settings.APPLE_KEY_ID,
        }

        payload = {
            'iss': settings.APPLE_TEAM_ID,
            'iat': time.time(),
            'exp': time.time() + 600,  # 10분
            'aud': apple_base_url,
            'sub': settings.APPLE_CLIENT_ID,
        }

        client_secret = jwt.encode(
            payload=payload, 
            key=settings.APPLE_PRIVATE_KEY, 
            algorithm='ES256', 
            headers=headers
        )

        return client_secret

    @swagger_auto_schema(query_serializer=CallbackAppleInfoSerializer)
    def get(self, request):
        '''
        apple id_token 및 user_info 조회

        ---
        '''
        data = request.query_params
        code = data.get('code')
        # id_token 서명 복호화시 에러로 검증할 수 없어 자체 발급한 id_token만 사용

        # CLIENT_SECRET 생성
        client_secret = self.get_key_and_secret()

        headers = {'Content-type': "application/x-www-form-urlencoded"}
        request_data = {
            'client_id': settings.APPLE_CLIENT_ID,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.APPLE_REDIRECT_URI,
        }
        # client_secret 유효성 검사
        res = requests.post(apple_token_url, data=request_data, headers=headers)
        response_json = res.json()
        id_token = response_json.get('id_token')
        if not id_token:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # 백엔드 자체적으로 id_token 발급받은 경우 서명을 검증할 필요 없음
        token_decode = jwt.decode(id_token, '', options={"verify_signature": False})
        # sub : (subject) is the unique user id
        # email : is the email address of the user

        if (not token_decode.get('sub')) or (not token_decode.get('email')) or (not token_decode.get('email_verified')):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Apple에서 받은 id_token에서 sub, email 조회
        social_type = 'apple'
        social_id = f"{social_type}_{token_decode['sub']}"
        user_email = token_decode['email']

        # 회원가입 및 로그인
        res = login_api(social_type=social_type, social_id=social_id, email=user_email)
        return res


class AppleEndpoint(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        '''
        apple 사용자 정보수정

        ---
        이메일 변경, 서비스 해지, 계정 탈퇴에 대한 정보를 받는용
        '''
        data = request.data

        response = Response(status=status.HTTP_200_OK)
        return response
