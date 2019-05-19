from django.db import models
from django.conf import settings
from django.db.models import Q
from eITIS.enums import *
import datetime

now = datetime.datetime.now()


def filled_docs_directory_path(instance, filename):
    return "filled_documents/{0} {1}/{2}/{3}".format(instance.student.first_name, instance.student.last_name, now.year,
                                                     filename)


def get_only_students_q():
    return Q(groups__name='Students')


def get_only_professors_q():
    return Q(groups__name='Professors')


class UserMediaFilesLinks(models.Model):
    file = models.FileField(upload_to='uploads', unique=True)
    name = models.CharField(max_length=100, blank=True)
    uploading_date = models.DateField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_media_files', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Ссылки на медиа курсов"
        get_latest_by = "uploading_date"


'''
class DocumentTemplate(models.Model):
    document_name = models.CharField(choices=DOCUMENT_KEYS, max_length=100, verbose_name="Уникальный ключ документа",
                                     unique=True)
    upload = models.FileField(upload_to='uploads/templates', unique=True, verbose_name="Файл загрузки")
    uploading_date = models.DateField(auto_now=True)

    def __str__(self):
        return "{}".format(self.document_name)

    class Meta:
        verbose_name_plural = "Шаблоны документов"


class Document(models.Model):
    template = models.ForeignKey(DocumentTemplate, on_delete=models.CASCADE, related_name='filled',
                                 verbose_name='Шаблон')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                limit_choices_to=get_only_students_q, related_name='student_documents',
                                verbose_name='Студент')
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE, related_name='practice_documents',
                                 verbose_name='Практика')
    upload = models.FileField(upload_to=filled_docs_directory_path, unique=True, verbose_name="Файл загрузки")
    uploading_date = models.DateField(auto_now=True)
    status = models.SmallIntegerField(choices=DOCUMENT_STATUS, default=0)

    def __str__(self):
        return "{0} {1}, от {2}".format(self.student.first_name, self.student.last_name, self.uploading_date)

    class Meta:
        verbose_name_plural = "Заполненные документы"
        unique_together = (("template", "student", "practice"),)
'''


class Chat(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, limit_choices_to=get_only_students_q,
                                on_delete=models.CASCADE, related_name='student_chats')
    professor = models.ForeignKey(settings.AUTH_USER_MODEL, limit_choices_to=get_only_professors_q,
                                  on_delete=models.CASCADE, related_name='professor_chats')

    class Meta:
        verbose_name_plural = "Чаты пользователей"

    def __str__(self):
        return "Chat between {} and {}".format(self.student, self.professor)


class Message(models.Model):
    message = models.TextField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_messages')
    date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Сообщения пользователей"

    def __str__(self):
        return "{}, at {}".format(self.user, self.date)
