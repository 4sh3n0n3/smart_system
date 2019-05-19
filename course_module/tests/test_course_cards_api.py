from django.contrib.auth.models import Group
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase


class CourseCardForStudentAPITestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make('user_module.User')
        self.user.groups.add(Group.objects.get_or_create(name='Students')[0])
        self.group = mommy.make('study_group_module.StudyGroup')
        self.user.student_profile.group = self.group
        self.user.student_profile.save()
        self.containers = mommy.make('course_module.CourseContainer', _quantity=3)
        # first and second containers will be available for user
        mommy.make('course_module.ContainerToGroup', group=self.group, container=self.containers[0])
        mommy.make('course_module.ContainerToGroup', group=self.group, container=self.containers[1])
        # the second one will also have another group
        mommy.make('course_module.ContainerToGroup', container=self.containers[1])
        # the third one doesn't have group of user
        mommy.make('course_module.ContainerToGroup', container=self.containers[2])
        self.courses = []
        for container in self.containers:
            # each container will have 2 courses.
            # 2 available containers -> 4 available courses
            for i in range(2):
                course = mommy.make('course_module.Course')
                mommy.make('course_module.ContainerToCourse', course=course, container=container)
                self.courses.append(course)
        self.url = reverse('containertocourse-list')

    def test_list(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(len(self.courses), response.data.get('count', None))
        for i in range(len(self.courses)):
            self.assertEqual(self.courses[i].id, response.data['results'][i]['course']['id'])

    def test_my_filter(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, data=dict(my=True))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(4, response.data.get('count', None))
        for i in range(4):
            self.assertEqual(self.courses[i].id, response.data['results'][i]['course']['id'])

    def test_filter_by_container(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, data=dict(container=self.containers[1].id))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, response.data.get('count', None))
        for i in range(2):
            self.assertEqual(self.courses[i + 2].id, response.data['results'][i]['course']['id'])

    def test_detail(self):
        url = '/course_api/cards/{}/'.format(self.containers[0].container_course_relations.first().id)
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue({'course', 'container', 'heads', 'status'}.issubset(response.data))
        self.assertEqual(self.courses[0].id, response.data['course']['id'])
        self.assertEqual(self.containers[0].id, response.data['container']['id'])


class CourseCardForProfessorAPITestCase(APITestCase):
    def setUp(self):
        self.user = mommy.make('user_module.User')
        self.user.groups.add(Group.objects.get_or_create(name='Professors')[0])
        self.containers = mommy.make('course_module.CourseContainer', _quantity=3)
        # first and second containers will be available for user
        self.relations = [
            mommy.make('course_module.ContainerToCourse', container=self.containers[0], heads=[self.user]),
            mommy.make('course_module.ContainerToCourse', container=self.containers[1], heads=[self.user]),
            # the third one will also have another head
            mommy.make('course_module.ContainerToCourse', container=self.containers[1],
                       heads=[self.user, mommy.make('user_module.User')]),
            # the fourth one doesn't have this user in heads
            mommy.make('course_module.ContainerToCourse', container=self.containers[2],
                       heads=[mommy.make('user_module.User')])
        ]
        self.url = reverse('containertocourse-list')

    def test_list(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(len(self.relations), response.data.get('count', None))
        for i in range(len(self.relations)):
            self.assertEqual(self.relations[i].id, response.data['results'][i]['id'])
            self.assertEqual(self.relations[i].course.id, response.data['results'][i]['course']['id'])

    def test_my_filter(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, data=dict(my=True))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(3, response.data.get('count', None))
        for i in range(3):
            self.assertEqual(self.relations[i].id, response.data['results'][i]['id'])
            self.assertEqual(self.relations[i].course.id, response.data['results'][i]['course']['id'])

    def test_filter_by_container(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, data=dict(container=self.containers[1].id))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, response.data.get('count', None))
        for i in range(2):
            self.assertEqual(self.relations[i + 1].id, response.data['results'][i]['id'])
            self.assertEqual(self.relations[i + 1].course.id, response.data['results'][i]['course']['id'])

    def test_detail(self):
        url = '/course_api/cards/{}/'.format(self.containers[0].container_course_relations.first().id)
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue({'course', 'container', 'heads', 'status'}.issubset(response.data))
        self.assertEqual(self.relations[0].course.id, response.data['course']['id'])
        self.assertEqual(self.containers[0].id, response.data['container']['id'])
