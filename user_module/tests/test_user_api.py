from django.contrib.auth.models import Group
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from user_module.models import User


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.user1 = mommy.make(User, password='123456')
        self.user2 = mommy.make(User)

    def test_cant_view_user_detail_unauthorized(self):
        url = reverse('user-detail', kwargs={'pk': self.user1.id})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_detail(self):
        self.client.force_login(self.user1)
        url = reverse('user-detail', kwargs={'pk': self.user2.id})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue({'username', 'email', 'role', 'first_name', 'last_name'}.issubset(
            response.data.keys()
        ))

    def test_student_detail(self):
        student = mommy.make(User)
        student.groups.add(Group.objects.get(name='Students'))
        self.client.force_login(self.user1)
        url = reverse('user-detail', kwargs={'pk': student.id})
        response = self.client.get(url)
        self.assertTrue({'username', 'email', 'role', 'first_name',
                         'last_name', 'student_profile'}.issubset(
            response.data.keys()
        ))

    def test_professor_detail(self):
        professor = mommy.make(User)
        professor.groups.add(Group.objects.get(name='Professors'))
        self.client.force_login(self.user1)
        url = reverse('user-detail', kwargs={'pk': professor.id})
        response = self.client.get(url)
        self.assertTrue({'username', 'email', 'role', 'first_name',
                         'last_name', 'professor_profile'}.issubset(
            response.data.keys()
        ))

    def test_deanery_worker_detail(self):
        deanery = mommy.make(User)
        deanery.groups.add(Group.objects.get(name='Students'))
        self.client.force_login(self.user1)
        url = reverse('user-detail', kwargs={'pk': deanery.id})
        response = self.client.get(url)
        self.assertTrue({'username', 'email', 'role', 'first_name',
                         'last_name'}.issubset(
            response.data.keys()
        ))

    def test_current_user(self):
        self.client.force_login(self.user1)
        url = reverse('user-current-user')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue({'id', 'username', 'email', 'role', 'first_name', 'last_name'}.issubset(
            response.data.keys()
        ))
        self.assertEqual(self.user1.id, response.data['id'])

    def test_change_invalid_password(self):
        user = User.objects.create_user(
            username='test',
            email='email@example.com',
            password='poiuytre'
        )
        self.client.force_login(user)
        url = reverse('user-change-password')
        response = self.client.post(url, data={
            'old_password': '123456',
            'new_password': 'poiuytrew',
        })
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_valid_password(self):
        user = User.objects.create_user(
            username='test',
            email='email@example.com',
            password='poiuytre'
        )
        self.client.force_login(user)
        url = reverse('user-change-password')
        response = self.client.post(url, data={
            'old_password': 'poiuytre',
            'new_password': 'poiuytrew',
        })
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.client.logout()
        
        # check login with new password
        self.client.login(username=user.username, password='poiuytrew')
        url = reverse('user-current-user')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
