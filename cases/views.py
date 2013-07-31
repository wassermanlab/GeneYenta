# cases -- views.py

from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from django.core.exceptions import ValidationError

from django.db import models

from django.contrib.auth.models import User
from registration.models import Clinician, ClinicianForm
from cases.models import Patient, Phenotype, PatientForm
# from django.contrib.auth import authenticate, login

import json

from django.contrib.auth.decorators import login_required
# from django.core.mail import send_mail
# from geneyenta.settings import EMAIL_HOST_USER
#from django.contrib.auth.decorators import user_passes_test
from helper import forbidden_request, LOGIN_REQUIRED_URL


#### HELPER FUNCTION ######
def process_phenotypes(request, patient, getlist_key):
	# Phenotype object processing
	json_str = str(request.POST.getlist(getlist_key)) #gets json as string
	processed = json_str.replace("[u\'","",1) #removes unecessary prefix [u'
	processed = processed.replace("\', u\'\']","",1) #removes uncessary suffix ',u'']
	# only after processing will it be successfully converted to an array of dictionaries
	json_data = json.loads(processed)
	for term in json_data: #iterates through array
		phenotype = Phenotype() #creates object
		phenotype.relevancy_score = int(term['importance'])
		phenotype.hpo_id = term['hpo_id']
		phenotype.description = term['description']
		phenotype.patient = patient #sets foreign key
		try:
			phenotype.full_clean() #validates fields
			phenotype.save() #saves the object
		except ValidationError as e:
			print e.message_dict + 'Validation error with creating phenotype'



# View: [title]
# [interface description]

# View: inbox
# Match notification dashboard for authenticated users
@login_required(login_url=LOGIN_REQUIRED_URL)
def inbox(request):
	user = request.user
	if user.is_authenticated() and user.is_active:
		profile = user.clinician		
		context = {'user': user,
		 			'profile': profile,}
		return render(request, 'cases/inbox.html', context)

# View: view_cases
# List of all cases associated with given clinician profile
# Provides links to editing patient profiles/cases
@login_required(login_url=LOGIN_REQUIRED_URL)
def view_cases(request):
	user = request.user
	if user.is_authenticated() and user.is_active:
		profile = user.clinician		
		patient_list = profile.patient_set.all()
		context = {'user': user,
		 			'profile': profile,
		 			'patient_list': patient_list,}
		return render(request, 'cases/view-cases.html', context)

# View: matches
# Provides a link to "Find Matches"
@login_required(login_url=LOGIN_REQUIRED_URL)
def matches(request):
	user = request.user
	if user.is_authenticated() and user.is_active:
		profile = user.clinician
		context = {'user': user,
		 			'profile': profile,}
		return render(request, 'cases/matches.html', context)

# View: settings
# Allows user to change Clinician fields ('the user profile') or settings
@login_required(login_url=LOGIN_REQUIRED_URL)
def settings(request):
	user = request.user
	if user.is_authenticated() and user.is_active:
		profile = user.clinician		
		context = {'user': user,
		 			'profile': profile,}
		return render(request, 'cases/settings.html', context)



# View: create_case
# Provides a form to create a new case or Patient model
@login_required(login_url=LOGIN_REQUIRED_URL)
def create_case(request):
	if request.method == 'POST':
		# Creates a 'bound' PatientForm instance
		patient_form = PatientForm(request.POST, prefix='patient')
		if patient_form.is_valid():
			
			# Patient object processing
			patient = patient_form.save(commit=False)
			user_patient = request.user.clinician
			patient.clinician = user_patient
			patient.save() #commits the patient object to the database

			# Phenotype object processing
			process_phenotypes(request, patient, 'patient-json')

			return HttpResponseRedirect('') #redirects to unbound form for another submission
	else:
		patient_form = PatientForm(prefix='patient')
	context = { 'patientform': patient_form, }
	return render(request, 'cases/create-case.html', context)

# View: patient_detail
# Provides a summary for the user of an indiviual case/Patient 
# associated with their account
@login_required(login_url=LOGIN_REQUIRED_URL)
def patient_detail(request, patient_id):
	patient = get_object_or_404(Patient, pk=patient_id)
	phenotypes = patient.phenotype_set.all() #using related model lookup
	# Crucial to check whether the user is requesting data that is not
	# associated with their account (the current authenticated User)
	if request.user.clinician.id == patient.clinician.id: # IMPORTANT FOR SECURITY
		context = {'patient': patient,
					'phenotypes': phenotypes,}
		return render(request, 'cases/patient-detail.html', context)
	else:
		return forbidden_request(request)

# View: patient_edit
# Provides a form to edit/change an individual Patient model
@login_required(login_url=LOGIN_REQUIRED_URL)  
def patient_edit(request, patient_id):
	patient = get_object_or_404(Patient, pk=patient_id)

	phenotypes = patient.phenotype_set.all()
	pheno_dict = {}
	for p in phenotypes:
		pheno_dict[p.hpo_id] = p.relevancy_score
	old_phenotypes_json = json.dumps(pheno_dict)

	if request.user.clinician.id == patient.clinician.id: # IMPORTANT FOR SECURITY
		if request.method == 'POST':
			form = PatientForm(request.POST, instance=patient)
			if form.is_valid():	
				phenotypes.delete()
				process_phenotypes(request, patient, 'json') #saves newly-selected phenotypes
				form.save()
				return HttpResponseRedirect('')
			else:
				print 'patient_edit: form save failure'		
		else:
			form = PatientForm(instance=patient)
			context = {'form': form,
						'patient': patient,
						'old_json':old_phenotypes_json,}
			return render(request, 'cases/patient-edit.html', context)
	else:
		return forbidden_request(request)

# View: profile_edit
# Allows the user to edit their profile information 
# (an instance of the registration.Clinician model)
@login_required(login_url=LOGIN_REQUIRED_URL)  
def profile_edit(request, clinician_id):
	clinician = get_object_or_404(Clinician, pk=clinician_id)
	if request.user.clinician.id == clinician.id: # IMPORTANT FOR SECURITY
		if request.method == 'POST':
			form = ClinicianForm(request.POST, instance=clinician)
			if form.is_valid():
				form.save()
				return HttpResponseRedirect('') #redirects to unbound form
			else:
				print 'profile_edit: failure to save form'		
		else:
			form = ClinicianForm(instance=clinician)
			context = {'form': form,
						'clinician': clinician,}
			return render(request, 'cases/clinician-edit.html', context)
	else:
		return forbidden_request(request)



















