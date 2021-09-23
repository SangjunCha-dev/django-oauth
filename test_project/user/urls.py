from django.urls import path
from user import views
urlpatterns = [
    path('user/kakao/login/', views.kakao_login, name='kakao_login'),
    path('user/kakao/callback/', views.kakao_callback, name='kakao_callback'),
    path('user/kakao/login/finish/', views.KakaoLogin.as_view(), name='kakao_login_todjango'),
]