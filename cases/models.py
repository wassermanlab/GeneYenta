# cases -- models.py

from django.db import models
from registration.models import Clinician
from django.forms import ModelForm
from django import forms
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
	#User set fields
	clinician = models.ForeignKey(Clinician) #ForeignKey allows many to one; instead of OneToOne
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
	date_added = models.DateField(auto_now_add=True)
	last_modified = models.DateField(auto_now=True)


	def __unicode__(self):
		#unicode() wrapper very important; self.id is an int and must be massaged to unicode
		# otherwise, the admin interface will throw a very confusing error about an 'encode' attribute
		return unicode(self.id) 

# Class: Phenotype
# Represents a single phenotype or symptom associated with a single Patient
# Multiple phenotypes can be linked to a single Patient
# hpo id
# relevancy rating
class Phenotype(models.Model):
	patient = models.ForeignKey(Patient)
	description = models.CharField(max_length=100)
	hpo_id = models.CharField(max_length=100)
	relevancy_score = models.IntegerField(default=0)

	def __unicode__(self):
		return unicode(self.description + '  ' + self.hpo_id)

# Class: PatientForm
# Represents a ModelForm used to create an instance of a Patient
class PatientForm(ModelForm):
	json = forms.CharField(widget=forms.HiddenInput(), required=False) #not sure if safe
	class Meta:
		model = Patient
		exclude = ['clinician','is_archived','date_added','last_modified']
		#widgets = {'first_appointment_date': SelectDateWidget(),}




