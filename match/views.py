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
            # print(request.data)
            match = serializer.save()
            author = request.user.author
            author.match.add(match)
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
            host_team = Team.objects.get_or_create(team_name=host_team_name)[0]
            visitor_team = Team.objects.get_or_create(team_name=visitor_team_name)[0]
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
    def create_opening_player(self,existing_match,striker,non_striker,bowler,batting_team,bowling_team,innings,):
        new_striker_player = Player.objects.create(name=striker,team=batting_team)
        new_non_striker_player = Player.objects.create(name=non_striker,team=batting_team)
        new_bowler_player = Player.objects.create(name=bowler,team=bowling_team)
        new_striker_batsman = Batsman.objects.create(player=new_striker_player,team=batting_team)
        new_non_striker_batsman = Batsman.objects.create(player=new_non_striker_player,team=batting_team)
        new_bowler = Bowler.objects.create(match=existing_match,player=new_bowler_player,team=bowling_team)
        existing_match.current_bowler = new_bowler
        existing_match.striker = new_striker_batsman
        existing_match.non_striker = new_non_striker_batsman
        if innings=="1st":
            new_over = OverFI.objects.create(bowler=new_bowler)
            existing_match.first_innings_over.add(new_over)
        else:
            new_over = OverSI.objects.create(bowler=new_bowler)
            existing_match.second_innings_over.add(new_over)
        existing_match.save()

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
            toss_winner = existing_match.toss_winner
            elected = existing_match.elected
            host_team = existing_match.team1
            visitor_team = existing_match.team2
            if existing_match.innings=="1st":
                if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                    self.create_opening_player(existing_match=existing_match,striker=striker,non_striker=non_striker,bowler=bowler,batting_team=host_team,bowling_team=visitor_team,innings="1st")
                    return Response({"match_id":existing_match.id,"message":"Successfully select opening player."},status=200)
                else:
                    self.create_opening_player(existing_match=existing_match,striker=striker,non_striker=non_striker,bowler=bowler,batting_team=visitor_team,bowling_team=host_team,innings="1st")
                    return Response({"match_id":existing_match.id,"message":"Successfully select opening player."},status=200)   
            else:
                if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                    self.create_opening_player(existing_match=existing_match,striker=striker,non_striker=non_striker,bowler=bowler,batting_team=visitor_team,bowling_team=host_team,innings="2nd")
                    return Response({"match_id":existing_match.id,"message":"Successfully select opening player."},status=200)
                else:
                    self.create_opening_player(existing_match=existing_match,striker=striker,non_striker=non_striker,bowler=bowler,batting_team=host_team,bowling_team=visitor_team,innings="2nd")
                    return Response({"match_id":existing_match.id,"message":"Successfully select opening player."},status=200)   
        return Response(serializer.errors,status=400)
        
            
