from django.contrib import admin
from .forms import *


class ProfInstituteInLine(admin.TabularInline):
    model = ProfessorProfile.institute.through


class DeanInstituteInLine(admin.TabularInline):
    model = DeaneryProfile.institute.through


@admin.register(DeaneryProfile)
class DeaneryAdmin(admin.ModelAdmin):
    inlines = (DeanInstituteInLine, )
    exclude = ('institute', )


@admin.register(ProfessorProfile)
class ProfessorAdmin(admin.ModelAdmin):
    inlines = (ProfInstituteInLine, )
    exclude = ('institute', )


admin.site.register(User, MyUserAdmin)
admin.site.register(StudentProfile)
