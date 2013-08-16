#!/usr/bin/env python2.7
"""
match.py

GeneYenta patient matching.

Written by: Mike Gottlieb (gottlieb@psych.ubc.ca)
Modified by: David Arenillas (dave@cmmt.ubc.ca)


TO DO
-----
- Add ability to match a single patient to all others instead of just matching
  all patients to all others.
  - Add ability to pass in a patient ID as a command line argument.
- Refactor code so that all DB access is performed through the GYMatcher class
  rather than through the individual Match, Patient classes etc.
- Rewrite SQL statements with proper Python format strings
- Determine best way to do date comparisons (in Python or SQL)?
- Are dates stored in UTC? If so we have to be careful calling now() funtion
  in SQL statements to set date to current.
- Updating/inserting date fields in SQL statements?
  - Have to add extra date fields to matches_match and cases_patient tables.
- Change Camel case to underscore?
- Re-implement using the GeneYenta Django class models rather than
  re-implementing the classes here and performing low level SQL routines???
  - It would be more consistent and may be easier to maintain by doing this,
    but this is debatable
  - It may be less efficient to doing it that way. We have more precise control
    over accessing the SQL and writing efficient queries.

"""
import math
import argparse
import MySQLdb
from datetime import tzinfo, timedelta, datetime

# Maybe these should be passed in as command line arguments
GY_DB_HOST = 'localhost'
GY_DB_USER = 'gyadmin'
GY_DB_PASS = 'gnytdmpw'
GY_DB_NAME = 'GeneYenta'

NO_MATCH = -1

class Match:
    def __init__(
        self, id, patient1_id, patient2_id, score12, score21, match_date
    ):
        self.id = id
        self.patient1_id = patient1_id
        self.patient2_id = patient2_id
        self.score12 = score12
        self.score21 = score21
        self.match_date = match_date

    def __str__(self):
        return "patien1 = {0:d} patient2 = {1:d} score12 = {2} " \
               "score21 = {3} date = {4}".format(
            self.patient1_id, self.patient2_id, str(self.score12),
            str(self.score21), self.match_date.strftime("%Y-%m-%d %H:%M:%S")
        )


class Patient:
    def __init__(self, id, last_modified):
        self.id = id
        self.last_modified = last_modified
        terms = None
        all_terms = None


class PhenoTerm:
    def __init__(self, id, score, weight):
        self.id = id
        self.score = score      # HPO term score
        self.weight = weight    # physician assigned relevancy score
        self.ancestors = None


