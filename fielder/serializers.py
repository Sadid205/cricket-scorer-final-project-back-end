from rest_framework import serializers
from .models import Fielder

class FielderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fielder
        fields = '__all__'