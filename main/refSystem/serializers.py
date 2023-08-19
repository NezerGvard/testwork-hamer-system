from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class UserSerialize(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'