from django.apps import apps

def get_fielder():
    Fielder = apps.get_model('fielder','Fielder')
    return Fielder

# def get_over():
#     Over = apps.get_model('over','Over')
#     return Over

def get_match():
    Match = apps.get_model('match','Match')
    return Match

def get_team():
    Team = apps.get_model('team','Team')
    return Team

def get_bowler():
    Bowler = apps.get_model('bowler','Bowler')
    return Bowler

def get_player():
    Player = apps.get_model('player','Player')
    return Player
