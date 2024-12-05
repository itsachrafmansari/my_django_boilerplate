from django.contrib import admin

from .models import Dummy, DummyCategory

admin.site.register(DummyCategory)
admin.site.register(Dummy)
