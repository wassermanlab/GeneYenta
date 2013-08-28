# cases -- admin.py

# Model Imports
from django.contrib import admin
from cases.models import Patient
from cases.models import Phenotype

# Model Registration
admin.site.register(Phenotype) 
admin.site.register(Patient) 
