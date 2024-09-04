from django.shortcuts import render
from .models import Batsman
from .serializers import BatsmanSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class BatsmanViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Batsman.objects.all()
    serializer_class = BatsmanSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            batsman = serializer.save()
            return Response({"batsman_id":batsman.id},status=200)
        return Response(serializer.errors,status=400)
