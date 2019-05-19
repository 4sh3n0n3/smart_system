from django.db import migrations


def forwards_func(apps, schema_editor):
    migrate_permissions(apps, schema_editor, forward=True)


def reverse_func(apps, schema_editor):
    migrate_permissions(apps, schema_editor, forward=False)


class Migration(migrations.Migration):
    dependencies = [
        ('user_module', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]


def migrate_permissions(apps, schema_editor, forward=True):
    User = apps.get_model('user_module', 'User')
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ct = ContentType.objects.get_for_model(User)

    if forward:
        students, created = Group.objects.get_or_create(name='Students')
        professors, created = Group.objects.get_or_create(name='Professors')
        deanery_workers, created = Group.objects.get_or_create(name='Deanery_Workers')

        students_permissions = Permission.objects.create(codename='student_permissions',
                                                         name='Permissions for all Students',
                                                         content_type=ct)
        professors_permissions = Permission.objects.create(codename='professor_permissions',
                                                           name='Permissions for all Professors',
                                                           content_type=ct)
        deanery_workers_permissions = Permission.objects.create(codename='deanery_worker_permissions',
                                                                name='Permissions for all Deanery Workers',
                                                                content_type=ct)
        Permission.objects.create(codename='deanery_recruitment_creator',
                                  name='Permissions for creating recruitment plans',
                                  content_type=ct)

        students.permissions.add(students_permissions)
        professors.permissions.add(professors_permissions)
        deanery_workers.permissions.add(deanery_workers_permissions)
    else:
        students = Group.objects.get(name='Students')
        professors = Group.objects.get(name='Professors')
        deanery_workers = Group.objects.get(name='Deanery_Workers')

        students_permissions = Permission.objects.get(codename='student_permissions',
                                                      content_type=ct)
        professors_permissions = Permission.objects.get(codename='professor_permissions',
                                                        content_type=ct)
        deanery_workers_permissions = Permission.objects.get(codename='deanery_worker_permissions',
                                                             content_type=ct)

        students.permissions.remove(students_permissions)
        professors.permissions.remove(professors_permissions)
        deanery_workers.permissions.remove(deanery_workers_permissions)

        Permission.objects.get(codename='deanery_recruitment_creator',
                               content_type=ct).delete()
        students_permissions.delete()
        professors_permissions.delete()
        deanery_workers_permissions.delete()
