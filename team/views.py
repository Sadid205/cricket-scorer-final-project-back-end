from django.shortcuts import render
from .models import Team
from .serializers import TeamSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from author.models import Author
from rest_framework import status
# Create your views here.

class TeamView(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def list(self,request,*args,**kwargs):
        author_id = kwargs.get('author_id')
        if author_id is not None:
            try:
                teams = Team.objects.filter(author__id=author_id)
                serializer = self.get_serializer(teams,many=True)
                return Response(serializer.data)
            except Exception as e:
                return Response({"detail":str(e)},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail":"Author ID is required."},status=status.HTTP_400_BAD_REQUEST)    
        


    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            team = serializer.save()
            return Response({'team_id':team.id})
        return Response(serializer.errors,status=400)
