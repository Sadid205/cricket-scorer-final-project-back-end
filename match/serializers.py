from rest_framework import serializers
from .models import Match
from over_fi.serializers import OverFISerializer
from over_si.serializers import OverSISerializer
from bowler.serializers import BowlerSerializer
from team.serializers import TeamSerializer

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class ScoreBoardSerializer(serializers.ModelSerializer):
    team1 = TeamSerializer()
    team2 = TeamSerializer()
    first_innings_over = OverSISerializer(many=True)
    second_innings_over = OverSISerializer(many=True)
    class Meta:
        model = Match
        fields = ['team1','match_status','toss_winner','elected','team2','first_innings_over','second_innings_over','batsman','current_bowler','first_innings_run','first_innings_wicket','first_innings_nth_over','first_innings_nth_ball','second_innings_run','second_innings_wicket','second_innings_nth_over','second_innings_nth_ball']

class MatchListSerializer(serializers.ModelSerializer):
    team1 = TeamSerializer()
    team2 = TeamSerializer()

    class Meta:
        model = Match
        fields = ['id','date','toss_winner','elected','team1','team2','first_innings_run','first_innings_wicket','second_innings_run','second_innings_wicket','first_innings_nth_over','second_innings_nth_over','nth_ball','match_status','first_innings_nth_ball','second_innings_nth_ball']


class StartMatchSerializer(serializers.Serializer):
    host_team_name = serializers.CharField(required=True)
    visitor_team_name = serializers.CharField(required=True)
    toss_winner_team_name = serializers.CharField(required=True)
    elected = serializers.CharField(required=True)
    over = serializers.IntegerField(required=True)
    author_id = serializers.CharField(required=True)

class SelectOpeningPlayerSerializer(serializers.Serializer):
    match_id = serializers.CharField(required=True)
    striker = serializers.CharField(required=True)
    non_striker = serializers.CharField(required=True)
    bowler = serializers.CharField(required=True)

class UpdateScoreSerializer(serializers.Serializer):
    match_id = serializers.CharField(required=True)
    run = serializers.IntegerField(required=True)
    wide = serializers.BooleanField(required=True)
    byes = serializers.BooleanField(required=True)
    legByes = serializers.BooleanField(required=True)
    no_ball = serializers.BooleanField(required=True)
    wicket = serializers.BooleanField()
    how_wicket_fall = serializers.CharField()
    who_helped = serializers.CharField()
    new_batsman = serializers.CharField()

class SelectANewBowlerSerializer(serializers.Serializer):
    match_id = serializers.CharField(required=True)
    bowler_name = serializers.CharField(required=True)

class StartSecondInningsSerializer(serializers.Serializer):
    match_id = serializers.CharField(required=True)
    striker = serializers.CharField(required=True)
    non_striker = serializers.CharField(required=True)
    bowler = serializers.CharField(required=True)