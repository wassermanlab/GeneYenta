# registration -- admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from registration.models import Clinician

# Send Mail Imports
from django.core.mail import send_mail
from geneyenta.settings import EMAIL_HOST_USER

# Model Registration
admin.site.register(Clinician) 

# Custom Actions for Admin Interface
def activate_account(self, request, queryset): 
	""" This action allows the admin to bulk activate multiple accounts."""
	queryset.update(is_active=True)
	activate_account.short_description = "Activate selected user account(s)"
	userprofile = Clinician.objects.filter(user=queryset)
	email = userprofile[0].email
	message = "Hello:\r\n\
	You have registered for GeneYenta. \r\n\
	Your account is approved.\r\n\
	Please login to your account here: http://geneyenta.ca \r\n\
	Your username is: " + queryset[0].username
	subject = 'Approval of GeneYenta Registration'
	send_mail(subject, message, EMAIL_HOST_USER, [email])

def deactivate_account(self, request, queryset):
	""" This actions allows the admin to bulk deactivate multple accounts."""
	queryset.update(is_active=False)
deactivate_account.short_description = "Deactivate selected user account(s)"

# Custom Action initialization
UserAdmin.actions = [activate_account, deactivate_account,]

# Custom Admin interface organization
UserAdmin.list_display = ('username','email', 'is_active', 'date_joined', 'is_staff')

# Admin Registration
admin.site.unregister(User) # Necessary
admin.site.register(User, UserAdmin)
