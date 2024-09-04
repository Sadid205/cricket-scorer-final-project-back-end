from django.shortcuts import render
from .models import History
from .serializers import HistorySerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class HistoryViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = History.objects.all()
    serializer_class = HistorySerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            history = serializer.save()
            return Response({"history_id":history.id},status=200)
        return Response(serializer.errors,status=400)
