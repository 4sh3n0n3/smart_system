from django.db import models
from eITIS.enums import GROUP_TYPE


class Institute(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Институт"

    def __str__(self):
        return "{}".format(self.name)


class Faculty(models.Model):
    name = models.CharField(max_length=200)
    spec_number = models.CharField(max_length=20)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='faculties')

    class Meta:
        verbose_name_plural = "Факультет"

    def __str__(self):
        return "{}, {}".format(self.institute.name, self.name)


class StudyGroup(models.Model):
    group_number = models.CharField(max_length=15, unique=True)
    start_year = models.DateField()
    study_form = models.SmallIntegerField(choices=GROUP_TYPE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='groups')

    def __str__(self):
        return "{}".format(self.group_number)

    class Meta:
        verbose_name_plural = "Студенческие группы"
