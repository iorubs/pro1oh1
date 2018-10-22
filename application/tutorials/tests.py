from django.test import TestCase
import unittest
from authentication.models import Account
from django.test import Client
from .views import *

from tutorials.models import TutorialGroup, Tutorial

import json
from django.http import JsonResponse

class ModelTestCase(TestCase):
    def setUp(self):
        self.test_group = TutorialGroup.objects.create(title='test_group', info='Just a test group')
        self.test_group.save()
        self.test_tutorial = Tutorial.objects.create(t_group=self.test_group, title='test_tutorial', url='https://www.youtube.com/watch?v=bSfpSOBD30U')
        self.test_tutorial.save()

    def test_create_tutorial_group(self):
        """Create new tutorial_group, check if it was added to DB"""
        create_tutorial_group = TutorialGroup.objects.create(title='create_test', info='Just a test group')
        create_tutorial_group.save()
        self.assertEqual(TutorialGroup.objects.get(id=create_tutorial_group.id).title, 'create_test')

    def test_list_tutorial_groups(self):
        """List tutorial_groups, verify with expected output"""
        queryset = TutorialGroup.objects.all()
        queryset = queryset.filter(title=self.test_group.title)
        self.assertNotEqual(len(queryset), 0)

    def test_test_tutorial_group(self):
        """Update tutorial_group, check if DB was updated"""
        self.test_group.title = 'updated_group'
        self.test_group.save()
        queryset = TutorialGroup.objects.all()
        queryset = queryset.filter(id=self.test_group.id)
        self.assertNotEqual(queryset, [])
        self.assertEqual(queryset[0].title, 'updated_group')

    def test_delete_tutorial_group(self):
        """Delete tutorial_group, check if it was removed from DB"""
        self.test_group.delete()
        queryset = TutorialGroup.objects.all()
        queryset = queryset.filter(title=self.test_group.title)
        self.assertEqual(len(queryset), 0)

    def test_create_tutorial(self):
        """Create new tutorial, check if it was added to DB"""
        create_tutorial = Tutorial.objects.create(t_group=self.test_group, title='create_tutorial', url='https://www.youtube.com/watch?v=qKldIZsrg1Y')
        create_tutorial.save()
        self.assertEqual(Tutorial.objects.get(id=create_tutorial.id).title, 'create_tutorial')
        self.assertEqual(Tutorial.objects.get(id=create_tutorial.id).t_group.title, 'test_group')

    def test_list_grouped_tutorials(self):
        """List tutorial in a particular group, verify with expected output"""
        queryset = Tutorial.objects.all()
        queryset = queryset.filter(t_group=self.test_group)
        self.assertNotEqual(len(queryset), 0)

    def test_update_tutorial(self):
        """Update tutorial, check if DB was updated"""
        self.test_tutorial.title = 'updated_tutorial'
        self.test_tutorial.save()
        queryset = Tutorial.objects.all()
        queryset = queryset.filter(id=self.test_tutorial.id)
        self.assertNotEqual(queryset, [])
        self.assertEqual(queryset[0].title, 'updated_tutorial')

    def test_delete_tutorial(self):
        """Delete tutorial, check if it was removed from DB"""
        self.test_tutorial.delete()
        queryset = Tutorial.objects.all()
        queryset = queryset.filter(title=self.test_tutorial.title)
        self.assertEqual(len(queryset), 0)

class HTTPTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.client.post('/api/v1/accounts/', {
            'username': 'test_http_user',
            'password': 'unit',
            'email': 'test_http_user@unit.ie',
            'first_name': 'test',
            'last_name': 'http'
        })
        self.client.login(username='test_http_user', password='unit')

    def test_create_unauthorized_tutorial_group_http(self):
        """Try create a new group with a normal user using the API, check response"""
        pass

    def test_create_tutorial_group_http(self):
        """Create a tutorial_group using the API, check response"""
        t_group_create = json.dumps({'title': 'create_test2', 'info': 'Some test group'})
        response = self.client.post('/api/v1/tutorial_groups/', t_group_create, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'create_test2')

    def test_list_tutorial_groups_http(self):
        """List user tutorial_groups using the API, check response"""
        test_group = json.dumps({'title': 'test_group', 'info': 'Some test group'})
        self.client.post('/api/v1/tutorial_groups/', test_group, content_type="application/json")
        response = self.client.get('/api/v1/tutorial_groups/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        found = False
        for p in data:
            if p['title'] == 'test_group':
                found = True

        self.assertTrue(found)

    def test_update_tutorial_group_http(self):
        """Update a tutorial_group using the API, check response"""
        pass

    def test_delete_tutorial_group_http(self):
        """Delete a tutorial_group using the API, check response"""
        pass

    def test_create_unauthorized_tutorial_http(self):
        """Try to create a tutorial using the API with a non admin user, check response"""
        pass

    def test_create_unauthorized_tutorial_http(self):
        """Try create a tutorial with a normal user using the API, check response"""
        pass

    def test_create_tutorial_http(self):
        """Create tutorial with an admin using the API, check response"""
        pass

    def test_list_tutorials_http(self):
        """List a group's tutorials using the API, check response"""
        pass

    def test_update_tutorial_http(self):
        """Update tutorial using the API, check response"""
        pass

    def test_delete_tutorial_http(self):
        """Delete tutorial using the API, check response"""
        pass
