from django.urls import path

from .views import DummyView, DummyViewProtected

urlpatterns = [
    path('dummy/', DummyView.as_view(), name='dummy-objects-view'),
    path('dummy/<int:pk>/', DummyView.as_view(), name='dummy-object-view'),
    path('dummy/protected/', DummyViewProtected.as_view(), name='dummy-objects-protected-view'),
    path('dummy/<int:pk>/protected/', DummyViewProtected.as_view(), name='dummy-object-protected-view'),
]