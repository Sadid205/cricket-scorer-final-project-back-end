from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from balls.models import Balls
from player.models import Player
from fielder.models import Fielder
from batsman.models import Batsman
from match.models import Match
from fielding.models import Fielding
from batting.models import Batting
from bowling.models import Bowling
from partnerships.models import Partnerships
from extras.models import Extras
from partnerships.serializers import PartnershipsSerializer
from extras.serializers import ExtrasSerializer
from fall_of_wickets.models import FallOfWickets

@database_sync_to_async
def add_nth_ball(existing_match):
    bowling = Bowling.objects.filter(player__id=existing_match.current_bowler.player.id).first()
    bowling.balls+=1
    bowling.save()
    existing_match.nth_ball+=1
    if existing_match.innings=="1st":
        existing_match.first_innings_nth_ball+=1
    else:
        existing_match.second_innings_nth_ball+=1
    existing_match.save()

@database_sync_to_async
def get_existing_striker(existing_match):
    return existing_match.striker

@database_sync_to_async
def get_batsman_id(batsman):
    return batsman.id

@database_sync_to_async
def get_first_innings_over_instance(existing_match):
    return existing_match.first_innings_over.last()

@database_sync_to_async
def get_second_innings_over_instance(existing_match):
    return existing_match.second_innings_over.last()

@database_sync_to_async
def get_existing_batsman(striker):
    return Batsman.objects.get(id=striker.id)

@database_sync_to_async
def get_existing_non_striker(existing_match):
    return existing_match.non_striker

@database_sync_to_async
def match_updates(existing_match,innings):
    if innings=="1st" and existing_match.total_over==existing_match.first_innings_nth_over:
        existing_match.save()
        return "Second innings started."
    if innings=="2nd" and existing_match.total_over==existing_match.second_innings_nth_over:
        existing_match.save()
        return "Match finished!"

@database_sync_to_async
def only_run(existing_match,run,ball_types,innings):
    batting = Batting.objects.filter(player__id=existing_match.striker.player.id).first()
    bowling = Bowling.objects.filter(player__id=existing_match.current_bowler.player.id).first()

    existing_partnerships = None
    try:
        existing_partnerships = Partnerships.objects.get(match=existing_match,team=existing_match.striker.team,striker=existing_match.striker,non_striker=existing_match.non_striker)
    except Partnerships.DoesNotExist:
        pass
    try:
        existing_partnerships = Partnerships.objects.get(match=existing_match,team=existing_match.striker.team,striker=existing_match.non_striker,non_striker=existing_match.striker)
    except Partnerships.DoesNotExist:
        pass
    
    if existing_partnerships is not None:
        existing_partnerships.total_run+=run
        existing_partnerships.total_ball+=1
        if existing_match.striker==existing_partnerships.striker:
            existing_partnerships.striker_runs+=run
        else:
            existing_partnerships.non_striker_runs+=run
        existing_partnerships.save()
    
    if run==0:
        bowling.dot_balls+=1
        bowling.save()
    if run==4:
        existing_match.striker.four+=1
        batting.fours+=1
        batting.save()
        existing_match.striker.save()
    if run==6:
        existing_match.striker.six+=1
        batting.sixs+=1
        batting.save()
        existing_match.striker.save()
    new_ball = Balls.objects.create(ball_types=ball_types,runs=str(run))
    if innings=="1st":
        over_fi_instance = existing_match.first_innings_over.last()
        over_fi_instance.ball.add(new_ball)
        existing_match.first_innings_over.add(over_fi_instance)
        existing_match.first_innings_run+=run
        over_fi_instance.scored_runs+=run
        over_fi_instance.save()
    else:
        over_si_instance = existing_match.second_innings_over.last()
        over_si_instance.ball.add(new_ball)
        existing_match.second_innings_over.add(over_si_instance)
        existing_match.second_innings_run+=run
        over_si_instance.scored_runs+=run
        over_si_instance.save()
    existing_match.striker.ball+=1
    existing_match.nth_ball+=1
    if innings=="1st":
        existing_match.first_innings_nth_ball+=1
    else:
        existing_match.second_innings_nth_ball+=1
    existing_match.striker.run+=run
    batting.runs+=run
    batting.balls+=1
    batting.save()
    bowling.runs+=run
    bowling.balls+=1
    bowling.save()
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

