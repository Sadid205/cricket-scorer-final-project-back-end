from django.shortcuts import render
from .models import Fielding
from .serializers import FieldingSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class FieldingViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Fielding.objects.all()
    serializer_class = FieldingSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            fielding = serializer.save()
            return Response({"fielding_id":fielding.id},status=200)
        return Response(serializer.errors,status=400)
