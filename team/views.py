from django.shortcuts import render
from .models import Team
from .serializers import TeamSerializer
from rest_framework import viewsets
from rest_framework.response import Response
# Create your views here.

class TeamView(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            team = serializer.save()
            return Response({'team_id':team.id})
        return Response(serializer.errors,status=400)
