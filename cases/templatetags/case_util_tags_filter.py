'''
Created on Apr 27, 2014

@author: jackwu
'''

from django import template

register = template.Library()


@register.filter
def parse_summary(value):
    if len(value) >=40:
        ret_summary = value[0:40] + '...'
    else:
        ret_summary = value
    return ret_summary

