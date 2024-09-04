from rest_framework import serializers
from .models import Balls

class BallsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balls
        fields = '__all__'