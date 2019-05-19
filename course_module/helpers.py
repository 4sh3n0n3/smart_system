from django.db import transaction
from rest_framework.exceptions import ValidationError

from eITIS.enums import SUBMITTED, ACCEPTED, REJECTED


@transaction.atomic
def delete_request(request):
    # if request.active_course has instant_accept and it was accepted
    if request.active_course.instant_accept and request.status == ACCEPTED:
        # get submitted requests, order by score, if exists first, then
        # change it's status on accepted
        submitted_requests = request.active_course.requests.filter(status=SUBMITTED)
        if len(submitted_requests):
            submitted_requests = sorted(submitted_requests, key=lambda obj: -obj.student.student_profile.score)
            submitted_requests[0].status = ACCEPTED
            submitted_requests[0].save()
    
    request.delete()


@transaction.atomic
def accept_request(request):
    student = request.student
    container = request.active_course.container
    student_containers_to_courses = student.student_course_requests.filter(status=ACCEPTED,
                                                                           active_course__container=container)
    if student_containers_to_courses.count():
        raise ValidationError('Студент уже записан на курс из этого набора')
    request.status = ACCEPTED
    request.save()
    return request


@transaction.atomic
def reject_request(request):
    request.status = REJECTED
    request.save()
    # if request.active_course has instant_accept
    if request.active_course.instant_accept:
        # get submitted requests, order by score, if exists first, then
        # change it's status on accepted
        submitted_requests = request.active_course.requests.filter(status=SUBMITTED)
        if len(submitted_requests):
            submitted_requests = sorted(submitted_requests, key=lambda obj: -obj.student.student_profile.score)
            submitted_requests[0].status = ACCEPTED
            submitted_requests[0].save()
    return request
