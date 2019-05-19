from django.contrib.auth.models import Group
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from course_module.models import ContainerToCourse, CourseHead
from user_module.models import User


class ContainerToCourseAPITestCase(APITestCase):
    def setUp(self):
        self.prof = mommy.make(User)
        self.prof.groups.add(Group.objects.get(name='Professors'))
        self.allowed_container_to_course1 = mommy.make(ContainerToCourse,
                                                       instant_accept=True,
                                                       min_quantity=10)
        self.allowed_container_to_course2 = mommy.make(ContainerToCourse,
                                                       instant_accept=False,
                                                       min_quantity=10,
                                                       quantity=20)
        CourseHead.objects.create(course=self.allowed_container_to_course1, curator=self.prof)
        CourseHead.objects.create(course=self.allowed_container_to_course2, curator=self.prof)
        self.not_allowed_container_to_course = mommy.make(ContainerToCourse, _quantity=3)
    
    def test_on_valid_data(self):
        self.client.force_login(self.prof)
        url = reverse('containertocourse-detail', kwargs=dict(pk=self.allowed_container_to_course1.id))
        response = self.client.patch(url, data=dict(quantity=20))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(20, response.data.get('quantity', None))

    def test_on_invalid_data(self):
        self.client.force_login(self.prof)
        url = reverse('containertocourse-detail', kwargs=dict(pk=self.not_allowed_container_to_course[0].id))
        response = self.client.patch(url, data=dict(quantity=20))
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_cant_set_quantity_less_than_min(self):
        self.client.force_login(self.prof)
        url = reverse('containertocourse-detail', kwargs=dict(pk=self.allowed_container_to_course1.id))
        response = self.client.patch(url, data=dict(quantity=9))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertTrue('quantity' in response.data)
