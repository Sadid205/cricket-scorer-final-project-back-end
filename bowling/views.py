from django.shortcuts import render
from .models import Bowling
from .serializers import BowlingSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class BowlingViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Bowling.objects.all()
    serializer_class = BowlingSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            bowling = serializer.save()
            return Response({"bowler_id":bowling.id},status=200)
        return Response(serializer.errors,status=400)
