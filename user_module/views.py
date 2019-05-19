from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from user_module.models import User
from user_module.serializers import UserSerializer, StudentSerializer, ProfessorSerializer, \
    ChangePasswordSerializer


class UserViewSet(RetrieveModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = UserSerializer

    def _get_serializer_class(self, user_obj):
        role = user_obj.role
        if role is 'student':
            return StudentSerializer
        elif role is 'professor':
            return ProfessorSerializer
        else:
            return UserSerializer

    def get_serializer_class(self):
        return self._get_serializer_class(self.get_object())
        
    @action(detail=False)
    def current_user(self, request):
        if request.user.is_anonymous:
            return Response({}, status=status.HTTP_200_OK)
        else:
            serializer_class = self._get_serializer_class(request.user)
            serializer = serializer_class(request.user)
            return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data,
                                              context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({}, status=status.HTTP_200_OK)
