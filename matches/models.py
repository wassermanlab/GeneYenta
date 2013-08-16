from django.db import models
from cases.models import Patient

# Class: Match
# Represents a match between two patients.
class Match(models.Model):
    # Patient1 should always have a lower patient ID than patient2 as a way
    # to check and avoid duplicate entries
	patient1 = models.ForeignKey(Patient, related_name='+')
	patient2 = models.ForeignKey(Patient, related_name='+')
	score12 = models.FloatField()
	score21 = models.FloatField()
    match_date = models.DateTimeField()
