from rest_framework import serializers

from .models import Dummy, DummyCategory


class DummyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DummyCategory
        fields = '__all__'


class DummySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dummy
        fields = '__all__'
