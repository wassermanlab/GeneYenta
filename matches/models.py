# matches -- models.py

# Model-Related Imports
from django.db import models
from cases.models import Patient

# Class: Match
# Represents a match from the perspective of one patient.
# Each Match object encapsulates enough data for one of the two 
# clinicians that are matched together by the system.

# i.e. for one patient pairing or 'match'  made by the system, there will be *two* Match 
# objects that are created.

# Imagine a match between two Patients: Patient A (belonging to Clinician A) and Patient B
# (belonging to Clinician B).
# In this scenario, two Match objects will be created in the data base.
# Match 1 is from the 'perspective' of Patient A and Clincian A.
# 	- the 'patient' field will be a FK to Patient A
#	- the 'matched_patient' will be a FK to Patient B
#	- all other fields, except score and last_matched, are set by
#	Clinician A
#
# Equivalently,
# Match 2 is from the 'perspective' of Patient B and Clincian B.
#       - the 'patient' field will be a FK to Patient B
#       - the 'matched_patient' will be a FK to Patient A
#       - all other fields, except score and last_matched, are set by
#       Clinician B
	
class Match(models.Model):
	
	# Foreign Keys
	patient = models.ForeignKey(Patient, related_name='+')
	matched_patient = models.ForeignKey(Patient, related_name='+')

	is_read = models.BooleanField(default=False) #unread feature like e-mail
	is_important = models.BooleanField(default=False) #user-supplied flag
	score = models.FloatField() #created by the match.py script
	last_matched = models.DateTimeField() #date last matched, created in match.py
	notes = models.CharField(max_length=450) #added by the user 

	def __unicode__(self):
		return unicode(self.patient) +" : "+ unicode(self.matched_patient)
