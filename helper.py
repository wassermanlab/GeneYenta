from django.shortcuts import render
#import json
#from cases.models import Phenotype
#from django.core.exceptions import ValidationError

# Program Wide Constants


# This is the constant value supplied to all login_required function decorators
# If the user is not authenticated (therefore failing the decorator test); 
# they will be redirected to this address
LOGIN_REQUIRED_URL = '/geneyenta/accounts/login/'




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







