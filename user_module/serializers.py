from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from study_group_module.serializers import GroupSerializer
from user_module.models import User, StudentProfile, ProfessorProfile, DeaneryProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'middle_name', 'username', 'email', 'photo', 'role')


# Student Profile serializer
# (using main Group serializer)
class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = '__all__'

    group = GroupSerializer()


# Professor Profile serializer
class ProfessorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessorProfile
        fields = ['position', 'academic_title', 'office', 'institute']
        depth = 1


class DeaneryProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeaneryProfile
        fields = ['institute']
        depth = 1


# Student user serializer
# (using Student Profile serializer
# (using main Group serializer)
class StudentSerializer(UserSerializer):
    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('student_profile',)

    student_profile = StudentProfileSerializer(read_only=True)


# Professor user serializer
# (using Professor Profile serializer)
class ProfessorSerializer(UserSerializer):
    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('professor_profile',)

    professor_profile = ProfessorProfileSerializer(read_only=True)


class DeanerySerializer(UserSerializer):
    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('deanery_profile', )

    deanery_profile = DeaneryProfileSerializer(read_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    @property
    def user(self):
        request = self.context['request']
        assert request and request.user and request.user.is_authenticated
        return request.user

    def validate_old_password(self, password):
        if not self.user.check_password(password):
            raise ValidationError('Неверно введён старый пароль')
        return password

    def validate_new_password(self, password):
        validate_password(password)
        return password

    def create(self, validated_data):
        user = self.user
        user.set_password(validated_data['new_password'])
        user.save(update_fields=['password'])
        return user


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'full_name', 'username', 'photo')
