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
