import unittest
from django.test import Client
from .views import *

class HTTPTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.client.post('/api/v1/accounts/', {
            'username': 'http',
            'password': 'unit',
            'email': 'http@unit.ie',
            'first_name': 'un',
            'last_name': 'it'
        })
        self.client.login(username='http', password='unit')

    def test_create_project_http(self):
        """Get registered user count from userCountView, check response"""
        response = self.client.post('/api/v1/user-count/', content_type=" text/html")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.content, '0')
