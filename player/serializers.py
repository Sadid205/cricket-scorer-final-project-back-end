from rest_framework import serializers
from .models import Player
from fielding.serializers import FieldingSerializer
from batting.serializers import BattingSerializer
from bowling.serializers import BowlingSerializer
class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = "__all__"
    
class PlayerDetailsSerializer(serializers.ModelSerializer):
    fielding = FieldingSerializer(many=True)
    batting = BattingSerializer(many=True)
    bowling = BowlingSerializer(many=True)
    class Meta:
        model = Player
        fields = ['id','name','image','team','fielding','batting','bowling']