#!/usr/local/bin/python2.7
"""
match.py

GeneYenta patient matching.

Written by: Mike Gottlieb (gottlieb@psych.ubc.ca)
Modified by: David Arenillas (dave@cmmt.ubc.ca)

Wasserman Lab
Centre for Molecular Medicine and Therapeutics
Child & Family Research Institute
University of British Columbia

Modifications
-------------
- Added ability to match a single patient to all others instead of just
  matching all patients to all others.
  - Added ability to pass in a patient ID as a command line argument.
- Refactored code so that all DB access is performed through the GYMatcher
  class rather than through the individual Match, Patient classes etc.
- Now use built in Python set classes to handle phenotype term storing and
  comparison.
- Added date checks to determine if existing matches were up to date or needed
  to be modified
  - Compare patient.last_modified to match.last_matched dates.
  - We may add a new patient.phenotype_modified date field to distinguish
    between when a patient is updated generally (case summary updated) vs. 
    phenotype info is updated specifically.
  - Django uses UTC dates so for compatibility, we use the datetime.utcnow()
    to date stamp with current date (MySQL does not provide robust UTC date
    conversions).
- Changed some Camel case to underscore for local variables. Function / method
  names are left in Camel case.
- Updated SQL and print statements to use Python format strings

TO DO
-----
- Re-implement using the GeneYenta Django class models rather than
  re-implementing the classes here and performing low level SQL routines???
  - It would be more consistent and *may* be easier to maintain by doing this,
    but this is debatable
  - It may be less efficient to doing it that way. We have more precise control
    over accessing the SQL and writing efficient queries.

"""
import math
import argparse
import MySQLdb
import smtplib
import time
import logging

from datetime import tzinfo, timedelta, datetime
from email.mime.text import MIMEText

# Maybe these should be passed in as command line arguments
GY_DB_HOST = 'localhost'
GY_DB_USER = 'gyadmin'
GY_DB_PASS = 'gnytdmpw'
GY_DB_NAME = 'GeneYenta'

NO_MATCH_SCORE = -1
PROCESS_RETRIES = 10    # number of times to try match processing
PROCESS_WAIT_TIME = 60  # number of seconds to wait between each
                        # match processing attempt
LOG_FILE = '/apps/GeneYenta/logs/match_process.log'

# XXX set up gyadmin e-mail and update
ADMIN_EMAIL = 'geneyenta_admin@geneyenta.cmmt.ubc.ca'


logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

class Match:
    """
    Class representing a patient to patient match. Models a record in the
    matches_match table of the GeneYenta DB. See also the matches/models.py
    module for the corresponding Django model.

    """

    def __init__(
        self, id, patient_id1, patient_id2, is_read, is_important, score,
        last_matched, notes
    ):
        self.id = id
        self.patient_id = patient_id1
        self.matched_patient_id = patient_id2
        self.is_read = is_read
        self.is_important = is_important
        self.score = score
        self.last_matched = last_matched
        self.notes = notes

    def __str__(self):
        return "{0:d} -> {1:d} = {2} at {3}".format(
            self.patient_id,
            self.matched_patient_id,
            str(self.score),
            self.last_matched.strftime("%Y-%m-%d %H:%M:%S")
        )


class Patient:
    """
    Class representing a patient. Models a record in the cases_patient
    table of the GeneYenta DB. See also the cases/models.py module for the
    corresponding Django model.

    """

    def __init__(self, id, clinician_id, last_modified):
        self.id = id
        self.clinician_id = clinician_id
        self.last_modified = last_modified
        self.terms = None
        self.all_terms = None


class PhenoTerm:
    """
    Class representing a phenotype term. This stores information from both the
    hpo_term and cases_phenotype table of the GeneYenta DB and also stores
    the ancestry information from hpo_ancestor. The ancestors of a term are
    ALL ancestors of the term, not just direct (parent) ancestors.

    """

    def __init__(self, id, term_score, clinician_score):
        self.id = id

        # HPO term score
        self.term_score = term_score

        # clinician assigned relevancy score
        self.clinician_score = clinician_score

        # HPO ancestor terms of this term
        self.ancestors = None

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return "{0} {1} {2}".format(
            self.id, self.term_score, self.clinician_score
        )

