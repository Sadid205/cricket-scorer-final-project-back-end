from rest_framework import serializers
from .models import FallOfWickets
from batsman.serializers import BatsmanSerializer
class FallOfWicketsSerializer(serializers.ModelSerializer):
    batsman = BatsmanSerializer()
    class Meta:
        model = FallOfWickets
        fields = '__all__'