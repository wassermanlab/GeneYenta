# helper.py
# Ultimately, this custom module should be placed in a different place.
# Originally, I had more functions defined in this file, but as we refactored
# some of the application code, I ended up moving a lot of these functions
# to the appropriate views.py files.

from django.shortcuts import render
#import json
#from cases.models import Phenotype
#from django.core.exceptions import ValidationError

# Program Wide Constants


# This is the constant value supplied to all login_required function decorators
# If the user is not authenticated (therefore failing the decorator test); 
# they will be redirected to this address
LOGIN_REQUIRED_URL = '/accounts/login/'
#This could be placed in settings.py (may be useful to add a single underscore to stop any collisions)



# Project-Wide Helper Functions
	# Normally used to simplify views code

# Helper Function: forbidden_request
# Returns a http response to an error page indicating
# that the user has tried to access content that is not associated
# with the account.
# e.g. Changing one of the positional url arguments to view
# a page that is not associated with one's account.
def forbidden_request(request):
	return render(request, 'cases/forbidden-request.html',)







