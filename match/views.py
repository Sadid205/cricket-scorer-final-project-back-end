from django.shortcuts import render
from .models import Match
from team.models import Team
from balls.models import Balls
from over_fi.models import OverFI
from over_si.models import OverSI
from player.models import Player
from batsman.models import Batsman
from bowler.models import Bowler
from fielder.models import Fielder
from batting.models import Batting
from bowling.models import Bowling
from author.models import Author
from .serializers import MatchSerializer,StartMatchSerializer,SelectOpeningPlayerSerializer,UpdateScoreSerializer,SelectANewBowlerSerializer,StartSecondInningsSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class MatchViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

    def create(self,request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(request.data)
            match = serializer.save()
            return Response({"match_id":match.id},status=200)
        return Response(serializer.errors,status=400)


class StartMatchView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request,*args,**kwargs):
        serializer = StartMatchSerializer(data=request.data)
        if serializer.is_valid():
            host_team_name = serializer.validated_data.get("host_team_name")
            visitor_team_name = serializer.validated_data.get("visitor_team_name")
            toss_winner_team_name = serializer.validated_data.get("toss_winner_team_name")
            elected = serializer.validated_data.get("elected")
            over = serializer.validated_data.get("over")
            author_id = serializer.validated_data.get("author_id")
            host_team = Team.objects.create(team_name=host_team_name)
            visitor_team = Team.objects.create(team_name=visitor_team_name)
         
            if(host_team.team_name==toss_winner_team_name):
                toss_winner = host_team
            else:
                toss_winner = visitor_team
            try:
                existing_author = Author.objects.get(id=author_id)
            except Author.DoesNotExist:
                existing_author = None
            if existing_author==None:
                return Response({author_id:"This author_id does not exist!"})
            match = Match.objects.create(team1=host_team,team2=visitor_team,total_over=over,toss_winner=toss_winner,elected=elected)
            existing_author.match.add(match)
            return Response({"match_id":match.id,"host_team_id":host_team.id,"visitor_team_id":visitor_team.id},status=200)
        return Response(serializer.errors,status=400)

class SelectOpeningPlayerView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request,*args,**kwargs):
        serializer = SelectOpeningPlayerSerializer(data=request.data)
        if serializer.is_valid():
            match_id = serializer.validated_data.get("match_id")
            striker = serializer.validated_data.get("striker")
            non_striker = serializer.validated_data.get("non_striker")
            bowler = serializer.validated_data.get("bowler")
            try:
                existing_match = Match.objects.get(id=match_id)
            except Match.DoesNotExist:
                existing_match = None
            if existing_match==None:
                return Response({match_id:"This match_id Does Not Exist!"},status=404)
            if existing_match.innings=="1st":
                toss_winner = existing_match.toss_winner
                elected = existing_match.elected
                host_team = existing_match.team1
                visitor_team = existing_match.team2
                # print(toss_winner.team_name,elected,host_team.team_name,visitor_team.team_name)
                if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                    new_striker_player = Player.objects.create(name=striker,team=host_team)
                    new_non_striker_player = Player.objects.create(name=non_striker,team=host_team)
                    new_bowler_player = Player.objects.create(name=bowler,team=visitor_team)
                    new_striker_batsman = Batsman.objects.create(player=new_striker_player,team=host_team)
                    new_non_striker_batsman = Batsman.objects.create(player=new_non_striker_player,team=host_team)
                    new_bowler = Bowler.objects.create(match=existing_match,player=new_bowler_player,team=visitor_team)
                    new_over = OverFI.objects.create(bowler=new_bowler)
                    existing_match.current_bowler = new_bowler
                    existing_match.striker = new_striker_batsman
                    existing_match.non_striker = new_non_striker_batsman
                    existing_match.first_innings_over.add(new_over)
                    existing_match.save()
                    return Response({"match_id":existing_match.id,"message":"Successfully select opening player."},status=200)

                if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                    new_striker_player = Player.objects.create(name=striker,team=visitor_team)
                    new_non_striker_player = Player.objects.create(name=non_striker,team=visitor_team)
                    new_bowler_player = Player.objects.create(name=bowler,team=host_team)
                    new_striker_batsman = Batsman.objects.create(player=new_striker_player,team=visitor_team)
                    new_non_striker_batsman = Batsman.objects.create(player=new_non_striker_player,team=visitor_team)
                    new_bowler = Bowler.objects.create(match=existing_match,player=new_bowler_player,team=host_team)
                    new_over = OverFI.objects.create(bowler=new_bowler)
                    existing_match.current_bowler = new_bowler
                    existing_match.striker = new_striker_batsman
                    existing_match.non_striker = new_non_striker_batsman
                    existing_match.first_innings_over.add(new_over)
                    existing_match.save()
                    return Response({"match_id":existing_match.id,"message":"Successfully select opening player."},status=200)           
            if existing_match=='2nd':
                if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                    new_striker_player = Player.objects.create(name=striker,team=visitor_team)
                    new_non_striker_player = Player.objects.create(name=non_striker,team=visitor_team)
                    new_bowler_player = Player.objects.create(name=bowler,team=host_team)
                    new_striker_batsman = Batsman.objects.create(player=new_striker_player,team=visitor_team)
                    new_non_striker_batsman = Batsman.objects.create(player=new_non_striker_player,team=visitor_team)
                    new_bowler = Bowler.objects.create(match=existing_match,player=new_bowler_player,team=host_team)
                    new_over = OverSI.objects.create(bowler=new_bowler)
                    existing_match.current_bowler = new_bowler
                    existing_match.striker = new_striker_batsman
                    existing_match.non_striker = new_non_striker_batsman
                    existing_match.second_innings_over.add(new_over)
                    existing_match.save()
                    return Response({"match_id":existing_match.id,"message":"Successfully select opening player."},status=200)

                if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                    new_striker_player = Player.objects.create(name=striker,team=host_team)
                    new_non_striker_player = Player.objects.create(name=non_striker,team=host_team)
                    new_bowler_player = Player.objects.create(name=bowler,team=visitor_team)
                    new_striker_batsman = Batsman.objects.create(player=new_striker_player,team=host_team)
                    new_non_striker_batsman = Batsman.objects.create(player=new_non_striker_player,team=host_team)
                    new_bowler = Bowler.objects.create(match=existing_match,player=new_bowler_player,team=visitor_team)
                    new_over = OverSI.objects.create(bowler=new_bowler)
                    existing_match.current_bowler = new_bowler
                    existing_match.striker = new_striker_batsman
                    existing_match.non_striker = new_non_striker_batsman
                    existing_match.second_innings_over.add(new_over)
                    existing_match.save()
                    return Response({"match_id":existing_match.id,"message":"Successfully select opening player."},status=200)           
            return Response(serializer.errors,status=400)
        
            
