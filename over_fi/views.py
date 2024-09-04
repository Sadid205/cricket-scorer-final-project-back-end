from django.shortcuts import render
from .models import OverFI
from .serializers import OverFISerializer
from rest_framework import viewsets
from rest_framework.response import Response
# Create your views here.

class OverFIViewSet(viewsets.ModelViewSet):
    queryset = OverFI.objects.all()
    serializer_class = OverFISerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            over = serializer.save()
            return Response({"over_id":over.id},status=200)
        return Response(serializer.errors,status=400)
