# cases -- views.py

#Python Library Imports
import json
import sys
from subprocess import Popen

#Django Library Imports
from django.shortcuts import render
from django.shortcuts import get_object_or_404 
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

#Model-Related Imports
from django.contrib.auth.models import User
from registration.models import Clinician 
from registration.models import ClinicianForm 
from cases.models import Patient
from cases.models import Phenotype
from cases.models import PatientForm

#Custom Package Imports
from helper import forbidden_request, LOGIN_REQUIRED_URL

from geneyenta.settings import MATCH_BINARY

#Constants
EDIT = True
CREATE = False

#NOTE: Helper functions starting with a single underscore are at the end of the file.

# View: [title]
# [interface description]

# View: view_cases
# List of all unarchived cases associated with given clinician profile
# Provides links to editing patient profiles/cases
@login_required(login_url=LOGIN_REQUIRED_URL)
def view_cases(request):
    user = request.user
    if user.is_authenticated() and user.is_active:
        profile = user.clinician
        patient_list = profile.patient_set.filter(is_archived=False)
        context = {'user': user,
                    'profile': profile,
                    'patient_list': patient_list,}
        return render(request, 'cases/view-cases.html', context)

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
            _process_phenotypes(request, patient, 'patient-json', CREATE)
            messages.success(request, "Case created successfully!", extra_tags='alert alert-success')

            # Run matching process for this patient in the background
            cmd = MATCH_BINARY
            args = []
            args.append(cmd)
            args.append("--patient_id")
            args.append("{0}".format(patient.id))

            #print >>sys.stderr, "match command = {0}".format(' '.join(args))
            p = Popen(args)

            return HttpResponseRedirect('') #redirects to unbound form for another submission
    else:
        patient_form = PatientForm(prefix='patient')
    context = { 'patientform': patient_form, }
    return render(request, 'cases/create-case.html', context)


# View: patient_detail
# Provides a summary for the user of an indiviual case/Patient 
# associated with their account
# IMPORTANT: Since the patient id is passed as an argument via url, it is important
# to make sure that the patient with this id actually belongs to the authenticated user.
# (see more commments below)
@login_required(login_url=LOGIN_REQUIRED_URL)
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    phenotypes = patient.phenotype_set.all() #using related modeli shortcut '_set' lookup

    # Crucial to check whether the user is requesting data that is not
    # associated with their account (the current authenticated User)
    # this simple check should be applied whenever passing arguments through a URL
    if request.user.clinician.id == patient.clinician.id: # IMPORTANT FOR SECURITY
        if request.method == 'POST':
            if patient.is_archived:
                message = "The case you selected was successfully unarchived."
                _change_archive_status(request, 'unarchive', False, message)
                return HttpResponseRedirect(reverse('archives'))
            else:
                message = "The case you selected was successfully archived."
                _change_archive_status(request, 'archive', True, message)
                return HttpResponseRedirect(reverse('view_cases'))
        else:
            if patient.is_archived:
                messages.warning(request, "Please note, this case is currently archived.", extra_tags='alert alert-warning')
            context = {'patient': patient,
                    'phenotypes': phenotypes,}
            return render(request, 'cases/patient-detail.html', context)
    else:
        return forbidden_request(request)


# View: patient_edit
# Provides a form to edit/change an individual Patient model
# IMPORTANT: Since the patient id is passed as an argument via url, it is important
# to make sure that the patient with this id actually belongs to the authenticated user.
@login_required(login_url=LOGIN_REQUIRED_URL)  
def patient_edit(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    phenotypes = patient.phenotype_set.all() #gets all phenotypes linked by FK to the patient
    pheno_dict = {} #python dict. mapping hpo_id's to relevancy scores
    for p in phenotypes:
        pheno_dict[p.hpo_id] = p.relevancy_score

    old_phenotypes_json = json.dumps(pheno_dict) #creates a JSON string that is used to pre-select these phenotypes in the UI

    if request.user.clinician.id == patient.clinician.id: # IMPORTANT FOR SECURITY
        if request.method == 'POST':
            form = PatientForm(request.POST, instance=patient)
            if form.is_valid():
                phenotypes.delete()
                _process_phenotypes(request, patient, 'json', EDIT) #saves newly-selected phenotypes
                form.save()
                messages.success(request, "Your changes were successful!", extra_tags='alert alert-success')
                return HttpResponseRedirect('/')
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
                messages.success(request, "User profile details updated successfully!", extra_tags='alert alert-success')
                return HttpResponseRedirect('') #redirects to unbound form
            else:
                messages.success(request, "There was an error saving your changes, please try again.", extra_tags='alert alert-error')
                print 'profile_edit: failure to save form'
        else:
            form = ClinicianForm(instance=clinician)
            context = {'form': form,
                        'clinician': clinician,}
            return render(request, 'cases/clinician-edit.html', context)
    else:
        return forbidden_request(request)

# View: archives
# Allows the user to unarchive previously archived patients
@login_required(login_url=LOGIN_REQUIRED_URL)
def archives(request):
    user = request.user
    clinician = user.clinician
    if user.is_authenticated() and user.is_active:
        if request.method == 'POST':
            patients_to_unarchive = request.POST.getlist('unarchive')
            for id_number in patients_to_unarchive:
                p = Patient.objects.get(pk=id_number)
                p.is_archived = False
                p.save()
            messages.success(request, "The cases you selected were successfully unarchived." , extra_tags='alert alert-success')
            return HttpResponseRedirect('')
        else:
            archived_patients = clinician.patient_set.filter(is_archived=True)
            context = {'patients': archived_patients,}
            return render(request, 'cases/archives.html', context)
    else:
        return forbidden_request(request)



#Private Helper Functions

# Function: [function name]
# [function description]

# Function: _process_phenotypes
# Completes the string manipulation required to submit/edit phenotypes
# based on a hidden field populated with JSON data 
# Note: the processing differs when the user edits pre-existing data
# vs. submits new data 
def _process_phenotypes(request, patient, getlist_key, flag):
    # Phenotype object processing
    json_str = str(request.POST.getlist(getlist_key)) #gets json as string
    #print json_str
    processed = json_str.replace("[u\'","",1) #removes unecessary prefix [u'
    #print processed
    if flag is EDIT:
        processed = processed.replace("\', u\'\']","",1) #removes uncessary suffix ',u'']
    else:
        processed = processed.replace("\']","",1) #removes uncessary suffix ',u'']
    #print processed
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

# Function: _change_archive_status
# Description: After the user has submitted a form to archive/unarchive a patient
# this fuction retrieves the pk of the patient from the POSTdata and changes the 
# status of is_archived appropriately.
def _change_archive_status(request, key, status, message):
    try:
        patient_id = request.POST.__getitem__(key)
        p = Patient.objects.get(pk=patient_id)
        p.is_archived = status
        messages.success(request, message, extra_tags='alert alert-success')
        p.save()
    except Exception,e:
        print '_change_archive_status failure: '+ str(e)










