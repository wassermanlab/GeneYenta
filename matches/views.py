# matches -- views.py


#Django Library Imports
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib import messages

#Model-related Imports
from django.contrib.auth.models import User
from registration.models import Clinician, ClinicianForm
from cases.models import Patient, Phenotype, PatientForm
from matches.models import Match

#Custom package imports
from helper import forbidden_request, LOGIN_REQUIRED_URL


#Constants
MATCH_THRESHOLD = 0.7
EDIT = True
CREATE = False


# View: [view name]
# [function description]

# View: view_matches
# Match notification dashboard for authenticated users
@login_required(login_url=LOGIN_REQUIRED_URL)
def view_matches(request):
	user = request.user
	if user.is_authenticated() and user.is_active:
		profile = user.clinician

		#BEWARE: Do not use the app name as a variable name for the template.
		#i.e. I used 'matches':matches = Match.objects.filter...
		#I got the strangest errors, where it would iterate over an empty set
		users_matches = Match.objects.filter(patient__clinician=profile).filter(patient__is_archived=False)

		#This dictionary maps each patient id to an array of matches for that patient.
		#The 0th index of the list is reserved for the number of unread match notifications.
		patient_match_dict = dict()
		unread_match_totals = dict()
		for match in users_matches:
			patient = match.patient
			if patient in patient_match_dict: #uncessary?
				if not match.is_read:
					unread_match_totals[patient.id] += 1
				patient_match_dict[patient.id] += match
			else:
				if match.is_read:
					unread_match_totals[patient.id] = 0
				else:
					unread_match_totals[patient.id] = 1
				patient_match_dict[patient.id] = [match,]		
		context = {'user': user,
		 			'profile': profile,
		 			'match_dict': patient_match_dict,
		 			'unread_dict': unread_match_totals,
		 		}
		return render(request, 'matches/view-matches.html', context)

# Helper Class
# Used to simplify unpacking of values in the template-code
class Term:
	def __init__(self, rating1, rating2, name):
		self.name = name
		self.user_rating = rating1
		self.other_rating = rating2
		self.html_class = "danger"


def _organizePatients(user_patient, other_patient, user, profile):
		other_user = other_patient.clinician
		user_phenotypes = Phenotype.objects.filter(patient=user_patient)	
		other_phenotypes = Phenotype.objects.filter(patient=other_patient)
		phenotype_dict = dict()
		for p in list(user_phenotypes):
			phenotype_dict[p.description] = Term(p.relevancy_score, "N/A", p.description)
		for p in list(other_phenotypes):
			if p.description not in phenotype_dict:
				phenotype_dict[p.description] = Term("N/A", p.relevancy_score, p.description)
			else:
				t = phenotype_dict[p.description]
				t.other_rating = p.relevancy_score
				if t.other_rating == t.user_rating:
					t.html_class = "success"
				else:
					t.html_class = "warning"
		
		phenotypes = list()
		for k in phenotype_dict:
			phenotypes.append(phenotype_dict[k])		

		context = {'user_patient': user_patient,
					'other_patient': other_patient,
					'user': user,
					'profile': profile,
					'other_user': other_user,
					'phenotypes': phenotypes,
					}
		return context


#View: match_detail
#
#
@login_required(login_url=LOGIN_REQUIRED_URL)
def match_detail(request, match_id):
	user = request.user
	match = Match.objects.get(pk=match_id)
	if match.patient.clinician.id == user.clinician.id:
		if not match.is_read:
			match.is_read = True
			match.save()
		if request.method == 'POST':
			try:
				notes = request.POST.__getitem__('notes')
				notes = str(notes).replace("\"","\'") #stops input from escaping function params in html
				print notes
				match.notes = notes
				message = "Your notes were saved successfully."
				messages.success(request, message, extra_tags='alert alert-success')
				match.save()
				return HttpResponseRedirect('')
			except Exception,e:
				print str(e)
		else:
			context = _organizePatients(match.patient, match.matched_patient, user, user.clinician)
			context['current_match'] = match
			return render(request, 'matches/match-detail.html', context)
	else:
		return forbidden_request(request)

