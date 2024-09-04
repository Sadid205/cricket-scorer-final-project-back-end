from django.shortcuts import render
from .models import OverSI
from .serializers import OverSISerializer
from rest_framework import viewsets
from rest_framework.response import Response
# Create your views here.

class OverSIViewSet(viewsets.ModelViewSet):
    queryset = OverSI.objects.all()
    serializer_class = OverSISerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            over = serializer.save()
            return Response({"over_id":over.id},status=200)
        return Response(serializer.errors,status=400)
