from rest_framework import serializers
from .models import Bowling

class BowlingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bowling
        fields = '__all__'