class GYMatcher:
    def __init()__:
        db = MySQLdb.connect(
            host    = GY_DB_HOST,
            user    = GY_DB_USER,
            passwd  = GY_DB_PASS,
            db      = GY_DB_NAME
        )

        self.db = db

        self.new_matches = []
        self.updated_matches = []

    def fetchPatient(self, patient_id):
        sql = "SELECT id, last_modified FROM cases_patient " \
              "where id = {0:d}".format(patient_id)
        cur = self.db.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        dt = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
        patient = Patient(row[0], dt)

        return patient

    def fetchAllPatients(self):
        sql = "SELECT id, last_modified FROM cases_patient"
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

        patients = []
        for row in rows:
            dt = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
            patients.append(Patient(row[0], dt))

        return patients

    def generatePatientPhenoTermSet(self, patient):
        all_terms = []
        if not patient.terms:
            patient.terms = self.fetchPatientPhenoTerms(patient)
        for term in patient.terms:
            if term not in all_terms:
                all_terms.append(term)

            if not term.ancestor_terms:
                term.ancestor_terms = self.fetchPhenoTermAncestors(term)

            for ancestor_term in term.ancestor_terms:
                if ancestor_term not in all_terms:
                    all_terms.append(ancestor_term)

        return all_terms

    def fetchPatientPhenoTerms(self, patient):
        sql = "SELECT cp.hpo_id, ht.score, cp.relevancy_score " \
              "FROM cases_phenotype cp, hpo_term ht" \
              "WHERE cp.hpo_id = ht.id and cp.patient_id = {0:d}".format(
            patient.id
        )
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

        terms = []
        for row in rows:
            term = PhenoTerm(row[0], row[1], row[2])
            terms.append(term)

        return terms

    def fetchPhenoTermAncestors(self, term):
        sql = "SELECT ancestor_id, ancestor_score FROM hpo_ancestor " \
              "WHERE id = '{0}' order by ancestor_score desc".format(
            str(self.id)
        )
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

        ancestors = []
        for row in rows:
            ancestors.append(PhenoTerm(row[0], row[1], self.score))

        return ancestors

    def findBestPhenoTermMatchScore(self, term, term_list):
        best_score = NO_MATCH
        for t in term_list:
            if t.id == term.id:
                best_score = t.score
                break

        return best_score

    def findBestPhenoTermAncestorMatchScore(self, term, term_list):
        if not term.ancestors:
            term.ancestors = self.fetchPhenoTermAncestors(term):

        best_score = NO_MATCH
        for ancestor_term in term.ancestors:
            match_score =  self.findBestPhenoTermMatchScore(
                ancestor_term, term_list
            )
            if match_score > best_score:
                best_score = match_score

        return best_score

    def fetchMatch(self, patient1, patient2):
        id1 = patient1.id
        id2 = patient2.id

        # make sure patient ID 1 is less than patient ID 2
        if (id2 < id1):
            tmp = id1
            id1 = id2
            id2 = tmp

        sql = "SELECT id, patient1_id, patient2_id, score12, score21, " \
              "date_matched FROM matches_match where patient1_id = {0:d} " \
              "and patient2_id = {1:d}".format(id1, id2)
        cur = self.db.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        match = None
        if row:
            print row
            dt = datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")
            match = Match(row[0], row[1], row[2], row[3], row[4], dt)

        return match

    def fetchAllMatches(self):
        matches = []
        sql = "SELECT id, patient1_id, patient2_id, score12, score21, " \
              "date_matched FROM matches_match"
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            print row
            dt = datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")
            matches.append(Match(row[0], row[1], row[2], row[3], row[4], dt))

        return matches

    def insertMatch(self, match):
        # Should we use now() or the Python datetime to format dates (are the
        # dates stored in UTC or local)?
        sql = "INSERT INTO cases_match " \
              "(patient1_id, patient2_id, score12, score21, date_matched) " \
              "VALUES ({0:d}, {1:d}, {2}, {3}, {4})".format(
            match.patient1_id,
            match.patient2_id,
            str(match.score12),
            str(match.score21),
            match.match_date.strftime("%Y-%m-%d %H:%M:%S")
        )
        cur = self.db.cursor()
        cur.execute(sql)

    def updateMatch(self, match):
        sql = "UPDATE cases_match SET score12 = {0}, score21 = {1}, " \
              "match_date = '{2}' WHERE id = {3:d}".format(
            str(match.score12),
            str(match.score21),
            match.match_date.strftime("%Y-%m-%d %H:%M:%S"),
            match.id
        )
        cur = self.db.cursor()
        cur.execute(sql)
        
    def getPatientMatchPercent(self, patient1, patient2):
        if not patient1.terms:
            patient1.terms = self.fetchPatientPhenoTerms(patient1)

        if not patient2.all_terms:
            patient2.all_terms = self.generatePatientPhenoTermSet(patient2)

        matchNumerator = 0
        matchDenominator = 0
        for p1_term in patient1.terms:
            matchDenominator += (p1_term.score * p1_term.weight)
            bestScore = self.findBestPhenoTermMatchScore(
                p1_term, patient2.all_terms
            )
            if bestScore == NO_MATCH:
                bestScore = self.findBestPhenoTermAncestorMatchScore(
                    p1_term, patient2.all_terms
                )
            matchNumerator += (bestScore * patient1_term.weight)

        match_score = 0
        if matchDenominator > 0:
            match_score = matchNumerator / matchDenominator

        return match_score

    def matchAll(self):
        patients = self.fetchAllPatients()

        for patient1 in patients:
            for patient2 in patients:
                if patient1.id >= patient2.id:
                    print "skipping match of " + str(patient1.id) + " and " + str(patient2.id)
                    continue 

                existing_match = self.fetchMatch(patient1, patient2)

                is_up_to_date_match = None
                if existing_match:
                    is_up_to_date_match = self.upToDateMatch(
                        existing_match, patient1, patient2
                    )

                newMatch = None
                if not existing_match or not is_up_to_date_match:
                    score12 = self.getPatientMatchPercent(parient1, patient2)
                    score21 = self.getPatientMatchPercent(patient2, patient1)
                    newMatch = Match(
                        patient1.id, patient2.id, score12,
                        score21, datetime.utcnow()
                    )

                if newMatch:
                    if existing_match:
                        print "updating match of " + str(patient1.id) + " and " + str(patient2.id)
                        self.updateMatch(newMatch)
                        self.updated_matches.append(newMatch)
                    else:
                        print "writing match of " + str(patient1.id) + " and " + str(patient2.id)
                        self.insertMatch(newMatch)
                        self.new_matches.append(newMatch)
        #db.commit()

    def alreadyMatched(self, patient1, patient2):
        for match in self.matches:
            if (match.patient1_id == patient1.id and match.patient2_id == patient2.id) or  (match.patient2_id == patient1.id and match.patient1_id == patient2.id):
                return True
        return False

    def upToDateMatch(self, match, patient1, patient2):
        if match.match_date >= patient1.last_modified
            and match.match_date >= patient2.last_modified:
                return True
        else:
            return False

def main():
    parser = argparse.ArgumentParser(
        description = 'Match patient phenotypes in the GeneYenta DB. If a patient ID is provided, match that patient to all other patients, otherwise match all patients to all other patients.'
    )

    parser.add_argument('-id', '--patient_id', nargs='?', const=0, default=0)
    args = parser.parse_args()
    patient_id = args.patient_id

    m = GYMatcher()

    if patient_id:
        patient = m.fetchPatient(patient_id)
        m.matchPatient(patient)
    else:
        m.matchAll()

if __name__ == "__main__":
    main()
