from rest_framework import serializers
from .models import Bowler
from player.serializers import PlayerSerializer

class BowlerSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    class Meta:
        model = Bowler
        fields = '__all__'