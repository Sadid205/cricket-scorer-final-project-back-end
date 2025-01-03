from rest_framework import serializers
from .models import Partnerships
from batsman.serializers import BatsmanSerializer

class PartnershipsSerializer(serializers.ModelSerializer):
   striker = BatsmanSerializer()
   non_striker = BatsmanSerializer()
   class Meta:
        model = Partnerships
        fields = '__all__'