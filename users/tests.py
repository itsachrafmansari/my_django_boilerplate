from django.test import TestCase
from django.urls import reverse
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
