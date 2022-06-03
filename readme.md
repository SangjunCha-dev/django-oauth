# django oauth

`django rest framework`의 APIView와 `drf-yasg`를 이용한 swagger API로 oauth 테스트 구현 

# Setting

## 1. 가상환경 생성 및 접속

```
> python -m venv venv
> venv\Scripts\activate
```

## 2. 라이브러리 설치

```bash
(venv)> pip install -U pylint
(venv)> pip install django

# restframework
(venv)> pip install djangorestframework
(venv)> pip install djangorestframework-simplejwt

# oauth
(venv)> pip install requests
(venv)> pip install pyjwt[crypto]

# swagger
(venv)> pip install drf-yasg
```

## 3. oauth 사이트 설정 및 설명

- [Django 소셜로그인(oauth) kakao 연동](https://sangjuncha-dev.github.io/posts/framework/django/2021-10-11-django-oauth-kakao/)
- [Django 소셜로그인(oauth) naver 연동](https://sangjuncha-dev.github.io/posts/framework/django/2021-11-12-django-oauth-naver/)
- [Django 소셜로그인(oauth) google 연동](https://sangjuncha-dev.github.io/posts/framework/django/2021-11-22-django-oauth-google/)
- [Django 소셜로그인(oauth) facebook 연동](https://sangjuncha-dev.github.io/posts/framework/django/2021-12-29-django-oauth-facebook/)
- [Django 소셜로그인(oauth) apple 연동](https://sangjuncha-dev.github.io/posts/framework/django/2021-12-28-django-oauth-apple/)

## 4. 서버 실행

```
python manage.py runserver localhost:8000
```

## 5. client 테스트

- 설정파일에 지정한 oauth의 `REDIRECT_URI`주소로 웹브라우저로 접속한다.
- oauth 로그인이 정상적으로 완료되면 `{"social_id": ..., "access_token": ..., "refresh_token": ...}` 값이 반환된다.
- `http://localhost:8000/swagger/` 접속하여 우측상단에 `Authorize`버튼 클릭한다.
- 방금전에 발급받은 `access_token`을 입력하고 `Authorize`버튼 클릭한다.
- users의 `GET /users/info/` 요청을 전송하면 사용자의 정보가 출력된다.