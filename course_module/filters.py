from datetime import datetime

from django_filters import FilterSet, filters, ModelChoiceFilter, NumberFilter, BooleanFilter

from course_module.models import CourseContainer, CourseRequest, ContainerToCourse, Course, ContainerToGroup
from study_group_module.models import StudyGroup


class ContainerFilterSet(FilterSet):
    class Meta:
        model = CourseContainer
        fields = {
            'id': ('in', ),
            'courses__id': ('in', 'exact')
        }


class RequestFilterSet(FilterSet):
    course = NumberFilter(method='filter_by_course')
    container = NumberFilter(method='filter_by_container')

    class Meta:
        model = CourseRequest
        fields = {
            'active_course': ('in', ),
        }

    def filter_by_course(self, queryset, name, value):
        today = datetime.today()
        if today.month > 8:
            groups = StudyGroup.objects.filter(start_year=datetime(today.year - value + 1, 9, 1))
        else:
            groups = StudyGroup.objects.filter(start_year=datetime(today.year - value, 9, 1))
        courses = Course.objects.filter(containers__container_group_relations__group__in=groups)
        return queryset.filter(active_course__course__in=courses)

    def filter_by_container(self, queryset, name, value):
        return queryset.filter(active_course__container=value)


class CourseCardFilterSet(FilterSet):
    my = BooleanFilter(method='filter_my')
    course = NumberFilter(method='filter_by_course')

    class Meta:
        model = ContainerToCourse
        fields = ('course__institutes', 'container', 'container__status', 'my')

    def filter_by_course(self, queryset, name, value):
        # ToDo: когда в модели будет храниться номер курса, переделать
        today = datetime.today()
        if today.month > 8:
            groups = StudyGroup.objects.filter(start_year=datetime(today.year - value + 1, 9, 1))
        else:
            groups = StudyGroup.objects.filter(start_year=datetime(today.year - value, 9, 1))
        return queryset.filter(
            container__container_group_relations__group__in=groups
        ).distinct()

    def filter_my(self, queryset, name, value):
        if not value:
            return queryset
        if self.request.user.role is 'student':
            return queryset.filter(container__groups=self.request.user.student_profile.group).distinct()
        if self.request.user.role is 'professor':
            return queryset.filter(heads=self.request.user).distinct()
        return queryset
