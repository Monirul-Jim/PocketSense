
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    password1 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password', 'password1']

    def validate(self, data):
        # Check if the passwords match
        if data['password'] != data['password1']:
            raise serializers.ValidationError(
                {'password1': 'Passwords do not match.'})

        # Check if the username already exists
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                {'username': 'Username is already taken.'})

        # Check if the email is already in use
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {'email': 'Email is already registered.'})

        return data

    def create(self, validated_data):
        validated_data.pop('password1')  # Remove the confirm password field
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'email': 'Email does not exist.'})

        user = authenticate(username=user.username, password=password)
        if user is None:
            raise serializers.ValidationError(
                {'password': 'Invalid password.'})

        attrs['user'] = user
        return attrs
