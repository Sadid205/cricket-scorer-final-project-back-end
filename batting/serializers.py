from rest_framework import serializers
from .models import Batting

class BattingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batting
        fields = '__all__'