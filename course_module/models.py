from django.db import models
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError

from user_module.models import User
from study_group_module.models import Institute, StudyGroup
from eITIS.enums import *
import datetime

now = datetime.datetime.now()


def get_workers_with_unit_creating_permission_q():
    return Q(user_permissions__codename='deanery_recruitment_creator')


def get_only_students_q():
    return Q(groups__name='Students')


def get_sentinel_user():
    return User.objects.get_or_create(username='deleted')[0]


def get_only_professors_q():
    return Q(groups__name='Professors')


class Course(models.Model):
    name = models.CharField(max_length=100, unique=True)
    requirements = models.TextField(blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(blank=True, upload_to='uploads')
    institutes = models.ManyToManyField(Institute, related_name='courses', through='CourseToInstitute')
    containers = models.ManyToManyField(through='ContainerToCourse', to='CourseContainer')

    @property
    def logo_path(self):
        return self.logo.name

    class Meta:
        verbose_name_plural = "Курсы по выбору"

    def __str__(self):
        return "{}".format(self.name)


class CourseToInstitute(models.Model):
    course = models.ForeignKey(Course, related_name='course_institute_relations', on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, related_name='institute_course_relations', on_delete=models.CASCADE)


class CourseContainer(models.Model):
    name = models.CharField(max_length=100)
    courses = models.ManyToManyField(Course, through="ContainerToCourse", related_name="course_containers")
    groups = models.ManyToManyField(StudyGroup, through='ContainerToGroup', related_name='group_containers')
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='containers',
                                   limit_choices_to=get_workers_with_unit_creating_permission_q)
    start_date = models.DateTimeField()
    expiration_date = models.DateTimeField()
    status = models.SmallIntegerField(choices=CONTAINER_STATUS, default=0)

    class Meta:
        unique_together = ('name', 'created_at')
        verbose_name_plural = "Наборы курсов"
        ordering = ["created_at"]
        get_latest_by = ["crated_at"]

    def __str__(self):
        return "{}, от {}. Создатель: {}".format(str(self.name), self.created_at, str(self.created_by))

    def clean(self):
        if not self.created_by.has_perm('user_module.deanery_recruitment_creator'):
            raise ValidationError(message='Пользователь не имеет прав на создание набора')

    @property
    def readable_status(self):
        for index in range(0, len(CONTAINER_STATUS)):
            if CONTAINER_STATUS[index][0] == self.status:
                return CONTAINER_STATUS[index][1]


class CourseRequest(models.Model):
    status = models.SmallIntegerField(choices=REQUEST_STATUS, default=0)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, limit_choices_to=get_only_students_q,
                                on_delete=models.CASCADE, related_name='student_course_requests')
    active_course = models.ForeignKey("ContainerToCourse", on_delete=models.CASCADE, related_name='requests')
    # course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_requests')
    # container = models.ForeignKey(CourseContainer, on_delete=models.CASCADE, related_name='container_requests')

    class Meta:
        unique_together = ('student', 'active_course')
        verbose_name_plural = "Заявки на курсы по выбору"

    def clean(self):
        if not self.student.has_perm('user_module.student_permissions'):
            raise ValidationError(message='Пользователь должен быть студентом чтобы подать заявку')
        if self.active_course.course not in Course.objects.filter(containers=self.active_course.container):
            raise ValidationError(message='Данная активность не принадлежит выбранному набору')
        if self.student.student_profile.group not in StudyGroup.objects.filter(
                group_relations__container=self.active_course.container):
            raise ValidationError(message='У данного студента нет такого набора')

    def __str__(self):
        return "{} to {}, at {}, status: {}".format(str(self.student), str(self.active_course),
                                                    str(self.created_at), str(self.readable_status))

    @property
    def readable_status(self):
        for index in range(0, len(REQUEST_STATUS) - 1):
            if REQUEST_STATUS[index][0] == self.status:
                return REQUEST_STATUS[index][1]


class ContainerToCourse(models.Model):
    container = models.ForeignKey(CourseContainer,
                                  on_delete=models.CASCADE, related_name='container_course_relations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_container_relations')
    heads = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='courses', through='CourseHead')
    instant_accept = models.BooleanField(default=False)
    status = models.SmallIntegerField(choices=ACTIVITY_TO_CONTAINER_STATUS, default=0)
    min_quantity = models.SmallIntegerField(default=15)
    quantity = models.SmallIntegerField(null=True, blank=True)

    @property
    def accepted_requests(self):
        return CourseRequest.objects.filter(active_course=self, status=ACCEPTED).count()

    @property
    def all_requests(self):
        return CourseRequest.objects.filter(active_course=self).exclude(status=REJECTED).count()

    class Meta:
        unique_together = ('course', 'container')
        verbose_name_plural = "Связь курсов по выбору и наборов"

    def __str__(self):
        return "{}, {}. Статус: {}".format(str(self.course), str(self.container), str(self.readable_status))

    @property
    def readable_status(self):
        for index in range(0, len(ACTIVITY_TO_CONTAINER_STATUS)):
            if ACTIVITY_TO_CONTAINER_STATUS[index][0] == self.status:
                return ACTIVITY_TO_CONTAINER_STATUS[index][1]


class CourseHead(models.Model):
    curator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET(get_sentinel_user),
                                limit_choices_to=get_only_professors_q, related_name='professor_course_head_relations')
    course = models.ForeignKey(ContainerToCourse, on_delete=models.CASCADE, related_name='course_head_relations')


class ContainerToGroup(models.Model):
    group = models.ForeignKey(StudyGroup,
                              on_delete=models.CASCADE, related_name='group_relations')
    container = models.ForeignKey(CourseContainer, on_delete=models.CASCADE, related_name='container_group_relations')

    class Meta:
        unique_together = ('group', 'container')
        verbose_name_plural = "Связи групп и наборов на курсы"

    def __str__(self):
        return "Группа {}, к набору {}. (от {})".format(self.group.group_number, self.container.name,
                                                        self.container.created_at)


class CourseMediaFilesLinks(models.Model):
    file = models.FileField(upload_to='uploads', unique=True)
    name = models.CharField(max_length=100, blank=True)
    uploading_date = models.DateField(auto_now=True)
    owner = models.ForeignKey(Course, related_name='media_files', on_delete=models.CASCADE)

    @property
    def path(self):
        return self.file.path

    class Meta:
        verbose_name_plural = "Ссылки на медиа курсов"
        get_latest_by = "uploading_date"
