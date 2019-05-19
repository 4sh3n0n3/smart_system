from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from eITIS.enums import ACCEPTED, REJECTED, SUBMITTED, CLOSED
from user_module.serializers import UserSerializer, StudentSerializer
from .models import Course, ContainerToCourse, CourseRequest, CourseMediaFilesLinks, CourseContainer


# COURSES

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class ShortCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'name', 'logo_path')


# COURSE CONTAINERS

class ShortCourseContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseContainer
        fields = ('id', 'name', 'start_date', 'expiration_date', 'status')


# CONTAINER TO COURSE (RELATIONS)

class ShortRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContainerToCourse
        fields = ('id', 'status', 'quantity', 'min_quantity', 'accepted_requests', 'all_requests', 'instant_accept')


class RelationSerializer(ShortRelationSerializer):
    class Meta:
        model = ContainerToCourse
        fields = ShortRelationSerializer.Meta.fields + ('container', 'course', 'heads')

    heads = UserSerializer(many=True)
    course = ShortCourseSerializer()
    container = ShortCourseContainerSerializer()


class RelationWithExtendedCourseSerializer(RelationSerializer):
    course = CourseSerializer()


class ProfessorUpdateRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContainerToCourse
        fields = '__all__'
        read_only_fields = ('container', 'course', 'heads', 'status', 'min_quantity',)

    def validate_quantity(self, quantity):
        if quantity < self.instance.min_quantity:
            raise ValidationError('Количество не может быть меньше минимума, установленного деканатом')
        return quantity

    @transaction.atomic
    def update(self, instance, validated_data):
        ContainerToCourse.objects.filter(id=instance.id).update(**validated_data)
        if (validated_data.get('instant_accept', None) and not instance.instant_accept or
                validated_data.get('instant_accept', None) and instance.instant_accept and (
                        validated_data.get('quantity', 0) > instance.quantity if instance.quantity else 0
                )):
            not_accepted_requests = CourseRequest.objects.filter(active_course=instance, status=SUBMITTED)
            not_accepted_requests = sorted(not_accepted_requests, key=lambda obj: -obj.student.student_profile.score)
            count = validated_data.get('quantity') - CourseRequest.objects.filter(active_course=instance,
                                                                                  status=ACCEPTED)
            for request in not_accepted_requests[:count]:
                request.status = ACCEPTED
                request.save()
        if (instance.instant_accept and validated_data.get('instant_accept', True) and
            instance.quantity if instance.quantity else 0 > validated_data.get(
                'quantity', instance.quantity)):
            accepted_requests = CourseRequest.objects.filter(active_course=instance, status=ACCEPTED)
            accepted_requests = sorted(accepted_requests, key=lambda obj: -obj.student.student_profile.score)
            count = len(accepted_requests) - validated_data.get('quantity')
            for request in accepted_requests[:count]:
                request.status = SUBMITTED
                request.save()
        return ContainerToCourse.objects.get(pk=instance.pk)


# REQUESTS

class ShortCourseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRequest
        fields = ('status', 'message')


class CourseRequestSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    active_course_id = serializers.PrimaryKeyRelatedField(source='active_course', write_only=True,
                                                          queryset=ContainerToCourse.objects.all())
    
    class Meta:
        model = CourseRequest
        fields = ('id', 'status', 'active_course_id', 'student', 'message', 'created_at', 'active_course')
        read_only_fields = ('status', 'student')
        validators = (
            UniqueTogetherValidator(
                queryset=CourseRequest.objects.all(),
                fields=('student', 'active_course')
            ),
        )
    
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        request = self.context['request']
        data['student'] = request.user
        return data
    
    def validate_active_course_id(self, active_course):
        if active_course.status is CLOSED:
            raise ValidationError('Прием заявок закрыт!')
        return active_course

    def validate(self, attrs):
        if CourseRequest.objects.filter(student=attrs['student'],
                                        active_course__container=attrs['active_course'].container
                                        ).exclude(status=REJECTED).exists():
            raise ValidationError('Студент уже записан на курс из этого набора')
        return attrs

    def create(self, validated_data):
        course_details = validated_data['active_course']
        if not course_details.instant_accept:
            instance = CourseRequest.objects.create(**validated_data)
            return instance
        
        # if automatic accept:
        # get already accepted requests
        accepted_requests = course_details.requests.filter(status=ACCEPTED)
        
        # if course is already full
        if course_details.quantity and (
                course_details.quantity <= accepted_requests.count()
        ):
            # get all requests, order by student score
            requests = sorted(course_details.requests.filter(status=ACCEPTED),
                              key=lambda obj: -obj.student.student_profile.score)
            
            last_request = requests[-1]
            # if last score < score of this student, then change status of that request on default,
            # create this request with status accepted
            if last_request.student.student_profile.score < validated_data['student'].student_profile.score:
                last_request.status = SUBMITTED
                last_request.save()
                instance = CourseRequest.objects.create(**validated_data, status=ACCEPTED)
                return instance
        # if course is not full
        if not course_details.quantity or course_details.quantity > accepted_requests.count():
            # then instantly accept request
            instance = CourseRequest.objects.create(**validated_data, status=ACCEPTED)
            return instance
        
        # in other cases save request with default status
        instance = CourseRequest.objects.create(**validated_data)
        return instance


class ExtendedCourseRequestSerializer(CourseRequestSerializer):
    active_course = RelationSerializer(read_only=True, required=False)


class RequestExistenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRequest
        fields = ('status',)


# MEDIA

class CourseMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMediaFilesLinks
        fields = ('name', 'path',)
