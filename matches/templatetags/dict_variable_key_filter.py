from django import template

# Registers this template for use in local Django template library
# Might be unecessary, double-checking in Django docs is required. 
register = template.Library()

# Simply allows a dictionary passed into a Django template
# to be queried by a *template* varaible acting as a key.  
@register.filter
def get_item(dictionary, key):
	return dictionary.get(key)

@register.filter
def to_percentage(value):
	return "{0:.1f}%".format(value*100)

@register.filter
def is_read(value):
	if value:
		return ""
	else:
		return "class=unread"

@register.filter	
def is_matched_patient_id_in_patient_list(patient_list, value):
	ret = [y for y in patient_list if value in y]
	if ret:
		return "id=hide"+str(value);
	else:
		return ""
	
@register.filter
def is_this_the_patient_id(valueOne, valueTwo):
	if valueOne != long(valueTwo):
		return "id=hide"+str(valueOne)
	else:
		return ""

@register.filter
def is_from_case(value):
	if value:
		return "collapse in";
	else:
		return "collapse out";
