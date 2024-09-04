from django.shortcuts import render
from .models import Player
from .serializers import PlayerSerializer
from rest_framework import viewsets
from rest_framework.response import Response
# Create your views here.

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            player=serializer.save()
            return Response({"player_id":player.id},status=200)
        return Response(serializer.errors,status=400)