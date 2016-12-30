from django.contrib.auth.models import User
from rest_framework import serializers, validators


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
        )


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, label='Enter password')
    password2 = serializers.CharField(required=True, label='Confirm password')

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'password2'
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise validators.ValidationError('Passwords must match')
        # TODO : check if it is correct ot do queries in validate!
        # if User.objects.filter(username=attrs['username']).exists():
        #     raise validators.ValidationError('User already exists')
        return attrs

    # override create cause of extra unnecessary fields
    # or just return necessary from validate method? ( bad idea)
    def create(self, validated_data):
        return User.objects.create_user(username=validated_data['username'],
                                        email=validated_data['email'],
                                        first_name=validated_data['first_name'],
                                        last_name=validated_data['last_name'],
                                        password=validated_data['password'])


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, label='Username')

    class Meta:
        model = User
        fields = [
            'username',
            'password'
        ]