@database_sync_to_async
def wide_or_others(existing_match,no_ball,run,ball_types,innings):
    batting = Batting.objects.filter(player__id=existing_match.striker.player.id).first()
    bowling = Bowling.objects.filter(player__id=existing_match.current_bowler.player.id).first()
    existing_extras = None
    try:
        existing_extras = Extras.objects.get(match=existing_match,team=existing_match.striker.team)
    except Extras.DoesNotExist:
        pass
    existing_partnerships = None
    try:
        existing_partnerships = Partnerships.objects.get(match=existing_match,team=existing_match.striker.team,striker=existing_match.striker,non_striker=existing_match.non_striker)
    except Partnerships.DoesNotExist:
        pass
    try:
        existing_partnerships = Partnerships.objects.get(match=existing_match,team=existing_match.striker.team,striker=existing_match.non_striker,non_striker=existing_match.striker)
    except Partnerships.DoesNotExist:
        pass
    if existing_extras is not None:
        if ball_types=="WD":
            existing_extras.wide+=1
        elif ball_types=="NB":
            existing_extras.no_ball+=1
        elif ball_types=="BYE":
            existing_extras.byes+=1
        elif ball_types=="LB":
            existing_extras.leg_byes+=1
        elif ball_types=="NO&LB":
            existing_extras.no_ball+=1
            existing_extras.leg_byes+=1
        elif ball_types=="NO&BYE":
            existing_extras.no_ball+=1
            existing_extras.byes+=1
        else:
            pass
        existing_extras.save()

    if existing_partnerships is not None:
        if ball_types=="WD" or ball_types=="NB":
            existing_partnerships.total_run+=(run+1)
            existing_partnerships.extras+=(run+1)
            if ball_types=="NB":
                if existing_match.striker==existing_partnerships.striker:
                    existing_partnerships.striker_runs+=run
                else:
                    existing_partnerships.non_striker_runs+=run
        elif ball_types=="NO&LB" or ball_types=="NO&BYE":
            existing_partnerships.total_run+=(run+1)
            existing_partnerships.extras+=(run+1)
        else:
            existing_partnerships.total_run+=(run)
            existing_partnerships.total_ball+=1
            existing_partnerships.extras+=run
        existing_partnerships.save()

    if no_ball==True:
        existing_match.striker.run+=run
        batting.runs+=run
        batting.save()
        existing_match.striker.save()
        if run==4:
            existing_match.striker.four+=1
            batting.fours+=1
            batting.save()
            existing_match.striker.save()
        if run==6:
            existing_match.striker.six+=1
            batting.sixs+=1
            batting.save()
            existing_match.striker.save()
    if ball_types!="WD" and ball_types!="NB":
        existing_match.nth_ball+=1
        if existing_match.innings=="1st":
            existing_match.first_innings_nth_ball+=1
        else:
            existing_match.second_innings_nth_ball+=1
        existing_match.current_bowler.nth_ball+=1
        existing_match.current_bowler.save()
        existing_match.striker.ball+=1
        bowling.balls+=1
        bowling.save()
        existing_match.striker.save()
    if ball_types =="WD":
        bowling.wides+=1
        bowling.save()
    if ball_types =="NB":
        bowling.no_balls+=1
        bowling.save()
    new_ball = Balls.objects.create(ball_types=ball_types,runs=str(run))
    if innings=="1st":
        over_fi_instance = existing_match.first_innings_over.last()
        if ball_types=="WD" or ball_types=="NB" or ball_types=="NO&BYE" or ball_types=="NO&LB":
            existing_match.first_innings_run+=(1+run)
            existing_match.current_bowler.run+=(1+run)
            bowling.runs+=(1+run)
            over_fi_instance.scored_runs+=(1+run)
        else:
            existing_match.first_innings_run+=(run)
            existing_match.current_bowler.run+=(run)
            bowling.runs+=(run)
            over_fi_instance.scored_runs+=(1+run)
        bowling.save()
        over_fi_instance.save()
        existing_match.current_bowler.save()
        over_fi_instance = existing_match.first_innings_over.last()
        over_fi_instance.ball.add(new_ball)
        existing_match.first_innings_over.add(over_fi_instance)
        existing_match.save()
    else:
        over_si_instance = existing_match.second_innings_over.last()
        if ball_types=="WD" or ball_types=="NB" or ball_types=="NO&BYE" or ball_types=="NO&LB":
            existing_match.second_innings_run+=(1+run)
            existing_match.current_bowler.run+=(1+run)
            bowling.runs+=(1+run)
            over_si_instance.scored_runs+=(1+run)
        else:
            existing_match.second_innings_run+=(run)
            existing_match.current_bowler.run+=(run)
            bowling.runs+=(run)
            over_si_instance.scored_runs+=(1+run)
        bowling.save()
        over_si_instance.save()
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

