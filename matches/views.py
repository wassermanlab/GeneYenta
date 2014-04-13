# matches -- views.py


#Django Library Imports
from django.shortcuts import render
from django.shortcuts import get_object_or_404 
from django.http import HttpResponse 
from django.http import HttpResponseRedirect 
from django.template import RequestContext #possibly unecssary b/c of "render()" shortcut
from django.template import loader #possibly unecessary b/c of "render()" shortcut 
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib import messages

#Model-related Imports
from django.contrib.auth.models import User
from registration.models import Clinician
from registration.models import ClinicianForm 
from cases.models import Patient 
from cases.models import Phenotype 
from cases.models import PatientForm
from matches.models import Match

#Custom package imports
from helper import forbidden_request 
from helper import LOGIN_REQUIRED_URL 

#Constants
#MATCH_THRESHOLD = 0.1 #currently unused, all matches regardless of score are shown to the viewer
EDIT = True
CREATE = False


# View: [view name]
# [function description]

# View: view_matches
# Match notification dashboard for authenticated users
# Also allows users to mark indivual cases as important through an 
# AJAX POST request.
# Most of the processing in this function is necessary for the organization of
# data in the template.
#
# The key variable in this data organization is patient_match_dict.
# This dictionary maps patient system id's (primary keys) to lists of Matche objects.
# This allows the UI to display inboxes of matches separated for each of the Clinician's
# patients.
@login_required(login_url=LOGIN_REQUIRED_URL)
def view_matches(request):
	user = request.user
	if user.is_authenticated() and user.is_active:

	#Asynchornous POST request
		#Triggered when an asychronous POST request is sent from the view-matches.html page.
		#Request is sent when the user flags a match notification as important
		if request.is_ajax(): #This may need to be separated into its own view function
			mark_important_match = Match.objects.get(pk=request.POST.__getitem__('match_id'))
			mark_important_match.is_important = request.POST.__getitem__('status')
			if request.POST.__getitem__('status') == 'true': #str comparison is necessary b/c JS's true != Python's True
				mark_important_match.is_important = True
			else:
				mark_important_match.is_important = False
			mark_important_match.save()
			return HttpResponse() #Returns a HTTP response that doesn't change anything/No page refresh
		
	#Normal rendering of page
		else:
			profile = user.clinician

			#BEWARE: Do not use the app name as a variable name for the template.
			#i.e. I used 'matches':matches = Match.objects.filter...
			#I got the strangest errors, where it would iterate over an empty set
			users_matches = Match.objects.filter(patient__clinician=profile).filter(patient__is_archived=False).order_by('-last_matched')

			#This dictionary maps each patient id to an array of matches for that patient.
			patient_match_dict = dict()

			#Maps each patient id to the number of unread messages associated with that patient.
			unread_match_totals = dict()

			#Maps each patient id to the number of important messages associated with that patient.
			important_match_totals = dict()

			for match in users_matches:

				key = match.patient.id

				if key not in patient_match_dict:
					#Creates a empty list of matches and maps that to the match id
					#needed an explicit declaration, rather than '[]' shorthand
					#otherwise it threw error 'Match is not iterable'
					patient_match_dict[key] = list() 
					patient_match_dict[key].append(match)
					
					# Initializes appropriate unread or is_important totals
					if match.is_important:
						important_match_totals[key] = 1
					else:
						important_match_totals[key] = 0
					if match.is_read:
						unread_match_totals[key] = 0
					else:
						unread_match_totals[key] = 1					
				else:
					#Adds the match to the pre-existing list matched to the var key		
					patient_match_dict[key].append(match)

					# Increments appropriate unread or is_important totals					
					if match.is_important:
						new_i = important_match_totals[key] + 1
						important_match_totals[key] = new_i			
					if not match.is_read:
						new_u = unread_match_totals[key] + 1
						unread_match_totals[key] = new_u
			
			context = {'user': user,
			 			'profile': profile,
			 			'match_dict': patient_match_dict,
			 			'unread_dict': unread_match_totals,
			 			'important_dict': important_match_totals,
			 		}
			return render(request, 'matches/view-matches.html', context)

# Helper Class: Term
# Used to simplify unpacking of values in the template-code.
# Used when viewing the match-detail in the UI.
# Allows the comparison of two phenotypes from two different cases to be encapsulated in 
# one object. Thus, it is easy to display whether or not the clinicians have added
# different relevancy scores to each phenotype
class Term:
	def __init__(self, rating1, rating2, name):
		self.name = name
		self.user_rating = rating1
		self.other_rating = rating2
		self.html_class = "danger"

#Helper Function: _organizePatients
# This function creates/returns the context dictionary
# for the match_detail view. 
# This function create
def _organizePatients(user_patient, other_patient, user, profile):
		other_user = other_patient.clinician
		user_phenotypes = Phenotype.objects.filter(patient=user_patient)	
		other_phenotypes = Phenotype.objects.filter(patient=other_patient)

		# A dictionary mapping phenotype descriptions to Term helper-objects.
		# This allows the template code to iterate over all the entries in the dictionary
		# and populate the phenotype summary table by referencing the fields of each Term using the '.' operator.
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

		# Not exactly sure of this code's relevance.
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


# View: match_detail
# This view provides the information required when the user clicks
# 'More Info' link for a given match.  
# Allows users to save notes that they have entered for a given match.
@login_required(login_url=LOGIN_REQUIRED_URL)
def match_detail(request, match_id):
	user = request.user
	match = Match.objects.get(pk=match_id)
	if match.patient.clinician.id == user.clinician.id: #IMPORTANT FOR SECURITY
		if not match.is_read: #sets the unread status to True
			match.is_read = True
			match.save()
		if request.method == 'POST': #True - when the user adds personal notes to the match
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

