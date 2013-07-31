# cases -- admin.py

from django.contrib import admin
from cases.models import Patient, Phenotype

# Model Registration
admin.site.register(Phenotype) 
admin.site.register(Patient) 