class UpdateScoreView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]                
    def only_run(self,existing_match,run,ball_types,innings):
        if run==4:
            existing_match.striker.four+=1
            existing_match.striker.save()
        if run==6:
            existing_match.striker.six+=1
            existing_match.striker.save()
        new_ball = Balls.objects.create(ball_types=ball_types,runs=str(run))
        if innings=="1st":
            over_fi_instance = existing_match.first_innings_over.last()
            over_fi_instance.ball.add(new_ball)
            existing_match.first_innings_over.add(over_fi_instance)
            existing_match.first_innings_run+=run
        else:
            over_si_instance = existing_match.second_innings_over.last()
            over_si_instance.ball.add(new_ball)
            existing_match.second_innings_over.add(over_si_instance)
            existing_match.second_innings_run+=run
        existing_match.striker.ball+=1
        existing_match.nth_ball+=1
        existing_match.striker.run+=run
        existing_match.current_bowler.nth_ball+=1
        existing_match.current_bowler.run+=run
        existing_match.current_bowler.save()
        existing_match.striker.save()
        existing_match.save()
        if run==1 or run==3 or run==5:
            current_striker = existing_match.striker
            existing_match.striker = existing_match.non_striker
            existing_match.non_striker = current_striker
            existing_match.save()

    def wide_or_others(self,existing_match,no_ball,run,ball_types,innings):
        if no_ball==True:
            existing_match.striker.run+=run
            existing_match.striker.save()
            if run==4:
                existing_match.striker.four+=1
                existing_match.striker.save()
            if run==6:
                existing_match.striker.six+=1
                existing_match.striker.save()
        if ball_types!="WD" and ball_types!="NB":
            existing_match.nth_ball+=1
            existing_match.current_bowler.nth_ball+=1
            existing_match.current_bowler.save()
            existing_match.striker.ball+=1
            existing_match.striker.save()
        new_ball = Balls.objects.create(ball_types=ball_types,runs=str(run))
        if innings=="1st":
            existing_match.first_innings_run+=(1+run)
            existing_match.current_bowler.run+=(1+run)
            existing_match.current_bowler.save()
            over_fi_instance = existing_match.first_innings_over.last()
            over_fi_instance.ball.add(new_ball)
            existing_match.first_innings_over.add(over_fi_instance)
            existing_match.save()
        else:
            existing_match.second_innings_run+=(1+run)
            existing_match.current_bowler.run+=(1+run)
            existing_match.current_bowler.save()
            over_si_instance = existing_match.second_innings_over.last()
            over_si_instance.ball.add(new_ball)
            existing_match.second_innings_over.add(over_si_instance)
            existing_match.save()
        if run==1 or run==3 or run==5:
            current_striker = existing_match.striker
            existing_match.striker = existing_match.non_striker
            existing_match.non_striker = current_striker
            existing_match.save()

    def wicket(self,existing_match,existing_striker_or_non_striker,bowling_team,batting_team,new_batsman,how_wicket_fall,ball_types,runs,innings,who_helped=None):
        # try:
        #     existing_batsman = Batsman.objects.get(id=existing_striker_or_non_striker.id)
        # except Batsman.DoesNotExist:
        #     return Response({existing_striker_or_non_striker.id:"This batsman id does not exist!"})
        existing_striker_or_non_striker.out_by = existing_match.current_bowler
        existing_striker_or_non_striker.how_wicket_fall = how_wicket_fall
        existing_striker_or_non_striker.is_out = True
        existing_striker_or_non_striker.save()

        if innings=="1st":
            existing_over_instance = existing_match.first_innings_over.last()
            existing_match.first_innings_wicket+=1
        else:
            existing_over_instance = existing_match.second_innings_over.last()
            existing_match.second_innings_wicket+=1

        newBall = Balls.objects.create(ball_types=ball_types,runs=runs)
        existing_match.current_bowler.nth_ball+=1
        existing_match.current_bowler.wicket+=1
        existing_match.current_bowler.save()
        existing_over_instance.ball.add(newBall)
        existing_match.save()
        if who_helped!=None:
            try:
                existing_catch_player = Player.objects.get(name=who_helped)
            except Player.DoesNotExist:
                existing_catch_player = None
            if existing_catch_player!=None:
                try:
                    existing_fielder = Fielder.objects.get(player=existing_catch_player)
                except Fielder.DoesNotExist:
                    existing_fielder = None
                if existing_fielder!=None:
                    existing_striker_or_non_striker.catch_by = existing_fielder
                    existing_striker_or_non_striker.save()
                else:
                    newFielder = Fielder.objects.create(player=existing_catch_player,team=bowling_team)
                    existing_striker_or_non_striker.catch_by = newFielder
                    existing_striker_or_non_striker.save()
            else:
                newCatchPlayer = Player.objects.create(name=who_helped,team=bowling_team)
                newCatchFielder = Fielder.objects.create(player=newCatchPlayer,team=bowling_team)
                existing_striker_or_non_striker.catch_by = newCatchFielder
                existing_striker_or_non_striker.save()
        try:
            existing_new_player = Player.objects.get(name=new_batsman)
        except Player.DoesNotExist:
            existing_new_player = None
        if existing_new_player!=None:
            newBatsman = Batsman.objects.create(player=existing_new_player,team=batting_team)
            if how_wicket_fall=="run_out_non_striker":
                existing_match.non_striker = newBatsman
            else:
                existing_match.striker = newBatsman
                existing_match.save()
            existing_match.save()
        else:
            newPlayer = Player.objects.create(name=new_batsman,team=batting_team)
            newBatsman = Batsman.objects.create(player=newPlayer,team=batting_team)
            if how_wicket_fall=="run_out_non_striker":
                existing_match.non_striker = newBatsman
            else:
                existing_match.striker = newBatsman
                existing_match.save()
            existing_match.save()

    def wide_and_wicket(self,existing_match,run,how_wicket_fall,existing_batsman,existing_over_instance,ball_types,runs,batting_team,bowling_team,new_batsman,wide,no_ball,innings):
        newBall = Balls.objects.create(ball_types=ball_types,runs=runs)
        if innings=="1st":   
            existing_match.first_innings_run+=run
            existing_match.first_innings_wicket+=1
        else:
            existing_match.second_innings_run+=run
            existing_match.second_innings_wicket+=1
        existing_batsman.out_by = existing_match.current_bowler
        existing_batsman.how_wicket_fall = how_wicket_fall
        existing_batsman.is_out = True
        existing_batsman.save()
        existing_match.current_bowler.wicket+=1
        existing_match.current_bowler.save()
        existing_over_instance.ball.add(newBall)
        existing_match.save()

        if wide!=True or no_ball!=True:
            existing_match.current_bowler.run+=run
            existing_match.current_bowler.save()
            existing_match.nth_ball+=1
            try:
                existing_player = Player.objects.get(name=new_batsman)
            except Player.DoesNotExist:
                existing_player = None
            if existing_player!=None:
                newBatsman = Batsman.objects.create(player=existing_player,team=batting_team)
                if how_wicket_fall=="run_out_non_striker":
                    existing_match.non_striker = newBatsman
                else:
                    existing_match.striker = newBatsman
                existing_match.save()
        else:
            newPlayer = Player.objects.create(name=new_batsman,team=batting_team)
            newBatsman = Batsman.objects.create(player=newPlayer,team=batting_team)
            if how_wicket_fall=="run_out_non_striker":
                existing_match.non_striker = newBatsman
            else:
                existing_match.striker = newBatsman
            existing_match.save()  

    def update_score(self,existing_match,toss_winner,host_team,visitor_team,elected,wicket,wide,no_ball,byes,legByes,how_wicket_fall,run,new_batsman,who_helped,innings):
        if innings=="1st" and existing_match.total_over==existing_match.first_innings_nth_over:
            existing_match.save()
            return Response("Second innings started.")
        if innings=="2nd" and existing_match.total_over==existing_match.second_innings_nth_over:
            existing_match.save()
            return Response("Match finished!")
        
        if wicket==True and (wide==True or no_ball==True or byes==True or legByes==True):
            existing_striker = existing_match.striker
            existing_non_striker = existing_match.non_striker
            try:
                if how_wicket_fall=="run_out_non_striker":
                    existing_batsman = Batsman.objects.get(id=existing_non_striker.id)
                else:
                    existing_batsman = Batsman.objects.get(id=existing_striker.id)
            except Batsman.DoesNotExist:
                if how_wicket_fall=="run_out_non_striker":
                    return Response({existing_non_striker.id:"This batsman id does not exist!"})
                else:
                    return Response({existing_striker.id:"This batsman id does not exist!"})
            if innings=="1st":
                existing_over_instance = existing_match.first_innings_over.last()
            else:
                existing_over_instance = existing_match.second_innings_over.last()

            if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                if wide==True and (how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker"):
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="WD&RO",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif wide==True and how_wicket_fall=="stumping":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="WD&S",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif wide==True and how_wicket_fall=="hit_wicket":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="WD&HW",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif no_ball==True and how_wicket_fall=="bowled":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&B",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif no_ball==True and how_wicket_fall=="catch_out":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&CO",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif no_ball==True and (how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker"):
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&RO",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif no_ball==True and how_wicket_fall=="stumping":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&S",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif no_ball==True and how_wicket_fall=="lbw":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&LBW",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif no_ball==True and how_wicket_fall=="hit_wicket":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&HW",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif (byes==True or legByes==True) and (how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker"):
                    if byes==True:
                        self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="BYE&RO",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                    else:
                        self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="LGB&RO",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif (byes==True or legByes==True) and (how_wicket_fall=="stumping"):
                    if byes==True:
                        self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="BYE&S",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                    else:
                        self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="LGB&S",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif (byes==True or legByes==True) and (how_wicket_fall=="hit_wicket"):
                    if byes==True:
                        self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="BYE&HW",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                    else:
                        self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="LGB&HW",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                else:
                    return Response({"error":"This rule does not exist in cricket."})
            else:
                if wide==True and (how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker"):
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="WD&RO",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif wide==True and how_wicket_fall=="stumping":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="WD&S",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif wide==True and how_wicket_fall=="hit_wicket":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="WD&HW",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif no_ball==True and how_wicket_fall=="bowled":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&B",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif no_ball==True and how_wicket_fall=="catch_out":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&CO",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif no_ball==True and (how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker"):
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&RO",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif no_ball==True and how_wicket_fall=="stumping":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&S",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif no_ball==True and how_wicket_fall=="lbw":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&LBW",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif no_ball==True and how_wicket_fall=="hit_wicket":
                    self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&HW",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif (byes==True or legByes==True) and (how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker"):
                    if byes==True:
                        self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="BYE&RO",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                    else:
                        self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="LGB&RO",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif (byes==True or legByes==True) and (how_wicket_fall=="stumping"):
                    if byes==True:
                        self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="BYE&S",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                    else:
                        self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="LGB&S",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif (byes==True or legByes==True) and (how_wicket_fall=="hit_wicket"):
                    if byes==True:
                        self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="BYE&HW",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                    else:
                        self.wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="LGB&HW",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                else:
                    return Response({"error":"This rule does not exist in cricket."})    
            return Response({"Success":"Successfully added a new batsman."})                 

        if wicket==True:
            existing_match.nth_ball+=1
            existing_match.save()
            existing_striker = existing_match.striker
            existing_non_striker = existing_match.non_striker
            if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                if how_wicket_fall=="bowled":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="BO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="catch_out":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="CO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="run_out_striker":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="RO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="run_out_non_striker":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_non_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="RO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="stumping":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="S",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="lbw":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="LBW",runs="0",innings=innings,who_helped=who_helped)   
                if how_wicket_fall=="hit_wicket":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="HW",runs="0",innings=innings,who_helped=who_helped)     
            else:
                if how_wicket_fall=="bowled":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="BO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="catch_out":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="CO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="run_out_striker":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="RO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="run_out_non_striker":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_non_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="RO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="stumping":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="S",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="lbw":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="LBW",runs="0",innings=innings,who_helped=who_helped)   
                if how_wicket_fall=="hit_wicket":
                    self.wicket(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="HW",runs="0",innings=innings,who_helped=who_helped)     
            return Response({"success":"Successfully added a new batsman"},status=200) 


        if wide==True or byes==True or legByes==True or no_ball==True:
            if no_ball==True and (byes==True or legByes==True):
                if byes==True:
                    self.wide_or_others(existing_match=existing_match,no_ball=no_ball,run=run,ball_types="NO&BYE",innings=innings)
                else:
                    self.wide_or_others(existing_match=existing_match,no_ball=no_ball,run=run,ball_types="NO&LB",innings=innings)
            elif byes==True or legByes==True:
                if byes==True:
                    self.wide_or_others(existing_match=existing_match,no_ball=no_ball,run=run,ball_types="BYE",innings=innings)
                else:
                    self.wide_or_others(existing_match=existing_match,no_ball=no_ball,run=run,ball_types="LB",innings=innings)
            elif wide==True:
                self.wide_or_others(existing_match=existing_match,no_ball=no_ball,run=run,ball_types="WD",innings=innings)
            elif no_ball==True:
                self.wide_or_others(existing_match=existing_match,no_ball=no_ball,run=run,ball_types="NB",innings=innings)
            else:
                return Response({"error":"This rule does not exist."})
        else:
            if run==1:
                self.only_run(existing_match=existing_match,run=run,ball_types="One",innings=innings)
            elif run==2:
                self.only_run(existing_match=existing_match,run=run,ball_types="Two",innings=innings)
            elif run==3:
                self.only_run(existing_match=existing_match,run=run,ball_types="Three",innings=innings)
            elif run==4:
                self.only_run(existing_match=existing_match,run=run,ball_types="Four",innings=innings)
            elif run==5:
                self.only_run(existing_match=existing_match,run=run,ball_types="Five",innings=innings)
            elif run==6:
                self.only_run(existing_match=existing_match,run=run,ball_types="Six",innings=innings)
            elif run==0:
                self.only_run(existing_match=existing_match,run=run,ball_types="DB",innings=innings)
        return Response("Update Success!",status=200)

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
                self.update_score(existing_match=existing_match,toss_winner=toss_winner,host_team=host_team,visitor_team=visitor_team,elected=elected,wicket=wicket,wide=wide,no_ball=no_ball,byes=byes,legByes=legByes,how_wicket_fall=how_wicket_fall,run=run,new_batsman=new_batsman,who_helped=who_helped,innings="1st")
            else :
                self.update_score(existing_match=existing_match,toss_winner=toss_winner,host_team=host_team,visitor_team=visitor_team,elected=elected,wicket=wicket,wide=wide,no_ball=no_ball,byes=byes,legByes=legByes,how_wicket_fall=how_wicket_fall,run=run,new_batsman=new_batsman,who_helped=who_helped,innings="2nd")
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
                dot_balls_count = 0
                balls = over.ball.all()
                if balls.exists():
                    balls_data = [{
                        "ball_type":ball.ball_types,
                        "runs":ball.runs
                    } for ball in balls]
                    for ball in balls:
                        if ball.runs=="0":
                            dot_balls_count+=1
                else:
                    balls_data = []
                # if len(balls)==6 and dot_balls_count==6:
                #     try:
                #         if existing_match.innings=="1st":
                #             existing_bowler = Bowler.objects.get(overs_fi=over)
                #             existing_bowler.madien_over+=1
                #         else:
                #             existing_bowler = Bowler.objects.get(overs_si=over)
                #             existing_bowler.madien_over+=1
                #         existing_bowler.save()
                #     except Bowler.DoesNotExist:
                #         return Response({over.id:"This over does not exist!"})

                first_innings_overs_data.append({
                    "over_id":over.id,
                    # "bowler":over.bowler.__str__(),
                     "bowler":{
                        "name":over.bowler.player.name,
                        "madien_over":over.bowler.madien_over,
                        "run":over.bowler.run,
                        "wicket":over.bowler.wicket,
                        "economy_rate":over.bowler.economy_rate,
                        "over":over.bowler.over,
                        "nth_ball":over.bowler.nth_ball,
                    },
                    "balls":balls_data
                })
        else:
            first_innings_overs_data = []

        second_innings_overs_list = existing_match.second_innings_over.all() 
        second_innings_overs_data = []
        if second_innings_overs_list.exists():
            for over in second_innings_overs_list:
                dot_balls_count = 0
                balls = over.ball.all()
                if balls.exists():
                    balls_data = [{
                        "ball_type":ball.ball_types,
                        "runs":ball.runs
                    } for ball in balls]
                    for ball in balls:
                        if ball.runs=="0":
                            dot_balls_count+=1
                else:
                    balls_data = []
                # if len(balls)==6 and dot_balls_count==6:
                #     existing_match.second_innings_over.bowler.madien_over+=1
                #     existing_match.second_innings_over.bowler.save()
                second_innings_overs_data.append({
                    "over_id":over.id,
                    # "bowler":over.bowler.__str__(),
                    "bowler":{
                        "name":over.bowler.player.name,
                        "madien_over":over.bowler.madien_over,
                        "run":over.bowler.run,
                        "wicket":over.bowler.wicket,
                        "economy_rate":over.bowler.economy_rate,
                        "over":over.bowler.over,
                        "nth_ball":over.bowler.nth_ball,
                    },
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
    def add_bowler(self,existing_match,innings,bowler_name,existing_bowler=None,bowling_team=None,existing_player=None):
        if existing_bowler!=None:
            if innings=="1st":
                new_over = OverFI.objects.create(bowler=existing_bowler)
                existing_match.current_bowler=existing_bowler
                existing_match.first_innings_over.add(new_over)
            else:
                new_over = OverSI.objects.create(bowler=existing_bowler)
                existing_match.current_bowler=existing_bowler
                existing_match.second_innings_over.add(new_over)
            existing_match.save()
        elif existing_player!=None:
            new_bowler = Bowler.objects.create(player=existing_player,team=bowling_team)
            if innings=="1st":
                new_over = OverFI.objects.create(bowler=new_bowler)
                existing_match.current_bowler=new_bowler
                existing_match.first_innings_over.add(new_over)
            else:
                new_over = OverSI.objects.create(bowler=new_bowler)
                existing_match.current_bowler=new_bowler
                existing_match.second_innings_over.add(new_over)
            existing_match.save()
        else:
            new_player = Player.objects.create(name=bowler_name,team=bowling_team)
            new_bowler = Bowler.objects.create(player=new_player,match=existing_match,team=bowling_team)
            if innings=="1st":
                new_over = OverFI.objects.create(bowler=new_bowler)
                existing_match.current_bowler=new_bowler
                existing_match.first_innings_over.add(new_over)
            else:
                new_over = OverSI.objects.create(bowler=new_bowler)
                existing_match.current_bowler=new_bowler
                existing_match.second_innings_over.add(new_over)
            existing_match.save()
        return Response({"Success":"Successfully added a new over"},status=202)
    
    def select_bowler(self,existing_match,bowler_name,toss_winner,host_team,visitor_team,elected,innings):
        try:
            existing_player = Player.objects.get(name=bowler_name)
        except Player.DoesNotExist:
            existing_player = None
        try:
            existing_bowler = Bowler.objects.get(player=existing_player)
        except Bowler.DoesNotExist:
            existing_bowler = None
        if existing_player !=None:
            if existing_bowler!=None:
                if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                    self.add_bowler(existing_match=existing_match,innings=innings,bowler_name=bowler_name,existing_bowler=existing_bowler,bowling_team=visitor_team,existing_player=existing_player)
                else:
                    self.add_bowler(existing_match=existing_match,innings=innings,bowler_name=bowler_name,existing_bowler=existing_bowler,bowling_team=visitor_team,existing_player=existing_player)
            else:
                if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                    self.add_bowler(existing_match=existing_match,innings=innings,bowler_name=bowler_name,bowling_team=visitor_team,existing_player=existing_player)
                else:
                    self.add_bowler(existing_match=existing_match,innings=innings,bowler_name=bowler_name,bowling_team=visitor_team,existing_player=existing_player)
        else:
            if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                self.add_bowler(existing_match=existing_match,innings=innings,bowler_name=bowler_name,bowling_team=visitor_team)
            else:
                self.add_bowler(existing_match=existing_match,innings=innings,bowler_name=bowler_name,bowling_team=visitor_team)

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
                self.select_bowler(existing_match=existing_match,bowler_name=bowler_name,toss_winner=toss_winner,host_team=host_team,visitor_team=visitor_team,elected=elected,innings="1st")
            else:
                self.select_bowler(existing_match=existing_match,bowler_name=bowler_name,toss_winner=toss_winner,host_team=host_team,visitor_team=visitor_team,elected=elected,innings="2nd")
        return Response(serializer.errors,status=404)
    
class StartSecondInningsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def add_player(self,existing_match,batting_team,bowling_team,striker,non_striker,bowler,innings,existing_striker_player=None,existing_non_striker_player=None,existing_bowler_player=None):
        existing_match.nth_ball=0
        existing_match.save()
        if existing_striker_player!=None:
            newStrikerBatsman = Batsman.objects.create(player=existing_striker_player,team=batting_team)
            existing_match.striker = newStrikerBatsman
            existing_match.save()
        else:
            newStrikerPlayer = Player.objects.create(name=striker,team=batting_team)
            newStrikerBatsman = Batsman.objects.create(player=newStrikerPlayer,team=batting_team)
            existing_match.striker = newStrikerBatsman
            existing_match.save()

        if existing_non_striker_player!=None:
            newNonStrikerBatsman = Batsman.objects.create(player=existing_non_striker_player,team=batting_team)
            existing_match.non_striker = newNonStrikerBatsman
            existing_match.save()
        else:
            newNonStrikerPlayer = Player.objects.create(name=non_striker,team=batting_team)
            newNonStrikerBatsman = Batsman.objects.create(player=newNonStrikerPlayer,team=batting_team)
            existing_match.non_striker = newNonStrikerBatsman
            existing_match.save()

        if existing_bowler_player!=None:
            newBowler = Bowler.objects.create(player=existing_bowler_player,team=bowling_team)
            existing_match.current_bowler=newBowler
            existing_match.save()
            if innings=="1st":
                newOver = OverFI.objects.create(bowler=newBowler)
                existing_match.first_innings_over.add(newOver)
            else:
                newOver = OverSI.objects.create(bowler=newBowler)
                existing_match.second_innings_over.add(newOver)
        else:
            newBowlerPlayer = Player.objects.create(name=bowler,team=bowling_team)
            newBowler = Bowler.objects.create(player=newBowlerPlayer,team=bowling_team)
            existing_match.current_bowler=newBowler
            existing_match.save()
            if innings=="1st":
                newOver = OverFI.objects.create(bowler=newBowler)
                existing_match.first_innings_over.add(newOver)
            else:
                newOver = OverSI.objects.create(bowler=newBowler)
                existing_match.second_innings_over.add(newOver)

            
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

            try:
                existing_non_striker_player = Player.objects.get(name=non_striker)
            except Player.DoesNotExist:
                existing_non_striker_player = None

            try:
                existing_bowler_player = Player.objects.get(name=bowler)
            except Player.DoesNotExist:
                existing_bowler_player = None

            if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                self.add_player(existing_match=existing_match,batting_team=visitor_team,bowling_team=host_team,striker=striker,non_striker=non_striker,bowler=bowler,innings="2nd",existing_striker_player=existing_striker_player,existing_non_striker_player=existing_non_striker_player,existing_bowler_player=existing_bowler_player)
            else:
                self.add_player(existing_match=existing_match,batting_team=host_team,bowling_team=visitor_team,striker=striker,non_striker=non_striker,bowler=bowler,innings="2nd",existing_striker_player=existing_striker_player,existing_non_striker_player=existing_non_striker_player,existing_bowler_player=existing_bowler_player)
            return Response({"Success":"Successfully started second innings."})
        return Response(serializer.errors,status=404)
                    

            
    