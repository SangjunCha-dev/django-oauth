from django.urls import path

from .views import *


urlpatterns = [
    path('kakao/login/', KakaoLoginView.as_view()),
    path('kakao/login/callback/', KakaoCallbackView.as_view()),

    path('naver/login/', NaverLoginView.as_view()),
    path('naver/login/callback/', NaverCallbackView.as_view()),

    path('google/login/', GoogleLoginView.as_view()),
    path('google/login/callback/', GoogleCallbackView.as_view()),

    path('facebook/login/', FacebookLoginView.as_view()),
    path('facebook/login/callback/', FacebookCallbackView.as_view()),

    path('apple/login/', AppleLoginView.as_view()),
    path('apple/login/callback/', AppleCallbackView.as_view()),
    path('apple/endpoint/', AppleEndpoint.as_view()),
]