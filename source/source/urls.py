"""source URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin 
from django.urls import path, include, re_path
from django.conf import settings
from rest_framework.permissions import AllowAny
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.generators import OpenAPISchemaGenerator


urlpatterns = [
    path('admin/', admin.site.urls),
    path('oauth/', include('oauth.urls')),
    path('users/', include('users.urls', namespace='users')),
]

# 디버그일때 swagger api 실행
if settings.DEBUG:
    # Schemes HTTPS 버튼 추가
    class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
        def get_schema(self, request=None, public=False):
            schema = super().get_schema(request, public)
            schema.schemes = ["http", "https"]
            return schema

    schema_view = get_schema_view(
        openapi.Info(
            title="Open API Swagger Test",
            default_version='v1',
            description="시스템 API Description",
            # reah_of_service="',
            # contact=openapi.Contact(name="test", email="test@test.test'), 
            # license=openapi.License(name="Test License'), 
        ),
        public=True,
        generator_class=BothHttpAndHttpsSchemaGenerator,
        permission_classes=(AllowAny,),
    )

    urlpatterns += [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]