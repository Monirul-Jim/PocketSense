
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from student.models import Group, Expense


class GroupSerializer(serializers.ModelSerializer):
    members = serializers.SlugRelatedField(
        many=True,
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'members', 'created_at']


class ExpenseSerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField(
        slug_field='name',  # Accept group name for the field
        queryset=Group.objects.all()
    )
    paid_by = serializers.SlugRelatedField(
        slug_field='username',  # Accept username for the user
        queryset=User.objects.all()
    )
    split_among = serializers.SlugRelatedField(
        many=True,
        slug_field='username',  # Accept usernames for the split
        queryset=User.objects.all()
    )

    class Meta:
        model = Expense
        fields = ['id', 'group', 'description', 'amount',
                  'paid_by', 'split_among', 'created_at']

    def validate(self, data):
        # Check if the amount is greater than 0
        if data['amount'] <= 0:
            raise serializers.ValidationError(
                {'amount': 'Amount must be greater than zero.'})

        # Ensure the user creating the expense is part of the group
        group = data['group']
        user = data['paid_by']

        if user not in group.members.all():
            raise serializers.ValidationError(
                {'paid_by': f'{user} is not a member of the selected group.'}
            )

        # Ensure that all users in the split_among field are members of the group
        for user_in_split in data['split_among']:
            if user_in_split not in group.members.all():
                raise serializers.ValidationError(
                    {'split_among': f'{
                        user_in_split.username} is not a member of the selected group.'}
                )

        return data
# --------------------------------------------------------------------------


class ExpenseWithShareSerializer(serializers.ModelSerializer):
    group = serializers.SlugRelatedField(
        slug_field='name', queryset=Group.objects.all())
    paid_by = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all())
    split_among = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all(), many=True)
    user_share = serializers.SerializerMethodField()
    paid_to_or_by = serializers.SerializerMethodField()
    amount_to_receive_or_pay = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = ['id', 'group', 'description', 'amount',
                  'paid_by', 'split_among', 'user_share', 'paid_to_or_by', 'amount_to_receive_or_pay']

    def get_user_share(self, obj):
        # Get the user making the request
        user = self.context['request'].user

        # Calculate the share of the user if they are in the split_among list
        total_members = len(obj.split_among.all()) + \
            1  # Including the one who paid
        share_amount = round(obj.amount / total_members, 2)

        # If the user is in the split_among list or is the one who paid
        if user in obj.split_among.all() or user == obj.paid_by:
            return share_amount
        return 0  # If the user is not part of the split, their share is 0

    def get_paid_to_or_by(self, obj):
        # Get the user making the request
        user = self.context['request'].user

        # If the user paid, return "Paid By" message
        if user == obj.paid_by:
            return "Paid By"

        # If the user is in the split_among list, return "Paid To" message
        if user in obj.split_among.all():
            return f"Paid To {obj.paid_by.username}"

        return None  # If the user is neither paying nor splitting, return None

    def get_amount_to_receive_or_pay(self, obj):
        user = self.context['request'].user
        total_members = len(obj.split_among.all()) + \
            1  # Including the one who paid
        share_amount = round(obj.amount / total_members, 2)

        # If the user is the one who paid, they will receive from others
        if user == obj.paid_by:
            amount_to_receive = (total_members - 1) * share_amount
            return round(amount_to_receive, 2)

        # If the user is in the split_among list, they owe their share to the user who paid
        if user in obj.split_among.all():
            return round(share_amount, 2)

        return 0  # If the user is not part of the split, they don't owe anything

# ------------------------------------------------------------------------------


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
