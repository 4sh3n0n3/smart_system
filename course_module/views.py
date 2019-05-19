from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action

from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


from course_module.helpers import delete_request, reject_request, accept_request
from user_module.permissions import OnlyStudentCanCreate, ProfessorPermission
from course_module.filters import ContainerFilterSet, RequestFilterSet, CourseCardFilterSet
from .models import CourseContainer, CourseRequest, ContainerToCourse
from .serializers import (ShortCourseContainerSerializer,
                          CourseRequestSerializer, ExtendedCourseRequestSerializer,
                          ProfessorUpdateRelationSerializer, RelationSerializer, RelationWithExtendedCourseSerializer)
from django_filters import rest_framework as filters


class CourseCardViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = ContainerToCourse.objects.all()
    serializer_class = RelationSerializer
    filterset_class = CourseCardFilterSet
    filter_backends = (filters.DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RelationWithExtendedCourseSerializer
        return super().get_serializer_class()


class CourseContainerViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = CourseContainer.objects.all()
    serializer_class = ShortCourseContainerSerializer
    filterset_class = ContainerFilterSet
    filter_backends = (filters.DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)


class CourseRequestViewSet(ListModelMixin, RetrieveModelMixin,
                           CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = CourseRequest.objects.all()
    serializer_class = ExtendedCourseRequestSerializer
    permission_classes = (OnlyStudentCanCreate,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RequestFilterSet

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role is 'student':
            return queryset.filter(id__in=self.request.user.student_course_requests.values_list('id'))
        if self.request.user.role is 'professor':
            professor_courses_detail = self.request.user.professor_course_head_relations
            return queryset.filter(active_course_id__in=professor_courses_detail.values_list('course_id'))
        return queryset

    def get_serializer_class(self):
        role = self.request.user.role
        if role is 'student':
            return ExtendedCourseRequestSerializer
        if role is 'professor':
            return CourseRequestSerializer
        else:
            return CourseRequestSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data="[]", status=status.HTTP_201_CREATED, headers=headers)

    def perform_destroy(self, instance):
        delete_request(instance)
        return Response(data="[]", status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, permission_classes=(ProfessorPermission,))
    def accept_request(self, request):
        course_request = get_object_or_404(self.get_queryset(), id=request.data.get('id', None))
        course_request = accept_request(course_request)
        serializer = self.get_serializer(course_request)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, permission_classes=(ProfessorPermission,))
    def reject_request(self, request):
        course_request = get_object_or_404(self.get_queryset(), id=request.data.get('id', None))
        course_request = reject_request(course_request)
        serializer = self.get_serializer(course_request)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ContainerRelationViewSet(UpdateModelMixin, GenericViewSet):
    queryset = ContainerToCourse.objects.all()
    serializer_class = ProfessorUpdateRelationSerializer
    permission_classes = (ProfessorPermission,)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(heads=self.request.user)