@database_sync_to_async
def wicket_function(existing_match,existing_striker_or_non_striker,bowling_team,batting_team,new_batsman,how_wicket_fall,ball_types,runs,innings,who_helped=None):
    batting = Batting.objects.filter(player__id=existing_match.striker.player.id).first()
    bowling = Bowling.objects.filter(player__id=existing_match.current_bowler.player.id).first()
    existing_striker_or_non_striker.out_by = existing_match.current_bowler
    existing_striker_or_non_striker.how_wicket_fall = how_wicket_fall
    existing_striker_or_non_striker.is_out = True
    existing_striker_or_non_striker.save()

    new_fall_of_wicket = FallOfWickets.objects.create(match=existing_match,team=batting_team,batsman=existing_striker_or_non_striker)
    
    newBall = Balls.objects.create(ball_types=ball_types,runs=runs)
    existing_match.current_bowler.nth_ball+=1
    existing_match.current_bowler.wicket+=1
    bowling.wickets+=1
    bowling.balls+=1
    bowling.save()
    batting.number_of_outs+=1
    batting.save()
    existing_match.current_bowler.save()
    existing_match.save()
    fielding = None
    
    if innings=="1st":
        existing_over_instance = existing_match.first_innings_over.last()
        existing_match.first_innings_wicket+=1
        new_fall_of_wicket.nth_over = existing_match.first_innings_nth_over
        new_fall_of_wicket.nth_ball= existing_match.first_innings_nth_ball
        new_fall_of_wicket.save()
    else:
        existing_over_instance = existing_match.second_innings_over.last()
        existing_match.second_innings_wicket+=1
        new_fall_of_wicket.nth_over = existing_match.second_innings_nth_over
        new_fall_of_wicket.nth_ball = existing_match.second_innings_nth_ball
        new_fall_of_wicket.save()
    existing_over_instance.ball.add(newBall)

    if who_helped!=None:
        try:
            existing_catch_player = Player.objects.get(name=who_helped,team=bowling_team)
        except Player.DoesNotExist:
            existing_catch_player = None
        if existing_catch_player!=None:
            fielding = Fielding.objects.get_or_create(player=existing_catch_player,team=bowling_team)[0]
            fielding.matches.add(existing_match)
            fielding.save()
            try:
                existing_fielder = Fielder.objects.get(player=existing_catch_player,team=bowling_team)
            except Fielder.DoesNotExist:
                existing_fielder = None
            if existing_fielder!=None:
                if how_wicket_fall=="catch_out":
                    existing_striker_or_non_striker.catch_by = existing_fielder
                    fielding.catches+=1
                    fielding.save()
                if how_wicket_fall=="stumping":
                    existing_striker_or_non_striker.stumping_by = existing_fielder
                    fielding.stumpings+=1
                    fielding.save()
                if how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker":
                    existing_striker_or_non_striker.run_out_by = existing_fielder
                    fielding.run_outs+=1
                    fielding.save()
                existing_striker_or_non_striker.save()
            else:
                newFielder = Fielder.objects.create(player=existing_catch_player,team=bowling_team)
                if how_wicket_fall=="catch_out":
                    existing_striker_or_non_striker.catch_by = newFielder
                    fielding.catches+=1
                    fielding.save()
                if how_wicket_fall=="stumping":
                    existing_striker_or_non_striker.stumping_by = newFielder
                    fielding.stumpings+=1
                    fielding.save()
                if how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker":
                    existing_striker_or_non_striker.run_out_by = newFielder
                    fielding.run_outs+=1
                    fielding.save()
                existing_striker_or_non_striker.save()
        else:
            newCatchPlayer = Player.objects.create(name=who_helped,team=bowling_team)
            fielding = Fielding.objects.create(player=newCatchPlayer,team=bowling_team)
            fielding.matches.add(existing_match)
            new_fielder = Fielder.objects.create(player=newCatchPlayer,team=bowling_team)
            if how_wicket_fall=="catch_out":
                existing_striker_or_non_striker.catch_by = new_fielder
                fielding.catches+=1
                fielding.save()
            if how_wicket_fall=="stumping":
                existing_striker_or_non_striker.stumping_by = new_fielder
                fielding.stumpings+=1
                fielding.save()
            if how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker":
                existing_striker_or_non_striker.run_out_by = new_fielder
                fielding.run_outs+=1
                fielding.save()
            existing_striker_or_non_striker.save()

    try:
        existing_new_player = Player.objects.get(name=new_batsman,team=batting_team)
    except Player.DoesNotExist:
        existing_new_player = None
    batting = None
    if existing_new_player!=None:
        newBatsman = Batsman.objects.create(match=existing_match,player=existing_new_player,team=batting_team)
        batting = Batting.objects.get_or_create(player=existing_new_player,team=batting_team)[0]
        batting.matches.add(existing_match)
        batting.innings+=1
        batting.save()
        if how_wicket_fall=="run_out_non_striker":
            existing_match.non_striker = newBatsman
            newPartnerships = Partnerships.objects.create(match=existing_match,team=batting_team,striker=existing_match.striker,non_striker=newBatsman)
        else:
            existing_match.striker = newBatsman
            existing_match.save()
            newPartnerships = Partnerships.objects.create(match=existing_match,team=batting_team,striker=newBatsman,non_striker=existing_match.non_striker)
        existing_match.save()
    else:
        newPlayer = Player.objects.create(name=new_batsman,team=batting_team)
        newBatsman = Batsman.objects.create(match=existing_match,player=newPlayer,team=batting_team)
        batting = Batting.objects.create(player=newPlayer,team=batting_team)
        batting.matches.add(existing_match)
        batting.innings+=1
        batting.save()
        if how_wicket_fall=="run_out_non_striker":
            existing_match.non_striker = newBatsman
            newPartnerships = Partnerships.objects.create(match=existing_match,team=batting_team,striker=existing_match.striker,non_striker=newBatsman)
        else:
            existing_match.striker = newBatsman
            existing_match.save()
            newPartnerships = Partnerships.objects.create(match=existing_match,team=batting_team,striker=newBatsman,non_striker=existing_match.non_striker)
        existing_match.save()

