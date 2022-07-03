from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [ 
    path('', UserView.as_view(), name='user'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
