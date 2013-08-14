# registration -- views.py

from django.shortcuts import render, get_object_or_404

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from registration.models import Clinician, ClinicianForm, UserForm
from django.contrib.auth import authenticate, login

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from geneyenta.settings import EMAIL_HOST_USER


from helper import LOGIN_REQUIRED_URL


# View: [view title]
# [view description]


# View: home_redirect
# If the user is authenticated, then the user is redirected to the inbox.
# If not, the user is redirected to the login page.
def home_redirect(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('matches/view-matches')
	else:
		return HttpResponseRedirect('accounts/login')

# View: registraion
# Allows the user to create an INACTIVE User account and user profile (a Clinician instance)
# This account must be approved by system admins before it can be logged in
def registration(request):
	if request.method == 'POST':
		user_form = UserForm(request.POST, prefix='user')
		clinician_form = ClinicianForm(request.POST, prefix='clinician')
		if user_form.is_valid() and clinician_form.is_valid():
			user = user_form.save(commit=False)
			user.is_active = False # set to be inactive
			user.set_password(user.password) #explicit function call required for password hash
			user.save()
			userprofile = clinician_form.save(commit=False)
			userprofile.user = user
			userprofile.save()
			message = 'Hello,</br> you have registered for GeneYenta. You will be notified when your account has been approved.'
			try:
				send_mail('Confirmation of GeneYenta Registration', message, EMAIL_HOST_USER, [user.email])
			except:
				print('Couldn\'t send email')
			return HttpResponseRedirect('registration-success/')
	else:
		user_form = UserForm(prefix='user')
		clinician_form = ClinicianForm(prefix='clinician')
	context = { 'userform': user_form,
				'userprofileform': clinician_form,}
	return render(request, 'registration/register.html', context)

# View: registration_success
# Returns a basic screen indicating registration success and how the user should proceed
@login_required(login_url=LOGIN_REQUIRED_URL)
def registration_success(request):
	return render(request, 'registration/registration-success.html', )

# View: login_success
# Basic placeholder screen to indicate login success
@login_required(login_url=LOGIN_REQUIRED_URL)
def login_success(request):
	return HttpResponseRedirect(reverse('view_matches'))

# View: change_succsess
# Indicates that the user has successfully changed the password of the account
@login_required(login_url=LOGIN_REQUIRED_URL)
def change_success(request):
	return render(request, 'registration/change-success.html', )

def logout_redirect(request):
	return HttpResponseRedirect(reverse('home'))
