from django.db import models

#
# Already defined in cases/models.py
#
# Class: Patient
#class Patient(models.Model):
#    GENDER_CHOICES = (
#        ('M', 'Male'),
#        ('F', 'Female'),
#        ('O', 'Other')
#    )
#
#    clinician = models.ForeignKey(Clinician)
#    name = models.CharField(max_length=100)
#    gender = models.CharField(max_length=1,
#                              choices=GENDER_CHOICES)
#    chart_number = models.CharField(max_length=32)
#    summary = models.CharField(max_length=2500)
#
#    def __unicode__(self):
#        return self.name

#
# Class: HPOTerm
# Models an HPO term, e.g. HP_0007010: Poor fine motor coordination
#
class HPOTerm(models.Model):
    name = models.CharField(max_length=255)
    score = models.FloatField()

    def __unicode__(self):
        return ': '.join([self.id, self.name])

#
# Class: HPOParent
# Models an child-parent relationship between the HPO terms.
# NOTES:
# - This is a many-to-many relationship.
# - This could potentially be accomplished by using a ManyToManyField to another
# HPO term ID in the HPOTerm class, but it's not clear if or how this works
# when a table is self-referencing
#
class HPOParent(models.Model):
    id = models.ForeignKey(HPOTerm)
    parent_id = models.ForeignKey(HPOTerm)

    def __unicode__(self):
        return ' --> '.join([self.id, self.parent_id])

#
# Class: HPOLineage
# Models an child-parent relationship between the HPO terms but differs from
# HPOParent in that HPOParent maps HPO terms to *direct* parents only whereas
# this maps the HPO term to all ancestor terms.
# NOTES:
# - See NOTES in HPOParent class
# - We could get combine HPOParent and HPOLineage and just have a boolean field
# indicating if the parent is a direct parent.
#
class HPOLineage(models.Model):
    id = models.ForeignKey(HPOTerm)
    parent_id = models.ForeignKey(HPOTerm)

    def __unicode__(self):
        return ' --> '.join([self.id, self.parent_id])
