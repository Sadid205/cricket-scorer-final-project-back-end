from django.apps import apps

def get_team():
    Team = apps.get_model('team','Team')
    return Team
    
def get_batsman():
    Batsman = apps.get_model('batsman','Batsman')
    return Batsman
    
def get_bowler():
    Bowler = apps.get_model('bowler','Bowler')
    return Bowler
    
def get_fi_over():
    OverFI = apps.get_model('over_fi','OverFI')
    return OverFI
def get_si_over():
    OverSI = apps.get_model('over_si','OverSI')
    return OverSI
