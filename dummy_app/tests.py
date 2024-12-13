import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import DummyCategory, Dummy


class DummyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.dummy_url = lambda pk=None: reverse('dummy-object-view', args=(pk,)) if pk else reverse('dummy-objects-view')

        self.category = DummyCategory.objects.create(label="Category 1")
        self.dummy = Dummy.objects.create(label="Dummy 1", description="Description 1", category=self.category)

    def test_get_all_dummies(self):
        response = self.client.get(self.dummy_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_single_dummy(self):
        response = self.client.get(self.dummy_url(1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['label'], self.dummy.label)

    def test_get_single_dummy_not_found(self):
        response = self.client.get(self.dummy_url(1000000))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_dummy(self):
        data = {'label': 'Dummy Label', 'description': 'Some text', 'category': self.category.id}
        response = self.client.post(self.dummy_url(), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['label'], data['label'])

        data = [
            {'label': 'Dummy Label 1', 'description': 'Some text', 'category': self.category.id},
            {'label': 'Dummy Label 2', 'description': 'Some text', 'category': self.category.id},
            {'label': 'Dummy Label 3', 'description': 'Some text', 'category': self.category.id},
        ]
        response = self.client.post(self.dummy_url(), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 3)
