#!/usr/bin/env python2.7

import sys
import os
import math
#import MySQLdb
import argparse

sys.path.append('/apps/GeneYenta')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geneyenta.settings")

from cases.models import Patient, Match

NO_MATCH = -1
threshold = .75

def match():
    print "in match routine"

    print "global var = {0}".format(a_global)

def main():
    parser = argparse.ArgumentParser(
        description = 'Match a case to all other cases in the GeneYenta DB'
    )

    parser.add_argument('-id', '--case_id', nargs='?')

    args = parser.parse_args()

    case_id = args.case_id

    case = Patient.objects.get(id=case_id)

    terms = case.phenotype_set.all()

    a_global = 'global'

    print "Case info"
    print case.id
    for t in terms:
        print t.id
    print ""

    match()

if __name__ == "__main__":
    main()
