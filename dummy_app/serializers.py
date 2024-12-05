from rest_framework import serializers

from .models import Dummy, DummyCategory


class DummyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DummyCategory
        fields = '__all__'


class DummySerializer(serializers.Serializer):
    class Meta:
        model = Dummy
        fields = '__all__'