class MatchProcess:
    def __init__(self, is_processing, start_date, end_date):
        # boolean indicating processing is in progress
        self.processing = is_processing

        # start datetime of match processing
        self.process_started = start_date

        # finish datetime of match processing
        self.process_finished = end_date

class GYMatcher:
    """
    Main GeneYenta matching class. Responsible for overall program flow and
    managing DB access.

    """

    def __init__(self):
        db = MySQLdb.connect(
            host    = GY_DB_HOST,
            user    = GY_DB_USER,
            passwd  = GY_DB_PASS,
            db      = GY_DB_NAME
        )

        self.db = db

        #
        # XXX
        # Do not store matches! It will blow up the system (run out of
        # memory when there are a large number of matches).
        # DJA 2014/08/07
        # XXX
        #
        #self.new_matches = []
        #self.updated_matches = []

    def isMatchProcessing(self):
        """
        Check if a match process is currently in progress by fetching
        the processing field of the match_process record.
        Returns a boolean.

        """

        sql = "SELECT processing FROM match_process"
        cur = self.db.cursor()
        cur.execute(sql)
        row = cur.fetchone()

        return row[0]

    def setMatchProcessStarted(self):
        """
        Update the match_process record to indicate a match process has
        started.

        """

        # Note we are using local time as opposed to UTC time as this is for
        # administration/logging purposes and not accessed by the Django
        # interface.
        sql = "UPDATE match_process set processing = True, " \
              "process_started = '{0}', process_finished = NULL".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        cur = self.db.cursor()
        cur.execute(sql)

    def setMatchProcessFinished(self):
        """
        Update the match_process record to indicate a match process has
        finished.

        """

        # Note we are using local time as opposed to UTC time as this is for
        # administration/logging purposes and not accessed by the Django
        # interface.
        sql = "UPDATE match_process set processing = False, " \
              "process_finished = '{0}'".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        cur = self.db.cursor()
        cur.execute(sql)

    def fetchPatient(self, patient_id):
        """
        Fetch a patient record from the GeneYenta DB by the patient ID.
        Returns a Patient object.

        """

        sql = "SELECT id, clinician_id, last_modified FROM cases_patient " \
              "where id = {0}".format(patient_id)
        cur = self.db.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        #dt = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
        #patient = Patient(row[0], dt)
        patient = Patient(row[0], row[1], row[2])

        return patient

    def fetchAllPatients(self):
        """
        Fetch all patient records from the GeneYenta DB.
        Return a list of Patient objects.

        """

        sql = "SELECT id, clinician_id, last_modified " \
              "FROM cases_patient order by id"
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

        patients = []
        for row in rows:
            #dt = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
            #patients.append(Patient(row[0], dt))
            patients.append(Patient(row[0], row[1], row[2]))

        return patients

    def fetchPatientPhenoTerms(self, patient):
        """
        Fetch all phenotype terms for a given patient from the GeneYenta DB.
        Sets the patient.terms attribute and returns the set of PhenoTerm
        objects.

        """ 

        sql = "SELECT cp.hpo_id, ht.score, cp.relevancy_score " \
              "FROM cases_phenotype cp, hpo_term ht " \
              "WHERE cp.hpo_id = ht.id and cp.patient_id = {0:d}".format(
            patient.id
        )
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

        terms = set()
        for row in rows:
            terms.add(PhenoTerm(row[0], row[1], row[2]))

        patient.terms = terms

        return terms

    def fetchPhenoTermAncestors(self, term):
        """
        Fetch all ancestor phenotype terms for a phenotype term from the
        GeneYenta DB.
        Sets the term.ancestors attribute and returns the set of PhenoTerm
        objects.

        """

        sql = "SELECT ancestor_id, ancestor_score FROM hpo_ancestor " \
              "WHERE id = '{0}' order by ancestor_score desc".format(
            str(term.id)
        )
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

        ancestors = set()
        for row in rows:
            ancestors.add(PhenoTerm(row[0], row[1], term.clinician_score))

        term.ancestors = ancestors

        return ancestors

    def fetchMatch(self, patient1, patient2):
        """
        Fetch an existing Match record from the matches_match table of the
        GeneYenta DB for the given patient and matched patient (if one exists).
        Returns a Match object (or None).

        """

        id1 = patient1.id
        id2 = patient2.id

        #
        # Old code from when we stored both directional matches in the same
        # record.
        #
        # make sure patient ID 1 is less than patient ID 2
        #if (id2 < id1):
        #    tmp = id1
        #    id1 = id2
        #    id2 = tmp

        sql = "SELECT id, patient_id, matched_patient_id, is_read, " \
              "is_important, score, last_matched, notes " \
              "FROM matches_match " \
              "WHERE patient_id = {0:d} " \
              "AND matched_patient_id = {1:d}".format(id1, id2)
        cur = self.db.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        match = None
        if row:
            #print row
            #dt = datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S")
            match = Match(
                #row[0], row[1], row[2], row[3], row[4], row[5], dt, row[7]
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]
            )

        return match

