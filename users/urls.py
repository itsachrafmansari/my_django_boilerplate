from django.urls import path
from .views import SignupView, LoginView, LogoutView, EmailVerificationView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup-view'),
    path('login/', LoginView.as_view(), name='login-view'),
    path('logout/', LogoutView.as_view(), name='logout-view'),
    path('email-verification/<str:uidb64>/<str:token>/', EmailVerificationView.as_view(), name='email-verification-view'),
]
