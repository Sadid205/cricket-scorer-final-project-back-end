from rest_framework import serializers
from .models import OverFI

class OverFISerializer(serializers.ModelSerializer):
    class Meta:
        model = OverFI
        fields = '__all__'
