from django.shortcuts import render
from .models import Batting
from .serializers import BattingSerializer
from rest_framework import viewsets
from rest_framework.response import Response
# Create your views here.

class BattingViewSets(viewsets.ModelViewSet):
    queryset = Batting.objects.all()
    serializer_class = BattingSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            batting = serializer.save()
            return Response({"batting_id":batting.id},status=200)
        return Response(serializer.errors,status=400)
