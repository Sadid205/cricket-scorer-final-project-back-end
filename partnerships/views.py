from django.shortcuts import render
from .models import Partnerships
from .serializers import PartnershipsSerializer
from rest_framework import viewsets
from rest_framework.response import Response
# Create your views here.

class PartnershipsViewSet(viewsets.ModelViewSet):
    queryset = Partnerships.objects.all()
    serializer_class = PartnershipsSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            partnerships = serializer.save()
            return Response({"partnerships_id":partnerships.id},status=200)
        return Response(serializer.errors,status=400)