@database_sync_to_async
def wide_and_wicket(existing_match,run,how_wicket_fall,existing_batsman,existing_over_instance,ball_types,runs,batting_team,bowling_team,new_batsman,wide,no_ball,innings,who_helped=None):
    batting = Batting.objects.filter(player__id=existing_match.striker.player.id).first()
    bowling = Bowling.objects.filter(player__id=existing_match.current_bowler.player.id).first()
    newBall = Balls.objects.create(ball_types=ball_types,runs=runs)
    existing_extras = None
    try:
        existing_extras = Extras.objects.get(match=existing_match,team=existing_match.striker.team)
    except Extras.DoesNotExist:
        pass
    existing_partnerships = None
    try:
        existing_partnerships = Partnerships.objects.get(match=existing_match,team=existing_match.striker.team,striker=existing_match.striker,non_striker=existing_match.non_striker)
    except Partnerships.DoesNotExist:
        pass

    try:
        existing_partnerships = Partnerships.objects.get(match=existing_match,team=existing_match.striker.team,striker=existing_match.non_striker,non_striker=existing_match.striker)
    except Partnerships.DoesNotExist:
        pass
    if existing_extras is not None:
        existing_extras.wide+=1
        existing_extras.save()
    if existing_partnerships is not None:
        existing_partnerships.extras+=(run+1)
        existing_partnerships.total_run+=(run+1)
        existing_partnerships.save()
    new_fall_of_wicket = FallOfWickets.objects.create(match=existing_match,team=batting_team,batting=existing_batsman)
    if innings=="1st":
        over_fi_instance = existing_match.first_innings_over.last()
        over_fi_instance.scored_runs+=(run+1)
        over_fi_instance.save()
        existing_match.first_innings_run+=(run+1)
        existing_match.first_innings_wicket+=1
        new_fall_of_wicket.nth_over = existing_match.first_innings_nth_over
        new_fall_of_wicket.nth_ball = existing_match.first_innings_nth_ball
        new_fall_of_wicket.save()
    else:
        over_si_instance = existing_match.second_innings_over.last()
        over_si_instance.scored_runs+=(run+1)
        over_si_instance.save()
        existing_match.second_innings_run+=(run+1)
        existing_match.second_innings_wicket+=1
        new_fall_of_wicket.nth_over = existing_match.second_innings_nth_over
        new_fall_of_wicket.nth_ball = existing_match.second_innings_nth_ball
        new_fall_of_wicket.save()
    existing_batsman.out_by = existing_match.current_bowler
    existing_batsman.how_wicket_fall = how_wicket_fall
    existing_batsman.is_out = True
    existing_batsman.save()
    existing_match.current_bowler.wicket+=1
    bowling.wickets+=1
    if wide==True:
        bowling.wides+=1
        bowling.save()
    batting.number_of_outs+=1
    batting.save()
    existing_match.current_bowler.save()
    existing_over_instance.ball.add(newBall)
    existing_match.save()
    fielding=None
    if who_helped!=None:
        try:
            existing_catch_player = Player.objects.get(name=who_helped,team=bowling_team)
        except Player.DoesNotExist:
            existing_catch_player = None
        if existing_catch_player!=None:
            fielding = Fielding.objects.get_or_create(player=existing_catch_player,team=bowling_team)[0]
            fielding.matches.add(existing_match)
            fielding.save()
            try:
                existing_fielder = Fielder.objects.get(player=existing_catch_player,team=bowling_team)
            except Fielder.DoesNotExist:
                existing_fielder = None
            if existing_fielder!=None:
                if how_wicket_fall=="stumping":
                    existing_batsman.stumping_by = existing_fielder
                    fielding.stumpings+=1
                    fielding.save()
                if how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker":
                    existing_batsman.run_out_by = existing_fielder
                    fielding.run_outs+=1
                    fielding.save()
                existing_batsman.save()
            else:
                newFielder = Fielder.objects.create(player=existing_catch_player,team=bowling_team)
                if how_wicket_fall=="stumping":
                    existing_batsman.stumping_by = newFielder
                    fielding.stumpings+=1
                    fielding.save()
                if how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker":
                    existing_batsman.run_out_by = newFielder
                    fielding.run_outs+=1
                    fielding.save()
                existing_batsman.save()
        else:
            newCatchPlayer = Player.objects.create(name=who_helped,team=bowling_team)
            fielding = Fielding.objects.create(player=newCatchPlayer,team=bowling_team)
            fielding.matches.add(existing_match)
            new_fielder = Fielder.objects.create(player=newCatchPlayer,team=bowling_team)
            if how_wicket_fall=="stumping":
                existing_batsman.stumping_by = new_fielder
                fielding.stumpings+=1
                fielding.save()
            if how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker":
                existing_batsman.run_out_by = new_fielder
                fielding.run_outs+=1
                fielding.save()
            existing_batsman.save()

        if wide!=True and no_ball!=True:
            existing_match.current_bowler.run+=run
            bowling.runs+=run
            bowling.balls+=1
            bowling.save()
            existing_match.current_bowler.save()
            existing_match.nth_ball+=1
            if existing_match.innings=="1st":
                existing_match.first_innings_nth_ball+=1
            else:
                existing_match.second_innings_nth_ball+=1
    try:
        existing_player = Player.objects.get(name=new_batsman,team=batting_team)
    except Player.DoesNotExist:
        existing_player = None
    if existing_player!=None:
        newBatsman = Batsman.objects.create(match=existing_match,player=existing_player,team=batting_team)
        newBatting = Batting.objects.get_or_create(player=existing_player,team=batting_team)[0]
        newBatting.matches.add(existing_match)
        newBatting.innings+=1
        newBatting.save()
        if how_wicket_fall=="run_out_non_striker":
            existing_match.non_striker = newBatsman
            newPartnerships = Partnerships.objects.create(match=existing_match,team=batting_team,striker=existing_match.striker,non_striker=newBatsman)
        else:
            existing_match.striker = newBatsman
            newPartnerships = Partnerships.objects.create(match=existing_match,team=batting_team,striker=newBatsman,non_striker=existing_match.non_striker)
        existing_match.save()
    else:
        newPlayer = Player.objects.create(name=new_batsman,team=batting_team)
        newBatsman = Batsman.objects.create(match=existing_match,player=newPlayer,team=batting_team)
        newBatting = Batting.objects.get_or_create(player=newPlayer,team=batting_team)[0]
        newBatting.matches.add(existing_match)
        newBatting.innings+=1
        newBatting.save()
        if how_wicket_fall=="run_out_non_striker":
            existing_match.non_striker = newBatsman
            newPartnerships = Partnerships.objects.create(match=existing_match,team=batting_team,striker=existing_match.striker,non_striker=newBatsman)
        else:
            existing_match.striker = newBatsman
            newPartnerships = Partnerships.objects.create(match=existing_match,team=batting_team,striker=newBatsman,non_striker=existing_match.non_striker)
        existing_match.save()

