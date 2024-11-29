from django.urls import path
from .views import SignupView, LoginView, LogoutView, EmailVerificationView, PasswordResetRequestView, \
    PasswordResetConfirmView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup-view'),
    path('login/', LoginView.as_view(), name='login-view'),
    path('logout/', LogoutView.as_view(), name='logout-view'),
    path('email-verification/<str:uidb64>/<str:token>/', EmailVerificationView.as_view(), name='email-verification-view'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password-reset-request-view'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm-view'),
]