class UpdateScoreView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def put(self,request,*args,**kwargs):
        serializer = UpdateScoreSerializer(data=request.data)
        if serializer.is_valid():
            match_id = serializer.validated_data.get("match_id")
            run = serializer.validated_data.get("run")
            wide = serializer.validated_data.get("wide")
            byes = serializer.validated_data.get("byes")
            legByes = serializer.validated_data.get("legByes")
            no_ball = serializer.validated_data.get("no_ball")
            wicket = serializer.validated_data.get("wicket")
            how_wicket_fall = serializer.validated_data.get("how_wicket_fall")
            who_helped = serializer.validated_data.get("who_helped")
            new_batsman = serializer.validated_data.get("new_batsman")
            try:
                existing_match = Match.objects.get(id=match_id)
            except Match.DoesNotExist:
                existing_match = None
            if existing_match == None:
                return Response({match_id:"This match_id does not exist."},status=404)
            host_team = existing_match.team1
            visitor_team = existing_match.team2
            toss_winner = existing_match.toss_winner
            elected = existing_match.elected
            if existing_match.innings=="1st":
                if wicket==True:
                    existing_match.nth_ball+=1
                    existing_match.first_innings_wicket+=1
                    existing_match.save()
                    if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                        existing_striker = existing_match.striker
                        existing_non_striker = existing_match.non_striker
                        if how_wicket_fall=="bowled":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "bowled"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Bowled_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_player = None
                            if existing_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_player,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="catch_out":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "catch_out"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Catch_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=host_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=host_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=host_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="run_out_striker":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "run_out"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Run_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=host_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=host_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=host_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="run_out_non_striker":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_non_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "run_out"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Run_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=host_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=host_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=host_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=host_team)
                                existing_match.non_striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.non_striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="stumping":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "stumping"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Stumping",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=host_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=host_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=host_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="lbw":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "lbw"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Leg_before_wicket",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_player = None
                            if existing_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_player,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()   
                        if how_wicket_fall=="hit_wicket":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "hit_wicket"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Hit_wicket",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_player = None
                            if existing_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_player,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()   
                    if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                        existing_striker = existing_match.striker
                        existing_non_striker = existing_match.non_striker
                        if how_wicket_fall=="bowled":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "bowled"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Bowled_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_player = None
                            if existing_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_player,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="catch_out":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "catch_out"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Catch_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=visitor_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=visitor_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=visitor_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="run_out_striker":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "run_out"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Run_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=visitor_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=visitor_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=visitor_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="run_out_non_striker":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_non_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "run_out"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Run_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=visitor_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=visitor_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=visitor_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=visitor_team)
                                existing_match.non_striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.non_striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="stumping":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "stumping"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Stumping",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=visitor_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=visitor_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=visitor_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="lbw":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "lbw"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Leg_before_wicket",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_player = None
                            if existing_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_player,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()   
                        if how_wicket_fall=="hit_wicket":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "hit_wicket"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Hit_wicket",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_player = None
                            if existing_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_player,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()   
                    return Response({"success":"Successfully added a new batsman"},status=200) 



                if wide==True or byes==True or legByes==True or no_ball==True:
                    if run==1 or run==3 or run==5:
                        current_striker = existing_match.striker
                        existing_match.striker = existing_match.non_striker
                        existing_match.non_striker = current_striker
                        existing_match.save()
                    if wide==True:
                        existing_match.first_innings_run+=(1+run)
                        new_ball = Balls.objects.create(ball_types="Wide",runs=run)
                        over_fi_instance = existing_match.first_innings_over.last()
                        over_fi_instance.ball.add(new_ball)
                        existing_match.first_innings_over.add(over_fi_instance)
                        existing_match.save()
                    if no_ball==True:
                        if run==4:
                            existing_match.striker.four+=1
                            existing_match.striker.save()
                        if run==6:
                            existing_match.striker.six+=1
                            existing_match.striker.save()
                        
                        existing_match.first_innings_run+=(1+run)
                        existing_match.striker.ball+=1
                        existing_match.striker.run+=run
                        existing_match.striker.save()
                        new_ball = Balls.objects.create(ball_types="No_ball",runs=run)
                        over_fi_instance = existing_match.first_innings_over.last()
                        over_fi_instance.ball.add(new_ball)
                        existing_match.first_innings_over.add(over_fi_instance)
                        existing_match.save()
                    if byes==True:
                        existing_match.first_innings_run+=run
                        existing_match.nth_ball+=1
                        existing_match.striker.ball+=1
                        existing_match.striker.save()
                        new_ball = Balls.objects.create(ball_types="Byes",runs=run)
                        over_fi_instance = existing_match.first_innings_over.last()
                        over_fi_instance.ball.add(new_ball)
                        existing_match.first_innings_over.add(over_fi_instance)
                        existing_match.save()
                    if legByes==True:
                        existing_match.first_innings_run+=run
                        existing_match.nth_ball+=1
                        existing_match.striker.ball+=1
                        existing_match.striker.save()
                        new_ball = Balls.objects.create(ball_types="Leg_byes",runs=run)
                        over_fi_instance = existing_match.first_innings_over.last()
                        over_fi_instance.ball.add(new_ball)
                        existing_match.first_innings_over.add(over_fi_instance)
                        existing_match.save()
                else:
                    if run==1:
                        new_ball = Balls.objects.create(ball_types="One",runs=run)
                        over_fi_instance = existing_match.first_innings_over.last()
                        over_fi_instance.ball.add(new_ball)
                        existing_match.first_innings_over.add(over_fi_instance)
                        current_striker = existing_match.striker
                        existing_match.striker = existing_match.non_striker
                        existing_match.non_striker = current_striker
                        existing_match.first_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.nth_ball+=1
                        existing_match.striker.run+=run
                        existing_match.striker.save()
                        existing_match.save()
                    elif run==2:
                        new_ball = Balls.objects.create(ball_types="Two",runs=run)
                        over_fi_instance = existing_match.first_innings_over.last()
                        over_fi_instance.ball.add(new_ball)
                        existing_match.first_innings_over.add(over_fi_instance)
                        existing_match.first_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.nth_ball+=1
                        existing_match.striker.run+=run
                        existing_match.striker.save()
                        existing_match.save()
                    elif run==3:
                        new_ball = Balls.objects.create(ball_types="Three",runs=run)
                        over_fi_instance = existing_match.first_innings_over.last()
                        over_fi_instance.ball.add(new_ball)
                        existing_match.first_innings_over.add(over_fi_instance)
                        current_striker = existing_match.striker
                        existing_match.striker = existing_match.non_striker
                        existing_match.non_striker = current_striker
                        existing_match.first_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.nth_ball+=1
                        existing_match.striker.run+=run
                        existing_match.striker.save()
                        existing_match.save()
                    elif run==4:
                        new_ball = Balls.objects.create(ball_types="Four",runs=run)
                        over_fi_instance = existing_match.first_innings_over.last()
                        over_fi_instance.ball.add(new_ball)
                        existing_match.first_innings_over.add(over_fi_instance)
                        existing_match.striker.four+=1
                        existing_match.first_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.nth_ball+=1
                        existing_match.striker.run+=run
                        existing_match.striker.save()
                        existing_match.save()
                    elif run==5:
                        new_ball = Balls.objects.create(ball_types="Five",runs=run)
                        over_fi_instance = existing_match.first_innings_over.last()
                        over_fi_instance.ball.add(new_ball)
                        existing_match.first_innings_over.add(over_fi_instance)
                        current_striker = existing_match.striker
                        existing_match.striker = existing_match.non_striker
                        existing_match.non_striker = current_striker
                        existing_match.first_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.nth_ball+=1
                        existing_match.striker.run+=run
                        existing_match.striker.save()
                        existing_match.save()
                    elif run==6:
                        new_ball = Balls.objects.create(ball_types="Six",runs=run)
                        over_fi_instance = existing_match.first_innings_over.last()
                        over_fi_instance.ball.add(new_ball)
                        existing_match.first_innings_over.add(over_fi_instance)
                        existing_match.striker.six+=1
                        existing_match.first_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.nth_ball+=1
                        existing_match.striker.run+=run
                        existing_match.striker.save()
                        existing_match.save()
                    elif run==0:
                        new_ball = Balls.objects.create(ball_types="Dot_ball",runs=run)
                        over_fi_instance = existing_match.first_innings_over.last()
                        over_fi_instance.ball.add(new_ball)
                        existing_match.first_innings_over.add(over_fi_instance)
                        existing_match.first_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.nth_ball+=1
                        existing_match.striker.run+=run
                        existing_match.striker.save()
                        existing_match.save()
            if existing_match.innings=="2nd":
                if wicket==True:
                    existing_match.nth_ball+=1
                    existing_match.second_innings_wicket+=1
                    existing_match.save()
                    if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                        existing_striker = existing_match.striker
                        existing_non_striker = existing_match.non_striker
                        if how_wicket_fall=="bowled":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "bowled"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Bowled_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_player = None
                            if existing_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_player,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="catch_out":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "catch_out"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Catch_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=visitor_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=visitor_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=visitor_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="run_out_striker":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "run_out"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Run_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=visitor_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=visitor_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=visitor_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="run_out_non_striker":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_non_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "run_out"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Run_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=visitor_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=visitor_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=visitor_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=visitor_team)
                                existing_match.non_striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.non_striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="stumping":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "stumping"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Stumping",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=visitor_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=visitor_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=visitor_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="lbw":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "lbw"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Leg_before_wicket",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_player = None
                            if existing_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_player,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()   
                        if how_wicket_fall=="hit_wicket":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "hit_wicket"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Hit_wicket",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_player = None
                            if existing_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_player,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=visitor_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=visitor_team)
                                existing_match.striker = newBatsman
                                existing_match.save()   
                    if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                        existing_striker = existing_match.striker
                        existing_non_striker = existing_match.non_striker
                        if how_wicket_fall=="bowled":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "bowled"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Bowled_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_player = None
                            if existing_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_player,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="catch_out":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "catch_out"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Catch_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=host_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=host_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=host_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="run_out_striker":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "run_out"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Run_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=host_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=host_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=host_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="run_out_non_striker" :
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_non_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "run_out"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Run_out",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=host_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=host_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=host_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=host_team)
                                existing_match.non_striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.non_striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="stumping":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "stumping"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Stumping",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_catch_player = Player.objects.get(name=who_helped)
                            except Player.DoesNotExist:
                                existing_catch_player = None
                            if existing_catch_player!=None:
                                try:
                                    existing_fielder = Fielder.objects.get(player=existing_player)
                                except Fielder.DoesNotExist:
                                    existing_fielder = None
                                if existing_fielder!=None:
                                    existing_batsman.catch_by = existing_fielder
                                    existing_batsman.save()
                                else:
                                    newFielder = Fielder.objects.create(player=existing_player,team=host_team)
                                    existing_batsman.catch_by = newFielder
                                    existing_batsman.save()
                            else:
                                newCatchPlayer = Player.objects.create(name=who_helped,team=host_team)
                                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=host_team)
                                existing_batsman.catch_by = newCatchFielder
                                existing_batsman.save()
                            try:
                                existing_new_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_new_player = None
                            if existing_new_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_new_player,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                        if how_wicket_fall=="lbw":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "lbw"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Leg_before_wicket",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_player = None
                            if existing_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_player,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()   
                        if how_wicket_fall=="hit_wicket":
                            try:
                                existing_batsman = Batsman.objects.get(id=existing_striker.id)
                            except Batsman.DoesNotExist:
                                return Response({existing_striker.id:"This batsman id does not exist!"})
                            existing_batsman.out_by = existing_match.current_bowler
                            existing_batsman.how_wicket_fall = "hit_wicket"
                            existing_batsman.is_out = True
                            existing_batsman.save()
                            existing_over_instance = existing_match.first_innings_over.last()
                            newBall = Balls.objects.create(ball_types="Hit_wicket",runs=0)
                            existing_over_instance.ball.add(newBall)
                            try:
                                existing_player = Player.objects.get(name=new_batsman)
                            except Player.DoesNotExist:
                                existing_player = None
                            if existing_player!=None:
                                newBatsman = Batsman.objects.create(player=existing_player,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()
                            else:
                                newPlayer = Player.objects.create(name=new_batsman,team=host_team)
                                newBatsman = Batsman.objects.create(player=newPlayer,team=host_team)
                                existing_match.striker = newBatsman
                                existing_match.save()  
                    return Response({"success":"Successfully added a new batsman"},status=200) 


                if wide==True or byes==True or legByes==True or no_ball==True:
                    if(run==1 or run==3 or run==5):
                        current_striker = existing_match.striker
                        existing_match.striker = existing_match.non_striker
                        existing_match.non_striker = current_striker
                        existing_match.save()
                    if wide==True:
                        existing_match.second_innings_run+=(1+run)
                        new_ball = Balls.objects.create(ball_types="Wide",runs=run)
                        over_si_instance = existing_match.second_innings_over.last()
                        over_si_instance.ball.add(new_ball)
                        existing_match.second_innings_over.add(over_si_instance)
                        existing_match.save()
                    if no_ball==True:
                        if run==4:
                            existing_match.striker.four+=1
                            existing_match.striker.save()
                        if run==6:
                            existing_match.striker.six+=1
                            existing_match.striker.save()
                        existing_match.second_innings_run+=(1+run)
                        existing_match.striker.ball+=1
                        existing_match.striker.run+=run
                        existing_match.striker.save()
                        new_ball = Balls.objects.create(ball_types="No_ball",runs=run)
                        over_si_instance = existing_match.second_innings_over.last()
                        over_si_instance.ball.add(new_ball)
                        existing_match.second_innings_over.add(over_si_instance)
                        existing_match.save()
                    if byes==True:
                        existing_match.second_innings_run+=run
                        existing_match.nth_ball+=1
                        existing_match.striker.ball+=1
                        existing_match.striker.run+=run
                        existing_match.striker.save()
                        new_ball = Balls.objects.create(ball_types="Byes",runs=run)
                        over_si_instance = existing_match.second_innings_over.last()
                        over_si_instance.ball.add(new_ball)
                        existing_match.second_innings_over.add(over_si_instance)
                        existing_match.save()
                    if legByes==True:
                        existing_match.second_innings_run+=run
                        existing_match.nth_ball+=1
                        existing_match.striker.ball+=1
                        existing_match.striker.run+=run
                        existing_match.striker.save()
                        new_ball = Balls.objects.create(ball_types="Leg_byes",runs=run)
                        over_si_instance = existing_match.second_innings_over.last()
                        over_si_instance.ball.add(new_ball)
                        existing_match.second_innings_over.add(over_si_instance)
                        existing_match.save()
                else:
                    if run==1:
                        new_ball = Balls.objects.create(ball_types="One",runs=run)
                        over_si_instance = existing_match.second_innings_over.last()
                        over_si_instance.ball.add(new_ball)
                        existing_match.second_innings_over.add(over_si_instance)
                        current_striker = existing_match.striker
                        existing_match.striker = existing_match.non_striker
                        existing_match.non_striker = current_striker
                        existing_match.second_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.striker.run+=run
                        existing_match.nth_ball+=1
                        existing_match.striker.save()
                        existing_match.save()
                    elif run==2:
                        new_ball = Balls.objects.create(ball_types="Two",runs=run)
                        over_si_instance = existing_match.second_innings_over.last()
                        over_si_instance.ball.add(new_ball)
                        existing_match.second_innings_over.add(over_si_instance)
                        existing_match.second_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.striker.run+=run
                        existing_match.nth_ball+=1
                        existing_match.striker.save()
                        existing_match.save()
                    elif run==3:
                        new_ball = Balls.objects.create(ball_types="Three",runs=run)
                        over_si_instance = existing_match.second_innings_over.last()
                        over_si_instance.ball.add(new_ball)
                        existing_match.second_innings_over.add(over_si_instance)
                        current_striker = existing_match.striker
                        existing_match.striker = existing_match.non_striker
                        existing_match.non_striker = current_striker
                        existing_match.second_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.striker.run+=run
                        existing_match.nth_ball+=1
                        existing_match.striker.save()
                        existing_match.save()
                    elif run==4:
                        new_ball = Balls.objects.create(ball_types="Four",runs=run)
                        over_si_instance = existing_match.second_innings_over.last()
                        over_si_instance.ball.add(new_ball)
                        existing_match.second_innings_over.add(over_si_instance)
                        existing_match.striker.four+=1
                        existing_match.second_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.striker.run+=run
                        existing_match.nth_ball+=1
                        existing_match.striker.save()
                        existing_match.save()
                    elif run==5:
                        new_ball = Balls.objects.create(ball_types="Five",runs=run)
                        over_si_instance = existing_match.second_innings_over.last()
                        over_si_instance.ball.add(new_ball)
                        existing_match.second_innings_over.add(over_si_instance)
                        current_striker = existing_match.striker
                        existing_match.striker = existing_match.non_striker
                        existing_match.non_striker = current_striker
                        existing_match.second_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.striker.run+=run
                        existing_match.nth_ball+=1
                        existing_match.striker.save()
                        existing_match.save()
                    elif run==6:
                        new_ball = Balls.objects.create(ball_types="Six",runs=run)
                        over_si_instance = existing_match.second_innings_over.last()
                        over_si_instance.ball.add(new_ball)
                        existing_match.second_innings_over.add(over_si_instance)
                        existing_match.striker.six+=1
                        existing_match.second_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.striker.run+=run
                        existing_match.nth_ball+=1
                        existing_match.striker.save()
                        existing_match.save()
                    elif run==0:
                        new_ball = Balls.objects.create(ball_types="Dot_ball",runs=run)
                        over_si_instance = existing_match.second_innings_over.last()
                        over_si_instance.ball.add(new_ball)
                        existing_match.second_innings_over.add(over_si_instance)
                        existing_match.second_innings_run+=run
                        existing_match.striker.ball+=1
                        existing_match.striker.run+=run
                        existing_match.nth_ball+=1
                        existing_match.striker.save()
                        existing_match.save()
            return Response("Update Success!",status=200)
        return Response(serializer.errors,status=404)
        
            
class GetOversListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request,*args,**kwargs):
        match_id = kwargs.get("match_id")
        try:
            existing_match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            existing_match = None
        if existing_match == None:
            return Response({match_id:"This match_id does not exist."},status=404)
        
        first_innings_overs_list = existing_match.first_innings_over.all() 
        first_innings_overs_data = []
        if first_innings_overs_list.exists():
            for over in first_innings_overs_list:
                balls = over.ball.all()
                if balls.exists():
                    balls_data = [{
                        "ball_type":ball.ball_types,
                        "runs":ball.runs
                    } for ball in balls]
                else:
                    balls_data = []
                first_innings_overs_data.append({
                    "over_id":over.id,
                    "bowler":over.bowler.__str__(),
                    "balls":balls_data
                })
        else:
            first_innings_overs_data = []

        second_innings_overs_list = existing_match.second_innings_over.all() 
        second_innings_overs_data = []
        if second_innings_overs_list.exists():
            for over in second_innings_overs_list:
                balls = over.ball.all()
                if balls.exists():
                    balls_data = [{
                        "ball_type":ball.ball_types,
                        "runs":ball.runs
                    } for ball in balls]
                else:
                    balls_data = []
                second_innings_overs_data.append({
                    "over_id":over.id,
                    "bowler":over.bowler.__str__(),
                    "balls":balls_data
                })
        else:
            second_innings_overs_data = []
        return Response({
            "fi_all_overs_length":len(first_innings_overs_list),
            "si_all_overs_length":len(second_innings_overs_list),
            "fi_all_overs":existing_match.first_innings_nth_over,
            "si_all_overs":existing_match.second_innings_nth_over,
            "first_innings":first_innings_overs_data,
            "second_innings":second_innings_overs_data
        },status=200)
           
