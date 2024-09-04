from rest_framework import serializers
from .models import Fielding

class FieldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fielding
        fields = '__all__'