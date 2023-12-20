from rest_framework import viewsets

from users.models import User
from users.seriliazers import UserSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
