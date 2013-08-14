from celery import task
from subprocess import call

@task()
def match_cases():
    call(['python', 'match.py'])