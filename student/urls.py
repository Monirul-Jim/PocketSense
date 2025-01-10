
from django.urls import path, include
from rest_framework import routers
from student.views import RegistrationViewSet, LoginView
from rest_framework_simplejwt.views import TokenRefreshView

router = routers.DefaultRouter()
router.register('register', RegistrationViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
