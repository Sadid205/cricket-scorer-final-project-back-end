from django.apps import apps

def get_balls():
    Balls = apps.get_model('balls','Balls')
    return Balls
def get_bowler():
    Bowler = apps.get_model('bowler','Bowler')
    return Bowler
