from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient

from .models import CustomUser


class Tests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.active_user_data = {'email': 'active@example.com', 'password': 'active123'}
        self.inactive_user_data = {'email': 'inactive@example.com', 'password': 'inactive123'}
        self.nonexistent_user_data = {'email': 'nonexistent@example.com', 'password': 'nonexistent123'}

        self.active_user = CustomUser.objects.create_user(**self.active_user_data, is_active=True)
        self.inactive_user = CustomUser.objects.create_user(**self.inactive_user_data)


class SignupTests(Tests):

    def setUp(self):
        super().setUp()

        self.signup_url = reverse('signup-view')
        self.email_verification_url = lambda uidb64, token: reverse(
            'email-verification-view', args=(uidb64, token)
        )


    def test_signup_a_new_user(self):
        """ Test the creation of a new user """

        response = self.client.post(self.signup_url, self.nonexistent_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User created. Please check your email to verify your account.')
        self.assertTrue(CustomUser.objects.filter(email=self.nonexistent_user_data['email']).exists())


    def test_signup_an_existing_user(self):
        """ Test the creation of an existing user """

        # Test with an active user
        response = self.client.post(self.signup_url, self.active_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test with an inactive user
        response = self.client.post(self.signup_url, self.inactive_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_signup_with_empty_password(self):
        """ Test the creation of a new user but with an empty password """

        response = self.client.post(self.signup_url, {'email': self.nonexistent_user_data['email'], 'password': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_email_confirmation_with_valid_token(self):
        """ Test email confirmation with a valid token """

        uidb64 = urlsafe_base64_encode(force_bytes(self.inactive_user.pk))
        token = default_token_generator.make_token(self.inactive_user)
        url = self.email_verification_url(uidb64, token)

        response = self.client.get(url)
        self.inactive_user.refresh_from_db() # Refresh the user instance from the database

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Email verified successfully.')
        self.assertTrue(self.inactive_user.is_active)


    def test_email_confirmation_with_invalid_token(self):
        """ Test email confirmation with an invalid token """

        uidb64 = urlsafe_base64_encode(force_bytes(self.inactive_user.pk))
        token = "invalid-token"
        url = self.email_verification_url(uidb64, token)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(Tests):

    def setUp(self):
        super().setUp()

        self.login_url = reverse('login-view')
        self.password_reset_request_url = reverse('password-reset-request-view')
        self.password_verification = lambda uidb64, token: reverse(
            'password-reset-confirm-view', args=(uidb64, token)
        )


class LogoutTests(Tests):

    def setUp(self):
        super().setUp()
        self.logout_url = reverse('logout-view')
