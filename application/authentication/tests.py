from django.test import TestCase
from authentication.models import Account
import unittest
from django.test import Client
from .views import *

import json
from django.http import JsonResponse

class AccountTestCase(TestCase):
    def setUp(self):
        Account.objects.create(
            email='pro1oh1@mymail.ie',
            username='pro',
            first_name='pro',
            last_name='1oh1',
            is_admin=True
        )
        Account.objects.create(
            email='del1oh1@mymail.ie',
            username='del',
            first_name='pro',
            last_name='1oh1'
        )

    def test_create_user(self):
        """Create user, check if user was created successfully."""
        user_create = Account.objects.create(email='create@mymail.ie',
        username='new', first_name='pro', last_name='1oh1')
        self.assertEqual(Account.objects.get(username='new').username, 'new')

    def test_is_admin(self):
        """Check if user is superuser."""
        user_is_admin = Account.objects.get(username='pro')
        self.assertEqual(user_is_admin.is_admin, True)

    def test_update_user(self):
        """Update user account, validate changes."""
        user_update = Account.objects.get(username='pro')
        user_update.first_name = 'orp'
        user_update.save()
        self.assertEqual(Account.objects.get(username='pro').first_name, 'orp')

    def test_delete_user(self):
        """Delete user, check user list to make sure it was removed."""
        user_delete = Account.objects.get(username='del').delete()
        try:
            Account.objects.get(username='del')
            self.fail("User del was not removed!")
        except Account.DoesNotExist:
            pass

class HTTPTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.client.post('/api/v1/accounts/', {
            'username': 'yoloswag1',
            'password': '123456789',
            'email': 'yolo1@mail.ie',
            'first_name': 'yo',
            'last_name': 'lo'
        })

        self.client.post('/api/v1/accounts/', {
            'username': 'delete_test',
            'password': '123456789',
            'email': 'delete_test@mail.ie',
            'first_name': 'delete',
            'last_name': 'test'
        })

    def test_register_http(self):
        """Send register request (post). Check response"""
        # Issue a POST request.
        response = self.client.post('/api/v1/accounts/', {
            'username': 'yoloswag',
            'password': '123456789',
            'email': 'yolo@mail.ie',
            'first_name': 'yo',
            'last_name': 'lo'
        })
        # Check that the response is 201 'Created'.
        self.assertEqual(response.status_code, 201)
        #check that the response matches the user
        data = json.loads(response.content)
        self.assertEqual(data['username'], 'yoloswag')

    def test_login_http(self):
        """Send login request (login). Check result, true == success"""
        response = self.client.login(username='yoloswag1', password='123456789')
        self.assertEqual(response, True)

    def test_logout_http(self):
        """Send logout request (logout). Check response status"""
        response = self.client.logout()
        self.assertEqual(response, None)

    def test_update_http(self):
        """Update user details (put). Check response"""
        self.client.login(username='yoloswag1', password='123456789')

        profile = json.dumps({
            'username': 'new_name',
            'password': '123456789',
            'email': 'yolo1@mail.ie',
            'first_name': 'yo',
            'last_name': 'lo'
        })
        response = self.client.put('/api/v1/accounts/yoloswag1/', profile, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['email'], 'yolo1@mail.ie')
        self.assertEqual(data['username'], 'new_name')

    def test_get_http(self):
        """Retrieve user details (get). Check response"""
        response = self.client.get('/api/v1/accounts/yoloswag1/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['email'], 'yolo1@mail.ie')

    def test_delete_http(self):
        """Retrieve user details (delete). Check response status"""
        self.client.login(username='delete_test', password='123456789')
        response = self.client.delete('/api/v1/accounts/delete_test/')
        self.assertEqual(response.status_code, 204)
