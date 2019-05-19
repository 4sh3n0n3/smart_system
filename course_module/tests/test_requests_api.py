from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from course_module.models import CourseRequest, Course, CourseContainer, ContainerToCourse, CourseHead
from eITIS.enums import ACCEPTED, SUBMITTED, CLOSED
from user_module.models import User


class RequestsAPITestCase(APITestCase):
    def setUp(self):
        self.student1 = mommy.make(User)
        self.student1.groups.add(Group.objects.get(name='Students'))
        self.student2 = mommy.make(User)
        self.student2.groups.add(Group.objects.get(name='Students'))
        self.requests_of_student1 = mommy.make(CourseRequest, student=self.student1, _quantity=3)
        self.requests_of_student2 = mommy.make(CourseRequest, student=self.student2, _quantity=2)

        self.professor1 = mommy.make(User)
        self.professor1.groups.add(Group.objects.get(name='Professors'))
        self.professor2 = mommy.make(User)
        self.professor2.groups.add(Group.objects.get(name='Professors'))
        self.deanery = mommy.make(User)
        self.deanery.groups.add(Group.objects.get(name='Deanery_Workers'))
        self.deanery.user_permissions.add(Permission.objects.get(codename='deanery_recruitment_creator'))
        self.course_of_pr1 = mommy.make(Course)
        self.course_of_pr2 = mommy.make(Course)
        self.container = mommy.make(CourseContainer, created_by=self.deanery)
        self.container_relations = [mommy.make(ContainerToCourse,
                                               container=self.container,
                                               course=self.course_of_pr1,
                                               instant_accept=True,
                                               quantity=10
                                               ),
                                    mommy.make(ContainerToCourse,
                                               container=self.container,
                                               course=self.course_of_pr2,
                                               )]
        mommy.make(CourseHead, course=self.container_relations[0], curator=self.professor1)
        mommy.make(CourseHead, course=self.container_relations[1], curator=self.professor2)
        self.requests_for_pr1 = mommy.make(CourseRequest, active_course=self.container_relations[0], _quantity=3)

    def test_student_can_view_his_requests(self):
        url = reverse('courserequest-list')
        self.client.force_login(self.student1)
        response = self.client.get(url)
        self.assertEqual(len(self.requests_of_student1), response.data['count'])
        for obj in self.requests_of_student1:
            self.assertTrue([i for i in response.data['results'] if i['id'] == obj.id])

    def test_prof_can_view_his_requests(self):
        url = reverse('courserequest-list')
        self.client.force_login(self.professor1)
        response = self.client.get(url)
        self.assertEqual(len(self.requests_for_pr1), response.data['count'])
        for obj in self.requests_for_pr1:
            self.assertTrue([i for i in response.data['results'] if i['id'] == obj.id])

    def test_can_create_request_with_valid_data(self):
        url = reverse('courserequest-list')
        self.client.force_login(self.student1)
        response = self.client.post(url, data=dict(active_course_id=self.container_relations[0].id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_create_only_one(self):
        url = reverse('courserequest-list')
        self.client.force_login(self.student1)
        response = self.client.post(url, data=dict(active_course_id=self.requests_of_student1[0].active_course.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_auto_accept_on_little_quantity(self):
        url = reverse('courserequest-list')
        self.client.force_login(self.student1)
        mommy.make(CourseRequest, active_course=self.container_relations[0], status=ACCEPTED, _quantity=9)
        response = self.client.post(url, data=dict(active_course_id=self.container_relations[0].id))
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_auto_accept_on_user_with_higher_score(self):
        url = reverse('courserequest-list')
        user = mommy.make(User)
        user.groups.add(Group.objects.get(name='Students'))
        user.student_profile.score=0
        request_of_student_with_min_score =  mommy.make(CourseRequest,
                                                        active_course=self.container_relations[0],
                                                        student=user,
                                                        status=ACCEPTED)
        other_requests = []
        for i in range(1, 10):
            user = mommy.make(User)
            user.groups.add(Group.objects.get(name='Students'))
            user.student_profile.score = i
            user.student_profile.save()
            other_requests.append(mommy.make(CourseRequest,
                                             active_course=self.container_relations[0],
                                             student=user,
                                             status=ACCEPTED))
        self.client.force_login(self.student1)
        self.student1.student_profile.score = 10
        self.student1.student_profile.save()
        response = self.client.post(url, data=dict(active_course_id=self.container_relations[0].id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SUBMITTED, CourseRequest.objects.get(pk=request_of_student_with_min_score.id).status)
        for i in other_requests:
            self.assertEqual(ACCEPTED, CourseRequest.objects.get(pk=i.id).status)

    def test_not_auto_accept_when_quantity_is_over(self):
        url = reverse('courserequest-list')
        self.client.force_login(self.student1)
        for i in range(10):
            user = mommy.make(User)
            user.groups.add(Group.objects.get(name='Students'))
            mommy.make(CourseRequest, active_course=self.container_relations[0],
                       student=user,
                       status=ACCEPTED)
        response = self.client.post(url, data=dict(active_course_id=self.container_relations[0].id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SUBMITTED, CourseRequest.objects.get(student=self.student1,
                                                              active_course=self.container_relations[0]).status)

    def test_auto_accept_when_quantity_is_not_set(self):
        self.container_relations[1].instant_accept = True
        self.container_relations[1].save()
        url = reverse('courserequest-list')
        self.client.force_login(self.student1)
        for i in range(10):
            user = mommy.make(User)
            user.groups.add(Group.objects.get(name='Students'))
            mommy.make(CourseRequest, active_course=self.container_relations[1],
                       student=user,
                       status=ACCEPTED)
        response = self.client.post(url, data=dict(active_course_id=self.container_relations[1].id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ACCEPTED, CourseRequest.objects.get(student=self.student1,
                                                             active_course=self.container_relations[1]).status)

    def test_not_auto_accept(self):
        url = reverse('courserequest-list')
        self.client.force_login(self.student1)
        response = self.client.post(url, data=dict(active_course_id=self.container_relations[1].id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SUBMITTED, CourseRequest.objects.get(student=self.student1,
                                                              active_course=self.container_relations[1]).status)

    def test_cancel_valid_request(self):
        url = reverse('courserequest-detail', kwargs=dict(pk=self.requests_of_student1[0].id))
        self.client.force_login(self.student1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_cancel_invalid_request(self):
        url = reverse('courserequest-detail', kwargs=dict(pk=self.requests_of_student1[0].id + 1000))
        self.client.force_login(self.student1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_change_other_requests_status_when_delete(self):
        CourseRequest.objects.filter(active_course=self.container_relations[0]).delete()
        user = mommy.make(User)
        user.groups.add(Group.objects.get(name='Students'))
        user.student_profile.score = 0
        request_of_student_with_min_score = mommy.make(CourseRequest,
                                                       active_course=self.container_relations[0],
                                                       student=user)
        other_requests = []
        for i in range(1, 10):
            user = mommy.make(User)
            user.groups.add(Group.objects.get(name='Students'))
            user.student_profile.score = i
            user.student_profile.save()
            other_requests.append(mommy.make(CourseRequest,
                                             active_course=self.container_relations[0],
                                             student=user,
                                             status=ACCEPTED))
        self.client.force_login(self.student1)
        self.student1.student_profile.score = 10
        self.student1.student_profile.save()
        student1_request = mommy.make(CourseRequest, active_course=self.container_relations[0],
                                      student=self.student1)
        student1_request.status = ACCEPTED
        student1_request.save()
        url = reverse('courserequest-detail', kwargs=dict(pk=student1_request.id))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ACCEPTED, CourseRequest.objects.get(pk=request_of_student_with_min_score.id).status)

    def test_can_create_only_students(self):
        url = reverse('courserequest-list')
        self.client.force_login(self.professor1)
        response = self.client.post(url, data=dict(active_course_id=self.container_relations[0].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cant_create_request_on_closed_course(self):
        self.container_relations[0].status = CLOSED
        self.container_relations[0].save()
        url = reverse('courserequest-list')
        self.client.force_login(self.student1)
        response = self.client.post(url, data=dict(active_course_id=self.container_relations[0].id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(response.data)
        self.assertTrue('active_course_id' in response.data)

    def test_filter_by_container(self):
        url = reverse('courserequest-list') + '?container=' + str(self.container_relations[0].id)
        self.client.force_login(self.deanery)
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(len(self.requests_for_pr1), response.data['count'])

    def test_student_cant_accept_request(self):
        self.client.force_login(self.student1)
        url = reverse('courserequest-accept-request')
        response = self.client.post(url, data=dict(id=self.requests_of_student1[0].id))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_student_cant_reject_request(self):
        self.client.force_login(self.student1)
        url = reverse('courserequest-reject-request')
        response = self.client.post(url, data=dict(id=self.requests_of_student1[0].id))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_cant_accept_request_of_already_accepted_student(self):
        mommy.make(CourseRequest, student=self.student1, active_course=self.container_relations[1], status=ACCEPTED)
        request = mommy.make(CourseRequest, student=self.student1, active_course=self.container_relations[0], status=SUBMITTED)
        self.client.force_login(self.professor1)
        url = reverse('courserequest-accept-request')
        response = self.client.post(url, data=dict(id=request.id))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
    
    def test_accept_valid_request(self):
        container_relation = mommy.make(ContainerToCourse,
                                        container=mommy.make(CourseContainer),
                                        course=self.course_of_pr1,
                                        instant_accept=True,
                                        quantity=10)
        mommy.make(CourseRequest, student=self.student1, active_course=container_relation,
                   status=ACCEPTED)
        request = mommy.make(CourseRequest, student=self.student1, active_course=self.container_relations[0],
                             status=SUBMITTED)
        self.client.force_login(self.professor1)
        url = reverse('courserequest-accept-request')
        response = self.client.post(url, data=dict(id=request.id))
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_cant_send_request_on_same_container(self):
        new_course = mommy.make(Course, containers=[self.requests_of_student1[0].active_course.container])
        self.client.force_login(self.student1)
        url = reverse('courserequest-list')
        response = self.client.post(url, data=dict(active_course_id=new_course.id))
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
