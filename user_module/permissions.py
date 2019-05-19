from rest_framework.permissions import IsAuthenticated


class OnlyStudentCanCreate(IsAuthenticated):
    def has_permission(self, request, view):
        res = super().has_permission(request, view)
        if not res:
            return res
        else:
            if request.method == 'POST' and (not request.user.role or request.user.role != 'student'):
                return False
        return True


class ProfessorPermission(IsAuthenticated):
    def has_permission(self, request, view):
        res = super().has_permission(request, view)
        if not res:
            return res
        else:
            return request.user.role is 'professor'
