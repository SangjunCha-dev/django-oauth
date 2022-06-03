
from django.contrib.auth.backends import BaseBackend

from users.models import UserModel


class SettingsBackend(BaseBackend):
    def authenticate(self, request, social_id=None):
        user = None
        try:
            user = UserModel.objects.get(social_id=social_id)
        except UserModel.DoesNotExist:
            pass
        return user

    def get_user(self, social_id):
        user = None
        try:
            user = UserModel.objects.get(social_id=social_id)
        except UserModel.DoesNotExist:
            pass
        return user
