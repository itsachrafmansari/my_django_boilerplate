from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import SignupSerializer
from users.utils import email_verification_token


class SignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()

            # Generate email verification token and link
            token = email_verification_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = request.build_absolute_uri(
                reverse('email-verification-view', kwargs={'uidb64': uid, 'token': token})
            )

            # Send verification email
            subject = 'Welcome to Django Boilerplate!'
            message = f"Hi {user.username},\n\nClick the link below to verify your email:\n{verification_link}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, (user.email,), fail_silently=False,)


            return Response(
                {"message": "User created. Check your email to verify your account."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token):

        # Get the user from the email verification url
        try:
            uid = force_bytes(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except User.DoesNotExist:
            return Response({'error': 'Invalid token or user ID'}, status=status.HTTP_400_BAD_REQUEST)

        # Check the verification token and verify the email
        if email_verification_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