#    def fetchAllMatches(self):
#        """
#        XXX
#        Do not use this method! It will blow up the system (run out of
#        memory when there are a large number of matches).
#        DJA 2014/08/07
#        XXX
#
#        Fetch all Match records from the matches_match table of the
#        GeneYenta DB.
#        Returns a list of Match objects.
#
#        """
#
#        sql = "SELECT id, patient_id, matched_patient_id, is_read, " \
#              "is_important, score, last_matched, notes " \
#              "FROM matches_match"
#        cur = self.db.cursor()
#        cur.execute(sql)
#        rows = cur.fetchall()
#        matches = []
#        for row in rows:
#            #print row
#            #dt = datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S")
#            matches.append(
#                Match(
#                    #row[0], row[1], row[2], row[3], row[4], row[5], dt, row[7]
#                    row[0], row[1], row[2], row[3], row[4], row[5], row[6],
#                    row[7]
#                )
#            )
#
#        return matches

    def insertMatch(self, match):
        """
        Insert a new Match record into the matches_match table of the
        GeneYenta DB.

        """

        #print "Inserting new match {0}".format(match)
        logging.info("Inserting new match {0}".format(match))
        sql = "INSERT INTO matches_match " \
              "(patient_id, matched_patient_id, is_read, is_important, " \
              "score, last_matched, notes) " \
              "VALUES ({0:d}, {1:d}, {2}, {3}, {4}, '{5}', '{6}')".format(
            match.patient_id,
            match.matched_patient_id,
            match.is_read,
            match.is_important,
            str(match.score),
            match.last_matched.strftime("%Y-%m-%d %H:%M:%S"),
            match.notes
        )
        #print "sql = {0}".format(sql)
        cur = self.db.cursor()
        cur.execute(sql)

    def updateMatch(self, match):
        """
        Update a Match record in the matches_match table of the GeneYenta DB.

        """

        #print "Updating match {0}".format(match)
        logging.info("Updating match {0}".format(match))
        sql = "UPDATE matches_match SET score = {0}, " \
              "is_read = FALSE, last_matched = '{1}' " \
              "WHERE id = {2:d}".format(
            str(match.score),
            match.last_matched.strftime("%Y-%m-%d %H:%M:%S"),
            match.id
        )
        #print "sql = {0}".format(sql)
        cur = self.db.cursor()
        cur.execute(sql)

    def generatePatientPhenoTermSet(self, patient):
        """
        Create a single set containing all the patient's direct phenotype
        terms plus all ancestors of those terms.

        """ 

        if not patient.terms:
            patient.terms = self.fetchPatientPhenoTerms(patient)

        all_terms = set()
        for term in patient.terms:
            all_terms.add(term)

            if not term.ancestors:
                term.ancestors = self.fetchPhenoTermAncestors(term)

            for ancestor_term in term.ancestors:
                all_terms.add(ancestor_term)

        patient.all_terms = all_terms

        return all_terms

    def isUpToDateMatch(self, match, patient1, patient2):
        """
        Determine if the given match is up to date. A match is up to date
        if the match date is at least as recent as the modification dates
        of both of the patients.

        """

        if (match.last_matched >= patient1.last_modified
            and match.last_matched >= patient2.last_modified):
            return True
        else:
            return False
        
    def getPatientMatchPercent(self, patient1, patient2):
        """
        Compute the match score between the two patients based on their
        phenotype terms. The score computed is the unidirectional score of
        patient1 to patient2.

        """

        #print "Getting match percent for patients {0} and {1}".format(
        #    patient1.id,
        #    patient2.id
        #)

        if not patient1.terms:
            self.fetchPatientPhenoTerms(patient1)

        if not patient1.terms:
            #print "Patient {0} has no phenotype terms associated".format(
            #    patient1.id
            #)
            logging.warning(
                "Patient {0} has no phenotype terms associated".format(
                    patient1.id
                )
            )
            return 0

        if not patient2.terms:
            self.fetchPatientPhenoTerms(patient2)

        if not patient2.terms:
            #print "Patient {0} has no phenotype terms associated".format(
            #    patient2.id
            #)
            logging.warning(
                "Patient {0} has no phenotype terms associated".format(
                    patient2.id
                )
            )
            return 0

        if not patient2.all_terms:
            self.generatePatientPhenoTermSet(patient2)

        matchNumerator = 0
        matchDenominator = 0
        for p1_term in patient1.terms:
            #print "term to match = {0}".format(p1_term)

            matchDenominator += (p1_term.clinician_score * p1_term.term_score)

            best_match = self.findBestPhenoTermMatch(
                p1_term, patient2.all_terms
            )

            if best_match:
                #print "best term match = {0}".format(best_match)

                matchNumerator += (
                    p1_term.clinician_score * best_match.term_score
                )
            else:
                # This should not happen
                #print "WARNING: term {0} not matched!!!".format(p1_term)
                logging.error("term {0} not matched!!!".format(p1_term))

        #print "match numerator {0}".format(matchNumerator)
        #print "match denominator {0}".format(matchDenominator)

        match_score = 0
        if matchDenominator > 0:
            match_score = matchNumerator / matchDenominator

        return match_score

    def findBestPhenoTermMatch(self, term, term_set):
        """
        Find the best matching phenotype term from a set of terms. The term
        is the phenotype term being matched and term_set contains the set
        being searched. This should be a set from a patient containing all
        direct terms and ancestor terms, i.e. constructed with the
        generatePatientPhenoTermSet method. If the term does not directly
        match any term in term_set then all ancestors of given term are
        compared to term set and the best scoring term (term with the highest
        term_score) is returned.

        """

        best_match = None
        for term2 in term_set:
            if term2.id == term.id:
                # Term directly matches a term in the term_set, so return it.
                best_match = term2
                break

        if not best_match:
            # If term does not directly match a term in the term_set, find
            # all of it's ancestors in the term_set and return the highest
            # scoring one.
            if not term.ancestors:
                self.fetchPhenoTermAncestors(term)

            best_score = NO_MATCH_SCORE
            for ancestor in term.ancestors:
                for term2 in term_set:
                    if term2.id == ancestor.id:
                        if ancestor.term_score > best_score:
                            # NOTE: the ancestor terms are stored sorted in the
                            # database and are sorted by highest to lowest score
                            # on retrieval (just to be sure), so we *should* be
                            # able to just return the first match.
                            best_score = ancestor.term_score
                            best_match = ancestor
            
        return best_match

    def matchPatientToPatient(self, patient1, patient2, force):
        """
        Compute the one-way match score from patient1 to patient2 based on
        their phenotype terms and update the database accordingly.
        Check if a match already exists and whether it is up to date.
        If no match exists it is computed and saved in the database. If a
        match exists but is not up to date the new match score is computed
        and the match updated in the DB. If a match exists and is up to date
        the matching is skipped.

        """

        existing_match = self.fetchMatch(patient1, patient2)

        if existing_match:
            is_up_to_date_match = False

            #
            # If force match is set, do matching regardless of whether a match
            # already exists and is up to date.
            #
            if not force:
                is_up_to_date_match = self.isUpToDateMatch(
                    existing_match, patient1, patient2
                )

            if is_up_to_date_match:
                #print "Existing match {0} is up to date".format(existing_match)
                logging.info("Existing match {0} is up to date".format(
                    existing_match
                ))
            else:
                score = self.getPatientMatchPercent(patient1, patient2)

                # Update match with new score. Set the is_read flag to false
                # and update the date to current time.
                # Note we use UTC time to be consistent with the Django
                # interface.
                existing_match.score = score
                existing_match.is_read = False
                existing_match.last_matched = datetime.utcnow()

                self.updateMatch(existing_match)
                #self.updated_matches.append(existing_match)
        else:
            score = self.getPatientMatchPercent(patient1, patient2)

            # Note: giving new_match a dummy id of 0. The id is an
            # auto-increment field which will be updated by the SQL server.
            # Note we use UTC time to be consistent with the Django
            # interface.
            new_match = Match(
                0, patient1.id, patient2.id, False, False, score,
                datetime.utcnow(), ''
            )

            self.insertMatch(new_match)
            #self.new_matches.append(new_match)

    def matchPatientToAll(self, patient, force):
        """
        Compute matches of the given patient to all other patients in the
        GeneYenta DB and update the database accordingly. Do not match
        patient to him/herself or to other patients belonging to the same
        clinician.

        """

        patients = self.fetchAllPatients()

        for other_patient in patients:
            if other_patient.id != patient.id:
                #
                # Now we will do patient matches for same clinician
                # DJA 2014/05/14
                # and patient1.clinician_id != patient2.clinician_id:
                #
                self.matchPatientToPatient(patient, other_patient, force)
                self.matchPatientToPatient(other_patient, patient, force)

    def matchAllPatients(self, force):
        """
        Compute matches of all patients to all other patients in the
        GeneYenta DB and update the database accordingly.

        """

        patients = self.fetchAllPatients()

        match_count = 0
        match_startdate = datetime.now()
        for patient1 in patients:
            for patient2 in patients:
                if patient1.id < patient2.id:
                    #
                    # Compute two-way patient to patient match below.
                    # Skip iterations where patient1.id > patient2.id.
                    # Don't match a patient to his/herself.
                    #
                    # Now we will do patient matches for same clinician
                    # DJA 2014/05/14
                    # and patient1.clinician_id != patient2.clinician_id:
                    #

                    if match_count % 100 == 0:
                        elapsed_time = datetime.now() - match_startdate
                        print "match operations = {1}\telapsed time = {0}".format(elapsed_time, match_count)

                    self.matchPatientToPatient(patient1, patient2, force)
                    self.matchPatientToPatient(patient2, patient1, force)

                    match_count += 1

    def notifyMatchProcessTimedOut(self):
        msg = "A GeneYenta matching process timed out waiting for a previous matching process to complete at {0}\n".format(datetime.now())

        print msg

        mime_msg = MIMEText(raw_msg)

        mime_msg['Subject'] = 'GeneYenta matching process failed'
        mime_msg['From'] = ADMIN_EMAIL
        mime_msg['To'] = ADMIN_EMAIL
        s = smtplib.SMTP('localhost')
        s.sendmail(ADMIN_EMAIL, [ADMIN_EMAIL], mime_msg.as_string())
        s.quit()


