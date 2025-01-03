from rest_framework import serializers
from .models import OverFI
from bowler.serializers import BowlerSerializer
from balls.serializers import BallsSerializer

class OverFISerializer(serializers.ModelSerializer):
    bowler = BowlerSerializer()
    ball = BallsSerializer(many=True)
    class Meta:
        model = OverFI
        fields = '__all__'
