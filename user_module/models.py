from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete, m2m_changed
from django.dispatch import receiver
from eITIS.enums import *
from study_group_module.models import Institute, StudyGroup


def get_only_students_q():
    return Q(groups__name='Students')


def get_only_professors_q():
    return Q(groups__name='Professors')


def get_only_deanery_workers_q():
    return Q(groups__name='Deanery_Workers')


class User(AbstractUser):
    middle_name = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='avatars', blank=True)

    def __str__(self):
        return "{} {} {}".format(self.first_name, self.last_name, self.middle_name)

    class Meta:
        verbose_name_plural = "Пользователи"

    @property
    def full_name(self):
        return str(self)

    @property
    def role(self):
        if self.groups.filter(name='Students').exists():
            return 'student'
        elif self.groups.filter(name='Professors').exists():
            return 'professor'
        elif self.groups.filter(name='Deanery_Workers').exists():
            return 'deanery'
        return None


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, limit_choices_to=get_only_students_q,
                                related_name='student_profile', unique=True)
    group = models.ForeignKey(StudyGroup, on_delete=models.DO_NOTHING, related_name='group_students', blank=True,
                              null=True)

    score = models.FloatField(blank=True, default=0.0)

    def __str__(self):
        if self.group:
            return "{} add. data".format(str(self.user))
        else:
            return "{} add. data (unassigned)".format(str(self.user))

    class Meta:
        verbose_name_plural = "Профили студентов"

    def clean(self):
        if StudyGroup.objects.filter(group_students__user=self.user):
            raise ValidationError(message='Студент уже состоит в группе')

    @receiver(m2m_changed, sender=User.groups.through)
    def create_or_update_student_profile(sender, instance, action, **kwargs):
        if action == 'post_add':
            is_student = instance.groups.filter(name='Students').exists()
            if is_student:
                StudentProfile.objects.create(user=instance)

    @receiver(pre_delete, sender=User)
    def delete_student_profile(sender, instance, **kwargs):
        is_student = instance.groups.filter(name='Students').exists()
        if is_student:
            instance.student_profile.delete()


class ProfessorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, limit_choices_to=get_only_professors_q,
                                related_name='professor_profile', unique=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    academic_title = models.CharField(max_length=100, blank=True, null=True)
    office = models.CharField(max_length=200, blank=True, null=True)
    institute = models.ManyToManyField(Institute, related_name='professor_profiles')

    def __str__(self):
        if self.position or self.academic_title or self.office:
            return "{} add. data".format(str(self.user))
        else:
            return "{} add. data (unassigned)".format(str(self.user))

    class Meta:
        verbose_name_plural = "Профили профессоров"

    @receiver(m2m_changed, sender=User.groups.through)
    def create_or_update_professor_profile(sender, instance, action, **kwargs):
        if action == 'post_add':
            is_professor = instance.groups.filter(name='Professors').exists()
            if is_professor:
                ProfessorProfile.objects.create(user=instance)

    @receiver(pre_delete, sender=User)
    def delete_professor_profile(sender, instance, **kwargs):
        is_professor = instance.groups.filter(name='Professors').exists()
        if is_professor:
            instance.professor_profile.delete()


class DeaneryProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, limit_choices_to=get_only_deanery_workers_q,
                                related_name='deanery_profile', unique=True)
    institute = models.ManyToManyField(Institute, related_name='deanery_workers_profiles')

    def __str__(self):
        if self.institute:
            return "{} add. data".format(str(self.user))
        else:
            return "{} add. data (unassigned)".format(str(self.user))

    class Meta:
        verbose_name_plural = "Профили сотрудников деканата"

    @receiver(m2m_changed, sender=User.groups.through)
    def create_or_update_deanery_profile(sender, instance, action, **kwargs):
        if action == 'post_add':
            is_deanery = instance.groups.filter(name='Deanery_Workers').exists()
            if is_deanery:
                DeaneryProfile.objects.create(user=instance)

    @receiver(pre_delete, sender=User)
    def delete_deanery_profile(sender, instance, **kwargs):
        is_deanery = instance.groups.filter(name='Deanery_Workers').exists()
        if is_deanery:
            instance.deanery_profile.delete()
