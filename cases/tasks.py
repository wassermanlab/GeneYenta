# This file is a test file that was used by Zach Maurer
# to test the feasability of using Celery as a task scheduler
# This code is INCOMPLETE and SHOULD NOT be used for deployment.

from celery import task
from subprocess import call

@task()
def match_cases(): #INCOMPLETE TEST CODE
    call(['python', 'match.py'])
