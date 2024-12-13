from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import DummyCategory, Dummy


class DummyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.dummy_url = lambda pk=None: reverse('dummy-object-view', args=(pk,)) if pk else reverse('dummy-objects-view')

        self.category = DummyCategory.objects.create(label="Category 1")
        self.dummy = Dummy.objects.create(label="Dummy 1", description="Description 1", category=self.category)
