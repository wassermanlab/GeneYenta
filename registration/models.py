# registration -- models.py
""" This file contains model class definitions for the user and clinician fields and account administration signal handlers"""

# Imports for models and model fields
from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms

# Imports for signal handlers
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from geneyenta.settings import EMAIL_HOST_USER

# Model Classes

# Class: Clincian
# Encapsulates all data for the 'user profile' or contact information
# associated with a given User
class Clinician(models.Model):
	user = models.OneToOneField(User)
	salutation = models.CharField(max_length=10)
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	phone = models.CharField(max_length=32)
	email = models.CharField(max_length=75)
	institute = models.CharField(max_length=100)
	address1 = models.CharField(max_length=100)
	address2 = models.CharField(max_length=100)
	city = models.CharField(max_length=100)
	country = models.CharField(max_length=100)
	postal_code = models.CharField(max_length=24)
	description = models.TextField(max_length=2500)

	def __unicode__(self):
		return '{0} {1} {2}'.format(self.salutation, self.first_name, self.last_name)

# Form Classes

class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ['username', 'password', 'email']
		widgets = {'password': forms.PasswordInput(),} #hides user password input
    
class ClinicianForm(ModelForm):
    class Meta:
        model = Clinician
    	exclude = ['user']


# Signal Handler Callbacks
# In all cases, the appropriate Django-core function decorator is
# required. 

# This is a signal handler that is used to notify a user
# if their account has been approved and activated by a
# system administrator. 
@receiver(pre_save, sender=User)
def activation_handler(sender, instance, **kwargs):
	subject = 'GeneYenta Account Activation'
	message = 'Your account has been activated for use by \
	a GeneYenta administrator, and you are now able to start adding \
	cases to the system and finding matches.'
	try:
		original = User.objects.get(pk=instance.pk)
	except User.DoesNotExist:
		print('activation_handler exception: User does not exist')
	else:
		if not original.is_active == instance.is_active:
			try:
				send_mail(subject, message, EMAIL_HOST_USER, [instance.email])
			except:
				print('activation_handler exception: Could not send approval email')


# A signal handler to inform users that their password has been changed.
@receiver(pre_save, sender=User)
def password_change_handler(sender, instance, **kwargs):
	subject = 'GeneYenta Password Change'
	message = 'Your password has been changed. If you believe that your security has \
	been compromised, please send an email to root@geneyenta.cmmt.ubc.ca'
	try:
		original = User.objects.get(pk=instance.pk)
	except User.DoesNotExist:
		print('password_change_handler exception: User does not exist')
	else:
		if not original.password == instance.password:
			try:
				send_mail(subject, message, EMAIL_HOST_USER, [instance.email])
			except:
				print('password_change_handler: Could not send approval email')
