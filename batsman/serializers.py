from rest_framework import serializers
from .models import Batsman
from player.serializers import PlayerSerializer
class BatsmanSerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    class Meta:
        model = Batsman
        fields = "__all__"