# @database_sync_to_async
@database_sync_to_async
def save_match(existing_match):
    existing_match.save()

@database_sync_to_async
def retire_batsman(existing_match,retired_batsman,new_batsman):
    batting_team = existing_match.striker.team
    if retired_batsman=="striker":
        existing_match.striker.how_wicket_fall="retired"
        existing_match.striker.is_out = True
        existing_match.striker.save()
    else:
        existing_match.non_striker.how_wicket_fall="retired"
        existing_match.non_striker.is_out = True
        existing_match.non_striker.save()

    try:
        existing_player = Player.objects.get(name=new_batsman,team=batting_team)
    except Player.DoesNotExist:
        existing_player = None
    if existing_player!=None:
        newBatsman = Batsman.objects.create(match=existing_match,player=existing_player,team=batting_team)
        newBatting = Batting.objects.get_or_create(player=existing_player,team=batting_team)[0]
        newBatting.matches.add(existing_match)
        newBatting.innings+=1
        newBatting.save()
        if retired_batsman=="striker":
            existing_match.striker = newBatsman
            newPartnerships = Partnerships.objects.create(match=existing_match,team=batting_team,striker=newBatsman,non_striker=existing_match.non_striker)
        else:
            existing_match.non_striker = newBatsman
            newPartnerships = Partnerships.objects.create(match=existing_match,team=batting_team,striker=existing_match.striker,non_striker=newBatsman)
        existing_match.save()
    else:
        newPlayer = Player.objects.create(name=new_batsman,team=batting_team)
        newBatsman = Batsman.objects.create(match=existing_match,player=newPlayer,team=batting_team)
        newBatting = Batting.objects.get_or_create(player=newPlayer,team=batting_team)[0]
        newBatting.matches.add(existing_match)
        newBatting.innings+=1
        newBatting.save()
        if retired_batsman=="striker":
            existing_match.striker = newBatsman
            newPartnerships = Partnerships.objects.create(match=existing_match,team=batting_team,striker=newBatsman,non_striker=existing_match.non_striker)
        else:
            existing_match.non_striker = newBatsman
            newPartnerships = Partnerships.objects.create(match=existing_match,team=batting_team,striker=existing_match.striker,non_striker=newBatsman)
        existing_match.save()

@database_sync_to_async
def swap(existing_match):
    temp_striker = existing_match.striker
    existing_match.striker = existing_match.non_striker
    existing_match.non_striker = temp_striker
    existing_match.save()

