from django.shortcuts import render
from .models import Fielder
from .serializers import FielderSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class FielderViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Fielder.objects.all()
    serializer_class = FielderSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            fielder = serializer.save()
            return Response({"fielder_id":fielder.id},status=200)
        return Response(serializer.errors,status=400)
