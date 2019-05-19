from django.contrib import admin
from .models import *


class InstituteInLine(admin.TabularInline):
    model = Course.institutes.through


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = (InstituteInLine, )
    exclude = ('institutes', )


class GroupsInLine(admin.TabularInline):
    model = CourseContainer.groups.through


class CoursesInLine(admin.TabularInline):
    model = CourseContainer.courses.through


class HeadsInLine(admin.TabularInline):
    model = ContainerToCourse.heads.through


@admin.register(ContainerToCourse)
class RelationAdmin(admin.ModelAdmin):
    inlines = (HeadsInLine, )
    exclude = ('heads', )


@admin.register(CourseContainer)
class ContainerAdmin(admin.ModelAdmin):
    inlines = (GroupsInLine, CoursesInLine, )
    exclude = ('groups', 'courses', )


admin.site.register(CourseRequest)
admin.site.register(CourseMediaFilesLinks)