@database_sync_to_async
def add_panalty_run(existing_match,scored_runs,panalty_runs,innings):
    if innings=="1st":
        existing_match.first_innings_run+=(scored_runs+panalty_runs)
    else:
        existing_match.second_innings_run+=(scored_runs+panalty_runs)
        existing_extras = None
    try:
        existing_extras = Extras.objects.get(match=existing_match,team=existing_match.striker.team)
    except Extras.DoesNotExist:
        pass
    existing_partnerships = None
    try:
        existing_partnerships = Partnerships.objects.get(match=existing_match,team=existing_match.striker.team,striker=existing_match.striker,non_striker=existing_match.non_striker)
    except Partnerships.DoesNotExist:
        pass

    try:
        existing_partnerships = Partnerships.objects.get(match=existing_match,team=existing_match.striker.team,striker=existing_match.non_striker,non_striker=existing_match.striker)
    except Partnerships.DoesNotExist:
        pass
    if existing_extras is not None:
        existing_extras.panalty+=panalty_runs
        existing_extras.save()
    if existing_partnerships is not None:
        existing_partnerships.extras+=panalty_runs
        existing_partnerships.total_run+=(scored_runs+panalty_runs)
        existing_partnerships.save()

async def update_score(existing_match,panalty,scored_runs,panalty_runs,swap_batsman,retired_batsman,replaced_batsman,toss_winner,host_team,visitor_team,elected,wicket,wide,no_ball,byes,legByes,how_wicket_fall,run,new_batsman,who_helped,innings):
        await match_updates(existing_match=existing_match,innings=innings)
        if retired_batsman is not None:
            await retire_batsman(existing_match,retired_batsman=retired_batsman,new_batsman=replaced_batsman)
        if panalty==True:
            await add_panalty_run(existing_match,scored_runs,panalty_runs,innings)
        if swap_batsman==True:
            await swap(existing_match)
            
        if wicket==True and (wide==True or no_ball==True or byes==True or legByes==True):
            existing_striker = await get_existing_striker(existing_match=existing_match)
            existing_non_striker = await get_existing_non_striker(existing_match=existing_match)
            try:
                if how_wicket_fall=="run_out_non_striker":
                    existing_batsman = await get_existing_batsman(existing_non_striker)
                else:
                    existing_batsman = await get_existing_batsman(existing_striker)
            except Batsman.DoesNotExist:
                if how_wicket_fall=="run_out_non_striker":
                    return f"{await get_batsman_id(existing_non_striker)}:This batsman id does not exist!"
                else:
                    return f"{await get_batsman_id(existing_striker)}:This batsman id does not exist!"
            if innings=="1st":
                existing_over_instance = await get_first_innings_over_instance(existing_match)
            else:
                existing_over_instance = await get_second_innings_over_instance(existing_match)

            if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                if wide==True and (how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker"):
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="WD&RO",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif wide==True and how_wicket_fall=="stumping":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="WD&S",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif wide==True and how_wicket_fall=="hit_wicket":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="WD&HW",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif no_ball==True and how_wicket_fall=="bowled":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&B",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif no_ball==True and how_wicket_fall=="catch_out":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&CO",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif no_ball==True and (how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker"):
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&RO",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif no_ball==True and how_wicket_fall=="stumping":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&S",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif no_ball==True and how_wicket_fall=="lbw":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&LBW",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings)
                elif no_ball==True and how_wicket_fall=="hit_wicket":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&HW",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif (byes==True or legByes==True) and (how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker"):
                    if byes==True:
                        await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="BYE&RO",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                    else:
                        await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="LGB&RO",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif (byes==True or legByes==True) and (how_wicket_fall=="stumping"):
                    if byes==True:
                        await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="BYE&S",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                    else:
                        await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="LGB&S",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif (byes==True or legByes==True) and (how_wicket_fall=="hit_wicket"):
                    if byes==True:
                        await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="BYE&HW",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                    else:
                        await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="LGB&HW",runs="OUT",batting_team=host_team,bowling_team=visitor_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                else:
                    return "error:This rule does not exist in cricket."
            else:
                if wide==True and (how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker"):
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="WD&RO",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif wide==True and how_wicket_fall=="stumping":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="WD&S",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif wide==True and how_wicket_fall=="hit_wicket":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="WD&HW",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif no_ball==True and how_wicket_fall=="bowled":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&B",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif no_ball==True and how_wicket_fall=="catch_out":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&CO",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif no_ball==True and (how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker"):
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&RO",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif no_ball==True and how_wicket_fall=="stumping":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&S",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif no_ball==True and how_wicket_fall=="lbw":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&LBW",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif no_ball==True and how_wicket_fall=="hit_wicket":
                    await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="NO&HW",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif (byes==True or legByes==True) and (how_wicket_fall=="run_out_striker" or how_wicket_fall=="run_out_non_striker"):
                    if byes==True:
                        await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="BYE&RO",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                    else:
                        await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="LGB&RO",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif (byes==True or legByes==True) and (how_wicket_fall=="stumping"):
                    if byes==True:
                        await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="BYE&S",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                    else:
                        await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="LGB&S",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                elif (byes==True or legByes==True) and (how_wicket_fall=="hit_wicket"):
                    if byes==True:
                        await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="BYE&HW",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                    else:
                        await wide_and_wicket(existing_match=existing_match,run=run,how_wicket_fall=how_wicket_fall,existing_batsman=existing_batsman,existing_over_instance=existing_over_instance,ball_types="LGB&HW",runs="OUT",batting_team=visitor_team,bowling_team=host_team,new_batsman=new_batsman,wide=wide,no_ball=no_ball,innings=innings,who_helped=who_helped)
                else:
                    return "error:This rule does not exist in cricket."    
            return "success:Successfully added a new batsman."                

        if wicket==True:
            existing_striker = await get_existing_striker(existing_match=existing_match)
            existing_non_striker = await get_existing_non_striker(existing_match=existing_match)
            await add_nth_ball(existing_match)
            if toss_winner == host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                if how_wicket_fall=="bowled":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="BO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="catch_out":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="CO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="run_out_striker":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="RO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="run_out_non_striker":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_non_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="RO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="stumping":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="S",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="lbw":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="LBW",runs="0",innings=innings,who_helped=who_helped)   
                if how_wicket_fall=="hit_wicket":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=visitor_team,batting_team=host_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="HW",runs="0",innings=innings,who_helped=who_helped)     
            else:
                if how_wicket_fall=="bowled":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="BO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="catch_out":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="CO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="run_out_striker":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="RO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="run_out_non_striker":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_non_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="RO",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="stumping":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="S",runs="0",innings=innings,who_helped=who_helped)
                if how_wicket_fall=="lbw":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="LBW",runs="0",innings=innings,who_helped=who_helped)   
                if how_wicket_fall=="hit_wicket":
                    await wicket_function(existing_match=existing_match,existing_striker_or_non_striker=existing_striker,bowling_team=host_team,batting_team=visitor_team,new_batsman=new_batsman,how_wicket_fall=how_wicket_fall,ball_types="HW",runs="0",innings=innings,who_helped=who_helped)     
            return "success:Successfully added a new batsman"


        if wide==True or byes==True or legByes==True or no_ball==True:
            if no_ball==True and (byes==True or legByes==True):
                if byes==True:
                    await wide_or_others(existing_match=existing_match,no_ball=no_ball,run=run,ball_types="NO&BYE",innings=innings)
                else:
                    await wide_or_others(existing_match=existing_match,no_ball=no_ball,run=run,ball_types="NO&LB",innings=innings)
            elif byes==True or legByes==True:
                if byes==True:
                    await wide_or_others(existing_match=existing_match,no_ball=no_ball,run=run,ball_types="BYE",innings=innings)
                else:
                    await wide_or_others(existing_match=existing_match,no_ball=no_ball,run=run,ball_types="LB",innings=innings)
            elif wide==True:
                await wide_or_others(existing_match=existing_match,no_ball=no_ball,run=run,ball_types="WD",innings=innings)
            elif no_ball==True:
                await wide_or_others(existing_match=existing_match,no_ball=no_ball,run=run,ball_types="NB",innings=innings)
            else:
                return "error:This rule does not exist."
        else:
            if run==1:
                await only_run(existing_match=existing_match,run=run,ball_types="One",innings=innings)
            elif run==2:
                await only_run(existing_match=existing_match,run=run,ball_types="Two",innings=innings)
            elif run==3:
                await only_run(existing_match=existing_match,run=run,ball_types="Three",innings=innings)
            elif run==4:
                await only_run(existing_match=existing_match,run=run,ball_types="Four",innings=innings)
            elif run==5:
                await only_run(existing_match=existing_match,run=run,ball_types="Five",innings=innings)
            elif run==6:
                await only_run(existing_match=existing_match,run=run,ball_types="Six",innings=innings)
            elif run==0:
                await only_run(existing_match=existing_match,run=run,ball_types="DB",innings=innings)
        await save_match(existing_match=existing_match)
        return "Update Success!"

