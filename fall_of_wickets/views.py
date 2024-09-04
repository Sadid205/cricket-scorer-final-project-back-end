from django.shortcuts import render
from .models import FallOfWickets
from .serializers import FallOfWicketsSerializer
from rest_framework import viewsets
from rest_framework.response import Response
# Create your views here.

class FallOfWicketsViewSet(viewsets.ModelViewSet):
    queryset = FallOfWickets.objects.all()
    serializer_class = FallOfWicketsSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            fall_of_wickets = serializer.save()
            return Response({"bowler_id":fall_of_wickets.id},status=200)
        return Response(serializer.errors,status=400)
