from rest_framework import serializers
from .models import Partnerships

class PartnershipsSerializer(serializers.ModelSerializer):
   class Meta:
        model = Partnerships
        fields = '__all__'