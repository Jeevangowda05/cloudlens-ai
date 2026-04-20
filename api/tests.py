from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import UserProfile


class AuthApiTests(APITestCase):
    def test_signup_creates_user_profile(self):
        response = self.client.post(
            '/api/auth/signup/',
            {
                'email': 'newuser@example.com',
                'password': 'StrongPass123!',
                'password_confirm': 'StrongPass123!',
                'first_name': 'New',
                'last_name': 'User',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='newuser@example.com')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_change_password_endpoint(self):
        user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='OldPass123!',
        )
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = self.client.post(
            '/api/auth/change-password/',
            {
                'old_password': 'OldPass123!',
                'new_password': 'NewPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('NewPass123!'))
        self.assertIn('token', response.data)
