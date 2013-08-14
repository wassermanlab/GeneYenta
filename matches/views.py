# views.py -- matches

from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from django.core.exceptions import ValidationError

from django.db import models

from django.contrib.auth.models import User
from registration.models import Clinician, ClinicianForm
from cases.models import Patient, Phenotype, PatientForm
from matches.models import Match
# from django.contrib.auth import authenticate, login

#import json
from django.db.models import Q
from django.contrib.auth.decorators import login_required
# from django.core.mail import send_mail
# from geneyenta.settings import EMAIL_HOST_USER
#from django.contrib.auth.decorators import user_passes_test
from helper import forbidden_request, LOGIN_REQUIRED_URL
#from django.contrib import messages


MATCH_THRESHOLD = 0.7

EDIT = True
CREATE = False

# View: view_matches
# Match notification dashboard for authenticated users
@login_required(login_url=LOGIN_REQUIRED_URL)
def view_matches(request):
	user = request.user
	if user.is_authenticated() and user.is_active:
		profile = user.clinician
		# make 2 separate query sets and pass them as appropriate

		#TODO: add a check for is_archived
		#TODO: MATCH_THRESHOLD -- score12 and score21 should be actually a mutual score
		
		users_matches_p1 = Match.objects.filter(
			(Q(patient1__clinician=profile)&Q(score12__gte=MATCH_THRESHOLD))
		)
		users_matches_p2 = Match.objects.filter(
			(Q(patient2__clinician=profile)&Q(score21__gte=MATCH_THRESHOLD))
		)

		context = {'user': user,
		 			'profile': profile,
		 			'matches_p1': users_matches_p1,
		 			'matches_p2': users_matches_p2,}
		return render(request, 'matches/view-matches.html', context)

class Term:
	def __init__(self, rating1, rating2, name):
		self.name = name
		self.user_rating = rating1
		self.other_rating = rating2
		self.html_class = "danger"

def organizePatients(user_patient, other_patient, user, profile):
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
					#'user_phenotypes': user_phenotypes,
					'other_patient': other_patient,
					#'other_phenotypes': other_phenotypes,
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
	if match.patient1.clinician.id == user.clinician.id:
		context = organizePatients(match.patient1, match.patient2, user, user.clinician)
		return render(request, 'matches/match-detail.html', context)
	elif match.patient2.clinician.id == user.clinician.id:
		context = organizePatients(match.patient2, match.patient1, user, user.clinician)
 		return render(request, 'matches/match-detail.html', context)
	else:
		return forbidden_request(request)


# View: matches
# Provides a link to "Find Matches"
@login_required(login_url=LOGIN_REQUIRED_URL)
def matches(request):
	user = request.user
	if user.is_authenticated() and user.is_active:
		profile = user.clinician
		context = {'user': user,
		 			'profile': profile,}
		return render(request, 'matches/matches.html', context)
