from django.db import models
from .utilities import get_match
# Create your models here.

class History(models.Model):
    matches = models.ForeignKey('match.Match',related_name="historys",on_delete=models.CASCADE)

    def __str__(self):
        if self.matches and self.matches.team1 and self.matches.team2:
            return f"{self.matches.team1.team_name} vs {self.matches.team2.team_name}"
        return "No Match Assigned"

   
    @staticmethod
    def get_match_model():
        return get_match()