def main():
    """
    Parse arguments. If a patient ID is given, match this patient to all other
    patients in the GeneYenta DB, otherwise match all patients to all other
    patients.

    """

    logging.info("matching process started at {0}".format(datetime.now()))

    parser = argparse.ArgumentParser(
        description = 'Match patient phenotypes in the GeneYenta DB. If a patient ID is provided, match that patient to all other patients, otherwise match all patients to all other patients.'
    )

    parser.add_argument('-id', '--patient_id', nargs='?', const=0, default=0)
    parser.add_argument('-id2', '--patient_id2', nargs='?', const=0, default=0)
    parser.add_argument('-f', '--force', action='store_true')
    args = parser.parse_args()
    patient_id = args.patient_id
    patient_id2 = args.patient_id2
    force_match = args.force

    m = GYMatcher()
    
    process_attempts = 0
    existing_process = m.isMatchProcessing()
    while existing_process and process_attempts < PROCESS_RETRIES:
        process_attempts += 1
        time.sleep(PROCESS_WAIT_TIME)
        existing_process = m.isMatchProcessing()

    if existing_process:
            logging.error(
                "matching process timed out waiting for a previous matching " \
                "process to complete at {0}".format(datetime.now()))
            m.notifyMatchProcessTimedOut()
    else:
        m.setMatchProcessStarted()

        if patient_id:
            patient = m.fetchPatient(patient_id)
            if patient_id2:
                patient2 = m.fetchPatient(patient_id2)
                m.matchPatientToPatient(patient, patient2, force_match)
            else:
                m.matchPatientToAll(patient, force_match)
        else:
            m.matchAllPatients(force_match)

        m.setMatchProcessFinished()

        logging.info("matching process completed at {0}".format(datetime.now()))


if __name__ == "__main__":
    main()
