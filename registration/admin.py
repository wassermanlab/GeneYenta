# registration -- admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from registration.models import Clinician

# Model Registration
admin.site.register(Clinician) 

# Custom Actions for Admin Interface
def activate_account(self, request, queryset): 
	""" This action allows the admin to bulk activate multiple accounts."""
	queryset.update(is_active=True)
activate_account.short_description = "Activate selected user account(s)"

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
