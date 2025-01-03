from django.shortcuts import render
from .models import Player
from .serializers import PlayerSerializer,PlayerDetailsSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from player.models import Player
from rest_framework import status,generics

# Create your views here.

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    def list(self,request,*args,**kwargs):
        team_id = kwargs.get('team_id')
        if team_id is not None:
            try:
                players = Player.objects.filter(team__id=team_id)
                serializer = self.get_serializer(players,many=True)
                return Response(serializer.data)
            except Exception as e:
                return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail":"Author ID is required"},status=status.HTTP_400_BAD_REQUEST)
        
    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            player=serializer.save()
            return Response({"player_id":player.id},status=200)
        return Response(serializer.errors,status=400)

class PlayerDetailsView(generics.RetrieveAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerDetailsSerializer
    lookup_field = 'id'