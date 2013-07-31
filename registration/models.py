# registration -- models.py

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
	name = models.CharField(max_length=100)
	phone = models.CharField(max_length=32)
	email = models.CharField(max_length=100)
	institute = models.CharField(max_length=100)
	address1 = models.CharField(max_length=100)
	address2 = models.CharField(max_length=100)
	city = models.CharField(max_length=100)
	country = models.CharField(max_length=100)
	postal_code = models.CharField(max_length=24)
	description = models.TextField(max_length=2500)

	def __unicode__(self):
		return self.name

# Form Classes

class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ['username', 'password', 'email']
		widgets = {'password': forms.PasswordInput(),}
    
class ClinicianForm(ModelForm):
    class Meta:
        model = Clinician
    	exclude = ['user']


# Signal Handler Callbacks

# This is a signal handler that is used to notify a user
# if their account has been approved and activated by a
# system administrator. 

@receiver(pre_save, sender=User)
def activation_handler(sender, instance, **kwargs):
	# print('calling activation handler')
	try:
		original = User.objects.get(pk=instance.pk)
	except User.DoesNotExist:
		print('activation_handler exception: User does not exist')
	else:
		if not original.is_active == instance.is_active:
			# print('activation_hanlder: Sending an email...')
			try:
				send_mail('GeneYenta Account Approval', 'Your account has been activated for use.', EMAIL_HOST_USER, [instance.email])
			except:
				print('activation_handler exception: Could not send approval email')

@receiver(pre_save, sender=User)
def password_change_handler(sender, instance, **kwargs):
	# print('calling activation handler')
	try:
		original = User.objects.get(pk=instance.pk)
	except User.DoesNotExist:
		print('password_change_handler exception: User does not exist')
	else:
		if not original.password == instance.password:
			# print('activation_handlder: Sending an email...')
			try:
				send_mail('GeneYenta Password Change', 'Your password has been changed. If you believe your security has been compromised, send an email to zzz@gmail.com', EMAIL_HOST_USER, [instance.email])
			except:
				print('password_change_handler: Could not send approval email')
