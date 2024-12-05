from django.urls import path

from .views import DummyView

urlpatterns = [
    path('dummy/', DummyView.as_view(), name='dummy-objects-view'),
    path('dummy/<int:pk>', DummyView.as_view(), name='dummy-object-view'),
]