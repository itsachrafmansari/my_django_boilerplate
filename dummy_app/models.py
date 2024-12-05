from django.db import models


class DummyCategory(models.Model):
    label = models.CharField(max_length=64)

    def __str__(self):
        return self.label


class Dummy(models.Model):
    label = models.CharField(max_length=128)
    description = models.TextField()
    category = models.ForeignKey(DummyCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.label