@database_sync_to_async
def get_match_data(match_id):
    try: 
        existing_match=Match.objects.get(id=match_id)
    except Match.DoesNotExist:
        existing_match = None
    if existing_match is not None:
        return {"existing_match":existing_match,"innings":existing_match.innings,"toss_winner":existing_match.toss_winner,"elected":existing_match.elected,"host_team":existing_match.team1,"visitor_team":existing_match.team2}
    else:
        return None

@database_sync_to_async
def get_updated_match_data(match_id):
    try:
        existing_match = Match.objects.get(id=match_id)
    except Match.DoesNotExist:
        existing_match = None
    if existing_match is not None:
        host_team = existing_match.team1
        visitor_team = existing_match.team2
        elected = existing_match.elected
        toss_winner = existing_match.toss_winner
        innings = existing_match.innings
                
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
             
                first_innings_overs_data.append({
                    "over_id":over.id,
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
                second_innings_overs_data.append({
                    "over_id":over.id,
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

        updated_score = {}
        if innings=="1st":
            updated_score["run"] = existing_match.first_innings_run
            updated_score["wicket"] = existing_match.first_innings_wicket
            updated_score["over"] = existing_match.first_innings_nth_over
            updated_score["run_rate"] = existing_match.first_innings_run_rate
            updated_score["overs_data"] = first_innings_overs_data
            if toss_winner==host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                updated_score["batting_team_name"]=host_team.team_name
            else:
                updated_score["batting_team_name"]=visitor_team.team_name
        else:
            updated_score["run"] = existing_match.second_innings_run
            updated_score["wicket"] = existing_match.second_innings_wicket
            updated_score["over"] = existing_match.second_innings_nth_over
            updated_score["run_rate"] = existing_match.second_innings_run_rate
            updated_score["overs_data"] = second_innings_overs_data
            if toss_winner==host_team and elected=="Bat" or toss_winner==visitor_team and elected=="Bowl":
                updated_score["batting_team_name"]=visitor_team.team_name
            else:
                updated_score["batting_team_name"]=host_team.team_name

        existing_extras = Extras.objects.get(match=existing_match,team=existing_match.striker.team)
        existing_partnerships = Partnerships.objects.filter(match=existing_match,team=existing_match.striker.team) 
        extras_data = ExtrasSerializer(existing_extras).data
        partnerships_data = PartnershipsSerializer(existing_partnerships,many=True).data
        updated_score.update(
            {   "innings":innings,
                "nth_ball":existing_match.nth_ball,
                "status":existing_match.match_status,
                "striker_name":existing_match.striker.player.name,
                "striker_run":existing_match.striker.run,
                "striker_bowl":existing_match.striker.ball,
                "striker_four":existing_match.striker.four,
                "striker_six":existing_match.striker.six,
                "striker_strike_rate":existing_match.striker.strike_rate,
                "non_striker_name":existing_match.non_striker.player.name,
                "non_striker_run":existing_match.non_striker.run,
                "non_striker_bowl":existing_match.non_striker.ball,
                "non_striker_four":existing_match.non_striker.four,
                "non_striker_six":existing_match.non_striker.six,
                "non_striker_strike_rate":existing_match.non_striker.strike_rate,
                "total_over":existing_match.total_over,
                "is_match_finished":existing_match.is_match_finished,
                "extras":extras_data,
                "partnerships":partnerships_data,
                })
        return updated_score
    return None
             
            
               
            
        

class ScoreUpdateReceiveConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.match_id = self.scope['url_route']['kwargs']['match_id']
            self.room_group_name = f'match_{self.match_id}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            match_data = await get_updated_match_data(match_id=self.match_id)
            response_data = "Successfully connected web socket!"
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':'score_update',
                    'match_data':{
                        "response":response_data,
                        "updated_data":match_data
                    }
                }
            )
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error' 'There was an issue with the connection!'
            }))
    async def score_update(self,event):
            match_data = event['match_data']
            await self.send(text_data=json.dumps(match_data))

    
    async def disconnect(self,close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


# score updated started
   
    async def receive(self,text_data):
        data = json.loads(text_data)

        match_id = data.get("match_id")
        run = data.get("run")
        wide = data.get("wide")
        byes = data.get("byes")
        legByes = data.get("legByes")
        no_ball = data.get("no_ball")
        wicket = data.get("wicket")
        how_wicket_fall = data.get("how_wicket_fall")
        who_helped = data.get("who_helped")
        new_batsman = data.get("new_batsman")
        retired_batsman = data.get("retired_batsman")
        replaced_batsman = data.get("replaced_batsman")
        swap_batsman = data.get("swap_batsman")
        panalty = data.get("panalty")
        scored_runs = int(data.get("scored_runs")) if data.get("scored_runs") is not None else None 
        panalty_runs = int(data.get("panalty_runs")) if data.get("panalty_runs") is not None else None
        match_data = await get_match_data(match_id=self.match_id)
        innings = match_data.get("innings")
        existing_match = match_data.get("existing_match")
        toss_winner = match_data.get("toss_winner")
        host_team = match_data.get("host_team")
        visitor_team = match_data.get("visitor_team")
        elected = match_data.get("elected")
        if match_data is not None:
            response_data = await update_score(existing_match,panalty,scored_runs,panalty_runs,swap_batsman,retired_batsman,replaced_batsman,toss_winner,host_team,visitor_team,elected,wicket,wide,no_ball,byes,legByes,how_wicket_fall,run,new_batsman,who_helped,innings)
            updated_data = await get_updated_match_data(match_id=self.match_id)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'score_update',
                'match_data':{
                    "response":response_data,
                    "updated_data":updated_data
                }
            }
        )

    async def score_update(self,event):
        match_data = event['match_data']
        await self.send(text_data=json.dumps(match_data))
            