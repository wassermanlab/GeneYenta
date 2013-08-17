from django.db import models
from cases.models import Patient

# Class: Match
# Represents a match from the perspective of one patient.
class Match(models.Model):
	patient = models.ForeignKey(Patient, related_name='+')
	matched_patient = models.ForeignKey(Patient, related_name='+')
	is_read = models.BooleanField()
	is_important = models.BooleanField()
	score = models.FloatField()
	last_matched = models.DateTimeField()
	notes = models.CharField(max_length=450)

	def __unicode__(self):
		return unicode(self.patient) +" : "+ unicode(self.matched_patient)
