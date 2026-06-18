from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminRole(BasePermission):
    """Разрешение только для пользователей с ролью admin."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Проверяет наличие роли admin у пользователя.

        Args:
            request: HTTP-запрос с данными пользователя.
            view: Представление, к которому обращаются.
        """
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.roles.filter(name='admin').exists()
        )


class IsAdminOrTeacher(BasePermission):
    """Разрешение для пользователей с ролью admin или teacher."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Проверяет наличие роли admin или teacher у пользователя.

        Args:
            request: HTTP-запрос с данными пользователя.
            view: Представление, к которому обращаются.
        """
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.roles.filter(name__in=['admin', 'teacher']).exists()
        )


class IsAdminOrTeacherOrReadOnly(BasePermission):
    """Безопасные методы доступны всем; небезопасные — только admin или teacher."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Разрешает GET/HEAD/OPTIONS всем, остальные методы — admin и teacher.

        Args:
            request: HTTP-запрос с данными пользователя.
            view: Представление, к которому обращаются.
        """
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.roles.filter(name__in=['admin', 'teacher']).exists()
        )


class IsOwnerOrAdminOrTeacher(BasePermission):
    """Разрешение для владельца объекта или пользователей с ролью admin/teacher."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Проверяет, что пользователь аутентифицирован.

        Args:
            request: HTTP-запрос с данными пользователя.
            view: Представление, к которому обращаются.
        """
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request: Request, view: APIView, obj: object) -> bool:
        """
        Проверяет, является ли пользователь владельцем объекта или имеет роль admin/teacher.

        Args:
            request: HTTP-запрос с данными пользователя.
            view: Представление, к которому обращаются.
            obj: Объект, к которому запрашивается доступ.
        """
        if request.user.roles.filter(name__in=['admin', 'teacher']).exists():
            return True
        return obj.user == request.user