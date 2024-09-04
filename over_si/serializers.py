from rest_framework import serializers
from .models import OverSI

class OverSISerializer(serializers.ModelSerializer):
    class Meta:
        model = OverSI
        fields = '__all__'
