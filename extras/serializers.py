from rest_framework import serializers
from .models import Extras

class ExtrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extras
        fields = '__all__'