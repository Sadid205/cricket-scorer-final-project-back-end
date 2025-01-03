from rest_framework import serializers
from .models import OverSI
from bowler.serializers import BowlerSerializer
from balls.serializers import BallsSerializer

class OverSISerializer(serializers.ModelSerializer):
    bowler = BowlerSerializer()
    ball = BallsSerializer(many=True)
    class Meta:
        model = OverSI
        fields = '__all__'