class SelectNewBowlerView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def put(self,request,*args,**kwargs):
        serializer = SelectANewBowlerSerializer(data=request.data)
        if serializer.is_valid():
            match_id = serializer.validated_data.get("match_id")
            bowler_name = serializer.validated_data.get("bowler_name")
            try:
                existing_match = Match.objects.get(id=match_id)
            except Match.DoesNotExist:
                existing_match=None
            if existing_match == None:
                return Response({match_id:"This match_id does not found!"},status=404)
            
            host_team = existing_match.team1
            visitor_team = existing_match.team2
            toss_winner = existing_match.toss_winner
            elected = existing_match.elected

            if existing_match.innings=="1st":
                try:
                    existing_player = Player.objects.get(name=bowler_name)
                except Player.DoesNotExist:
                    existing_player = None
                if existing_player !=None:
                    try:
                        existing_bowler = Bowler.objects.get(player=existing_player)
                    except Bowler.DoesNotExist:
                        existing_bowler = None
                    if existing_bowler!=None:
                        new_over = OverFI.objects.create(bowler=existing_bowler)
                        existing_match.first_innings_over.add(new_over)
                        existing_match.save()
                        return Response({"Success":"Successfully added a new over"},status=202)
                    else:
                        if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                            new_bowler = Bowler.objects.create(player=existing_player,team=visitor_team)
                            new_over = OverFI.objects.create(bowler=new_bowler)
                            existing_match.first_innings_over.add(new_over)
                            existing_match.save()
                            return Response({"Success":"Successfully added a new over"},status=202)
                        if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                            new_bowler = Bowler.objects.create(player=existing_player,team=host_team)
                            new_over = OverFI.objects.create(bowler=new_bowler)
                            existing_match.first_innings_over.add(new_over)
                            existing_match.save()
                            return Response({"Success":"Successfully added a new over"},status=202)
                else:
                    if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                        new_player = Player.objects.create(name=bowler_name,team=visitor_team)
                        new_bowler = Bowler.objects.create(player=new_player,match=existing_match,team=visitor_team)
                        new_over = OverFI.objects.create(bowler=new_bowler)
                        existing_match.first_innings_over.add(new_over)
                        existing_match.save()
                        return Response({"Success":"Successfully added a new over"},status=202)
                    if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                        new_player = Player.objects.create(name=bowler_name,team=host_team)
                        new_bowler = Bowler.objects.create(player=new_player,match=existing_match,team=host_team)
                        new_over = OverFI.objects.create(bowler=new_bowler)
                        existing_match.first_innings_over.add(new_over)
                        existing_match.save()
                        return Response({"Success":"Successfully added a new over"},status=202)
            if existing_match.innings=="2nd":
                try:
                    existing_player = Player.objects.get(name=bowler_name)
                except Player.DoesNotExist:
                    existing_player = None
                if existing_player !=None:
                    try:
                        existing_bowler = Bowler.objects.get(player=existing_player)
                    except Bowler.DoesNotExist:
                        existing_bowler = None
                    if existing_bowler!=None:
                        new_over = OverSI.objects.create(bowler=existing_bowler)
                        existing_match.second_innings_over.add(new_over)
                        existing_match.save()
                        return Response({"Success":"Successfully added a new over"},status=202)
                    else:
                        if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                            new_bowler = Bowler.objects.create(player=existing_player,team=visitor_team)
                            new_over = OverSI.objects.create(bowler=new_bowler)
                            existing_match.second_innings_over.add(new_over)
                            existing_match.save()
                            return Response({"Success":"Successfully added a new over"},status=202)
                        if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                            new_bowler = Bowler.objects.create(player=existing_player,team=host_team)
                            new_over = OverSI.objects.create(bowler=new_bowler)
                            existing_match.second_innings_over.add(new_over)
                            existing_match.save()
                            return Response({"Success":"Successfully added a new over"},status=202)
                else:
                    if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                        new_player = Player.objects.create(name=bowler_name,team=visitor_team)
                        new_bowler = Bowler.objects.create(player=new_player,match=existing_match,team=visitor_team)
                        new_over = OverSI.objects.create(bowler=new_bowler)
                        existing_match.second_innings_over.add(new_over)
                        existing_match.save()
                        return Response({"Success":"Successfully added a new over"},status=202)
                    if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                        new_player = Player.objects.create(name=bowler_name,team=host_team)
                        new_bowler = Bowler.objects.create(player=new_player,match=existing_match,team=host_team)
                        new_over = OverSI.objects.create(bowler=new_bowler)
                        existing_match.second_innings_over.add(new_over)
                        existing_match.save()
                        return Response({"Success":"Successfully added a new over"},status=202)
        return Response(serializer.errors,status=404)
    
class StartSecondInningsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def put(self,request,*args,**kwargs):
        serializer = StartSecondInningsSerializer(data=request.data)
        if serializer.is_valid():
            match_id = serializer.validated_data.get("match_id")
            striker = serializer.validated_data.get("striker")
            non_striker = serializer.validated_data.get("non_striker")
            bowler = serializer.validated_data.get("bowler")
            try:
                existing_match=Match.objects.get(id=match_id)
            except Match.DoesNotExist:
                existing_match = None
            if existing_match==None:
                return Response({match_id:"This match_id does not exist."},status=404)
            existing_match.innings="2nd"
            existing_match.save()
            host_team = existing_match.team1
            visitor_team = existing_match.team2
            elected = existing_match.elected
            toss_winner = existing_match.toss_winner
            try:
                existing_striker_player = Player.objects.get(name=striker)
            except Player.DoesNotExist:
                existing_striker_player = None
            if existing_striker_player!=None:
                if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                    newStrikerBatsman = Batsman.objects.create(player=existing_striker_player,team=visitor_team)
                    existing_match.striker = newStrikerBatsman
                    existing_match.save()
                if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                    newStrikerBatsman = Batsman.objects.create(player=existing_striker_player,team=host_team)
                    existing_match.striker = newStrikerBatsman
                    existing_match.save()
            else:
                if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                    newStrikerPlayer = Player.objects.create(name=striker,team=visitor_team)
                    newStrikerBatsman = Batsman.objects.create(player=newStrikerPlayer,team=visitor_team)
                    existing_match.striker = newStrikerBatsman
                    existing_match.save()
                if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                    newStrikerPlayer = Player.objects.create(name=striker,team=host_team)
                    newStrikerBatsman = Batsman.objects.create(player=newStrikerPlayer,team=host_team)
                    existing_match.striker = newStrikerBatsman
                    existing_match.save()
            try:
                existing_non_striker_player = Player.objects.get(name=non_striker)
            except Player.DoesNotExist:
                existing_non_striker_player = None
            if existing_non_striker_player!=None:
                if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                    newNonStrikerBatsman = Batsman.objects.create(player=existing_non_striker_player,team=visitor_team)
                    existing_match.non_striker = newNonStrikerBatsman
                    existing_match.save()
                if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                    newNonStrikerBatsman = Batsman.objects.create(player=existing_non_striker_player,team=host_team)
                    existing_match.non_striker = newNonStrikerBatsman
                    existing_match.save()
            else:
                if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                    newNonStrikerPlayer = Player.objects.create(name=non_striker,team=visitor_team)
                    newNonStrikerBatsman = Batsman.objects.create(player=newNonStrikerPlayer,team=visitor_team)
                    existing_match.non_striker = newNonStrikerBatsman
                    existing_match.save()
                if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                    newNonStrikerPlayer = Player.objects.create(name=non_striker,team=host_team)
                    newNonStrikerBatsman = Batsman.objects.create(player=newNonStrikerPlayer,team=host_team)
                    existing_match.non_striker = newNonStrikerBatsman
                    existing_match.save()
            try:
                existing_bowler_player = Player.objects.get(name=bowler)
            except Player.DoesNotExist:
                existing_bowler_player = None
            if existing_bowler_player!=None:
                if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                    newBowler = Bowler.objects.create(player=existing_bowler_player,team=host_team)
                    newOver = OverSI.objects.create(bowler=newBowler)
                    existing_match.second_innings_over.add(newOver)
                if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                    newBowler = Bowler.objects.create(player=existing_bowler_player,team=visitor_team)
                    newOver = OverSI.objects.create(bowler=newBowler)
                    existing_match.second_innings_over.add(newOver)
            else:
                if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                    newBowlerPlayer = Player.objects.create(name=bowler,team=host_team)
                    newBowler = Bowler.objects.create(player=newBowlerPlayer,team=host_team)
                    newOver = OverSI.objects.create(bowler=newBowler)
                    existing_match.second_innings_over.add(newOver)
                if toss_winner==host_team and elected=="Bowl" or toss_winner==visitor_team and elected=="Bat":
                    newBowlerPlayer = Player.objects.create(name=bowler,team=visitor_team)
                    newBowler = Bowler.objects.create(player=newBowlerPlayer,team=visitor_team)
                    newOver = OverSI.objects.create(bowler=newBowler)
                    existing_match.second_innings_over.add(newOver)
            return Response({"Success":"Successfully started second innings."})
        return Response(serializer.errors,status=404)
                    

            
    