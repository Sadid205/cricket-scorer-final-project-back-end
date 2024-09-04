from rest_framework import serializers
from .models import FallOfWickets

class FallOfWicketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FallOfWickets
        fields = '__all__'