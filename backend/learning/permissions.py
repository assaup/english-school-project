from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminRole(BasePermission):
    """Разрешает доступ только пользователям с ролью 'admin'."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.roles.filter(name='admin').exists()
        )


class IsAdminOrTeacher(BasePermission):
    """Разрешает доступ пользователям с ролью 'admin' или 'teacher'."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.roles.filter(name__in=['admin', 'teacher']).exists()
        )


class IsAdminOrTeacherOrReadOnly(BasePermission):
    """SAFE_METHODS — всем; небезопасные методы — только admin или teacher."""

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.roles.filter(name__in=['admin', 'teacher']).exists()
        )


class IsOwnerOrAdminOrTeacher(BasePermission):
    """Доступ к объекту: его владелец, пользователь с ролью admin или teacher."""

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.roles.filter(name__in=['admin', 'teacher']).exists():
            return True
        return obj.user == request.user
