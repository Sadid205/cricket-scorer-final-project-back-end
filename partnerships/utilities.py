from django.apps import apps

def get_match():
    Match = apps.get_model('match','Match')
    return Match

def get_batsman():
    Batsman = apps.get_model('batsman','Batsman')
    return Batsman
