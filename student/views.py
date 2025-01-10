
from rest_framework import status, viewsets
from rest_framework.response import Response
from student.serializers import RegistrationSerializer, LoginSerializer, GroupSerializer, ExpenseSerializer, ExpenseWithShareSerializer
from student.models import Group, Expense
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        expense = serializer.save()

        total_members = expense.split_among.count()
        if total_members > 0:
            split_amount = expense.amount / total_members

        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ---------------------------------------------------------------------------


class UserExpensesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all the group IDs the user is part of, based on custom_groups
        user_groups_ids = request.user.custom_groups.values_list(
            'id', flat=True)

        # Debugging: Print out the group IDs to see what groups the user is part of
        print(f"User groups: {user_groups_ids}")

        if not user_groups_ids:
            return Response({"message": "User is not part of any groups."}, status=status.HTTP_404_NOT_FOUND)

        # Get expenses for the user's groups
        expenses = Expense.objects.filter(group__id__in=user_groups_ids)

        # Debugging: Print out the number of expenses returned
        print(f"Number of expenses found: {expenses.count()}")

        # Serialize the expenses with user share
        serializer = ExpenseWithShareSerializer(
            expenses, many=True, context={'request': request})

        # Return the serialized data
        return Response(serializer.data)

# ---------------------------------------------------------------------------


class RegistrationViewSet(viewsets.ViewSet):

    def create(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.last_login = timezone.now()
            user.save()
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            access_token['email'] = user.email
            access_token['first_name'] = user.first_name
            access_token['last_name'] = user.last_name
            response = Response({
                "message": "User login successfully",
                "success": True,
                'access': str(access_token),
            }, status=status.HTTP_200_OK)
            cookie_max_age = 24 * 60 * 60
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=cookie_max_age,
            )

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
