from django.shortcuts import render
from .models import Bowler
from .serializers import BowlerSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class BowlerViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Bowler.objects.all()
    serializer_class = BowlerSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            bowler = serializer.save()
            return Response({"bowler_id":bowler.id},status=200)
        return Response(serializer.errors,status=400)
