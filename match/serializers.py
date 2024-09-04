from rest_framework import serializers
from .models import Match

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'


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