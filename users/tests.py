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


    def test_email_confirmation_with_invalid_uid(self):
        """ Test email confirmation with an invalid uid """

        uidb64 = urlsafe_base64_encode(force_bytes(-1))
        token = default_token_generator.make_token(self.inactive_user)
        url = self.email_verification_url(uidb64, token)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(Tests):

    def setUp(self):
        super().setUp()

        self.login_url = reverse('login-view')
        self.password_reset_request_url = reverse('password-reset-request-view')
        self.password_reset_confirm_url = lambda uidb64, token: reverse(
            'password-reset-confirm-view', args=(uidb64, token)
        )


    def test_login_active_user(self):
        """ Test the login with an active user """

        response = self.client.post(self.login_url, self.active_user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


    def test_login_inactive_user(self):
        """ Test the login with an inactive user """

        response = self.client.post(self.login_url, self.inactive_user_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)


    def test_login_invalid_credentials(self):
        """ Test the login with a non-existing user or invalid credentials """

        # Test the login with a non-existing user
        response = self.client.post(self.login_url, self.nonexistent_user_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

        # Test the login with wrong credentials
        response = self.client.post(self.login_url, {'email': self.active_user_data['email'], 'password': '<>'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)


    def test_password_reset_request_valid(self):
        """ Test password reset request with a valid email """

        # Test password reset request with an active user
        response = self.client.post(self.password_reset_request_url, {'email': self.active_user_data['email']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password reset email sent.')

        # Test password reset request with an inactive user
        response = self.client.post(self.password_reset_request_url, {'email': self.inactive_user_data['email']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password reset email sent.')

class LogoutTests(Tests):

    def setUp(self):
        super().setUp()
        self.logout_url = reverse('logout-view')

        self.get_login_tokens = lambda user_data: self.client.post(reverse('login-view'), user_data).data


    def test_logout_with_valid_token(self):
        """ Test logout with valid refresh token """

        tokens = self.get_login_tokens(self.active_user_data)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.post(self.logout_url, {"refresh": tokens["refresh"]})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data['message'], 'Logged out successfully')


    def test_logout_invalid_refresh_token(self):
        """ Test logout with an invalid refresh token """

        tokens = self.get_login_tokens(self.active_user_data)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.post(self.logout_url, {'refresh': 'invalidToken'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
