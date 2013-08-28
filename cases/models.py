# cases -- models.py

# Django Core Imports
from django import forms

# Model Related Imports
from django.db import models
from registration.models import Clinician
from django.forms import ModelForm

# Widget Imports
#from django.forms.extras.widgets import SelectDateWidget


# Constants
GENDER = (
		('M', 'Male'),
		('F', 'Female'),
		('O', 'Other'),
	)

MONTHS = (
		('jan', 'January'),
		('feb', 'February'),
		('mar', 'March'),
		('apr', 'April'),
		('may', 'May'),
		('jun', 'June'),
		('jul', 'July'),
		('aug', 'August'),
		('sep', 'September'),
		('oct', 'October'),
		('nov', 'November'),
		('dec', 'December'),
	)



# Class: Patient
# Represents an individual clinical case that is associated with a single user via
# ForeignKey link to the Clinician model
class Patient(models.Model):
	# Foreign Key
	clinician = models.ForeignKey(Clinician) #ForeignKey allows many to one; instead of OneToOne
	
	#User set fields
	case_summary = models.TextField(max_length=2500)
	institute = models.CharField(max_length=64)
	clinic = models.CharField(max_length=64)
	gender = models.CharField(max_length=1, choices=GENDER)
	first_appointment_month = models.CharField(max_length=3, choices=MONTHS)
	first_appointment_year = models.IntegerField('Year of first appointment')
	first_appointment_age = models.IntegerField('Age at first appointment')
	is_archived = models.BooleanField(default=False)
	private_id = models.CharField(max_length=20) #encrypted?

	#System-set fields
	date_added = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)


	def __unicode__(self):
		#unicode() wrapper very important; self.id is an int and must be massaged to unicode
		# otherwise, the admin interface will throw a very confusing error about an 'encode' attribute
		return unicode(self.id) 

# Class: Phenotype
# Represents a single phenotype or symptom associated with a single Patient
# Multiple phenotypes can be linked to a single Patient
class Phenotype(models.Model):
	# Foreign Key
	patient = models.ForeignKey(Patient)
	
	hpo_id = models.CharField(max_length=10) #HPO ID from the tree
	relevancy_score = models.IntegerField(default=0) #User-supplied relevancy score (1-5)
	date_added = models.DateTimeField(auto_now_add=True) #automatically added timestamp
	description = models.CharField(max_length=255) #The human-readable name of the phenotype 

	def __unicode__(self):
		return unicode("Patient {0}: {1}".format(self.patient.id, self.hpo_id))

# Class: PatientForm
# Represents a ModelForm used to create an instance of a Patient
class PatientForm(ModelForm):
	# This additional json field is used to capture the phenotype information
	# harvested by the Jquery scripts on the Create A Case or Edit a Case page.
	json = forms.CharField(widget=forms.HiddenInput(), required=False) #not sure if safe
	class Meta:
		model = Patient
		exclude = ['clinician','is_archived','date_added','last_modified']
		#widgets = {'first_appointment_date': SelectDateWidget(),}





