from django.apps import apps

def get_team():
    Team = apps.get_model('team','Team')
    return Team
    