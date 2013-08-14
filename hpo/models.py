from django.db import models

#
# Class: Term
# Models an HPO term, e.g. HP_0007010: Poor fine motor coordination
#
class Term(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)
    score = models.FloatField()
    parents = models.ManyToManyField('self', through='Parent', 
                                     symmetrical=False,
                                     related_name='parent_of')
    ancestors = models.ManyToManyField('self', through='Ancestor', 
                                     symmetrical=False,
                                     related_name='ancestor_of')


    def __unicode__(self):
        return ': '.join([self.id, self.name])

#
# Class: Parent
# Models a child-parent relationship between the HPO terms.
# NOTES:
# - This is a many-to-many relationship.
# - This could potentially be accomplished by using a ManyToManyField to another
# HPO term ID in the Term class, but it's not clear if or how this works
# when a table is self-referencing
#
class Parent(models.Model):
    child = models.ForeignKey(Term, related_name='child')
    parent = models.ForeignKey(Term, related_name='parent')

    def __unicode__(self):
        return ' --> '.join([self.child.id, self.parent.id])

#
# Class: Ancestor
# Models a child-parent relationship between the HPO terms but differs from
# Parent in that Parent maps HPO terms to *direct* parents only whereas
# this maps the HPO term to all ancestor terms.
# NOTES:
# - See NOTES in Parent class
# - We could combine Parent and Ancestor and just have a boolean field
# indicating if the parent is a direct parent.
#
class Ancestor(models.Model):
    descendent = models.ForeignKey(Term, related_name='descendent')
    ancestor = models.ForeignKey(Term, related_name='ancestor')
    parent_score = models.FloatField()

    def __unicode__(self):
        return ' --> '.join([self.descendent.id, self.ancestor.id])
