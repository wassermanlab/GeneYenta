# registration -- views.py

# Url and HTTP response Imports
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Model Imports
from django.contrib.auth.models import User
from registration.models import Clinician
from registration.models import ClinicianForm
from registration.models import UserForm

# Authentication Imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login 

from django.contrib.auth.views import password_reset, password_reset_confirm, password_reset_done

# Send Mail Imports
from django.core.mail import send_mail
from geneyenta.settings import EMAIL_HOST_USER

# Custom imports
from helper import LOGIN_REQUIRED_URL

import os
import mimetypes
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
import time
# View: [view title]
# [view description]



# View: home_redirect
# If the user is authenticated, then the user is redirected to the inbox.
# If not, the user is redirected to the login page.
def home_redirect(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('cases/view-cases')
	else:
		return HttpResponseRedirect('accounts/home')
	
def home(request):
	return render(request, 'registration/home.html',)

# View: registraion
# Allows the user to create an INACTIVE User account and user profile (a Clinician instance)
# This account must be approved by system admins before it can be logged in
def registration(request):
	if request.method == 'POST':
		user_form = UserForm(request.POST, prefix='user')
		clinician_form = ClinicianForm(request.POST, prefix='clinician')


		if user_form.is_valid() and clinician_form.is_valid():
			user = user_form.save(commit=False)
			user.is_active = False  # set to be inactive
			user.set_password(user.password)  # explicit function call required for password hash
			user.save()
			userprofile = clinician_form.save(commit=False)
			userprofile.user = user
			userprofile.save()
			message = "Hello:\r\n\
			You have registered for GeneYenta. \r\n\
			You will be notified when your account has been approved."
			subject = 'Confirmation of GeneYenta Registration'
			adminMessage="\
			A new user has registered for the GeneYenta system. \r\n\
			To approve this registration, please login to the admin interface at http://geneyenta.ca/admin. \r\n\r\n\
			User details follow:\r\n\r\n\
			User ID: " + str(user.id) + "\r\n\
			Name: " + userprofile.full_name() + "\r\n\
			Email: " + str(userprofile.email) + "\r\n\
			Date: " + str(time.strftime("%d/%m/%Y")) + "\r\n";
			
			adminSubject = "A new user is registered."
			huamn = True
			try:
				send_mail(subject, message, EMAIL_HOST_USER, [user.email])
				send_mail(adminSubject, adminMessage, EMAIL_HOST_USER, ['geneyenta_admin@cmmt.ubc.ca'])
			except:
				print('registration.views.registration error: Couldn\'t send email')
			return HttpResponseRedirect('registration-success/')
	else:
		user_form = UserForm(prefix='user')
		clinician_form = ClinicianForm(prefix='clinician')
	context = { 'userform': user_form,
				'userprofileform': clinician_form,
				'next': 'registration-success/', }
	return render(request, 'registration/register.html', context)

# View: registration_success
# Returns a basic screen indicating registration success and how the user should proceed
def registration_success(request):
	return render(request, 'registration/registration-success.html',)

# View: contact_us
def contact_us(request):
	return render(request, 'registration/contact_us.html', {})


# View: login_success
# After a user successfully logs in to the system they are automatically
# redirected to the url that displays the matches for their cases. 
@login_required(login_url=LOGIN_REQUIRED_URL)
def login_success(request):
	return HttpResponseRedirect(reverse('view_cases'))

# View: change_succsess
# Indicates that the user has successfully changed the password of the account
@login_required(login_url=LOGIN_REQUIRED_URL)
def change_success(request):
	return render(request, 'registration/change-success.html',)

# View: logout_redirect
# After loggin out, the user is redirected to the homepage
def logout_redirect(request):
	return HttpResponseRedirect(reverse('home'))


def reset_confirm(request, uidb36=None, token=None):
	return password_reset_confirm(request, template_name='registration/geneyenta_password_reset_confirm.html',
        uidb36=uidb36, token=token, post_reset_redirect=reverse('home'))


def reset(request):
	return password_reset(request, template_name='registration/geneyenta_password_reset_form.html',
        email_template_name='registration/geneyenta_password_reset_email.html')

def download_file(request):
	the_file='/space/apps/GeneYenta/media/GeneYentaSecond.txt'
	filename=os.path.basename(the_file)
	response = HttpResponse(FileWrapper(open(the_file)),
				content_type=mimetypes.guess_type(the_file)[0])
	response['Content-Length'] = os.path.getsize(the_file)
	response['Content-Disposition']="attachment;filename=%s" % filename
	return response	
