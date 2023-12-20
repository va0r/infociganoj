from rest_framework import permissions

from users.models import UserRoles


class IsModerator(permissions.BasePermission):
    message = 'Внести изменения может только модератор'

    def has_permission(self, request, view):
        if request.user.role == UserRoles.MODERATOR:
            # разрешаем только методы GET и PUT/PATCH
            return request.method in ['GET', 'PUT', 'PATCH']


class IsOwner(permissions.BasePermission):
    message = 'Вы не являетесь владельцем'

    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner:
            return True
        return False
