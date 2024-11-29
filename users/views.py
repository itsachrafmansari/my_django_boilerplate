from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser
from users.serializers import UserSerializer


class SignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate email verification token and link
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = request.build_absolute_uri(
                reverse('email-verification-view', kwargs={'uidb64': uid, 'token': token})
            )

            # Send verification email
            send_mail(
                "Verify Your Email Address",
                f"Click the link to verify your email: {verification_link}",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            return Response({
                "message": "User created. Please check your email to verify your account."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token):

        # Check the existence of the user
        try:
            uid = force_str(urlsafe_base64_decode(uidb64)) # Extract the user's id from the verification link
            user = CustomUser.objects.get(pk=uid)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the token and update the user
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid token or expired link."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):

        # Check the existence of the user
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid email."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate reset token and link
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = request.build_absolute_uri(
            reverse('password-reset-confirm-view', kwargs={'uidb64': uid, 'token': token})
        )

        # Send reset email
        send_mail(
            "Reset Your Password",
            f"Click the link to reset your password: {reset_link}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, uidb64, token):

        # Check the existence of the user
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the token and update the user
        if default_token_generator.check_token(user, token):

            # Check the password is not empty
            password = request.data.get('password')
            if not password:
                return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Update the user
            user.set_password(password)
            user.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid token or expired link."}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token or logout failed."}, status=status.HTTP_400_BAD_REQUEST)
