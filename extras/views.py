from django.shortcuts import render
from .models import Extras
from .serializers import ExtrasSerializer
from rest_framework import viewsets
from rest_framework.response import Response
# Create your views here.

class ExtrasViewSet(viewsets.ModelViewSet):
    queryset = Extras.objects.all()
    serializer_class = ExtrasSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            extras = serializer.save()
            return Response({"bowler_id":extras.id},status=200)
        return Response(serializer.errors,status=400)
