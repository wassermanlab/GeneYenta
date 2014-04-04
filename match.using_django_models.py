import sys
import os
import math
import MySQLdb
import argparse

sys.path.append('/apps/GeneYenta')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geneyenta.settings")

from patients.models import Patient, Match

NO_MATCH = -1
threshold = .75

db=MySQLdb.connect(host="localhost",user="gyadmin",passwd="gnytdmpw",db="GeneYenta")
cur = db.cursor()

def matchPatientToAll(patient1):
    hpoTerms = fetchHPOTerms()
    patients = Patient.objects.all()

    for patient2 in patients:
        if patient2.id == patient1.id:
            print "skipping self-match of " + patient1.id
            continue 

        score12 = getMatchPercent(hpoTerms, patient1, patient2)
        score21 = getMatchPercent(hpoTerms, patient2, patient1)

        newMatch = Match(patientA.id, patientB.id, ABScore, BAScore)

        if self.alreadyMatched(patientA, patientB):
            print "updating match of " + str(patientA.id) + " and " + str(patientB.id)
            newMatch.updateDB()
            continue

        ABScore = patientA.getMatchPercent(patientB)
        BAScore = patientB.getMatchPercent(patientA)
        newMatch = Match(patientA.id, patientB.id, ABScore, BAScore)
        self.matches.append(newMatch)
        newMatch.writeToDB()
        print "writing match of " + str(patientA.id) + " and " + str(patientB.id)

    db.commit()


def alreadyMatched(self, patientA, patientB):
    for match in self.matches:
        if (match.patientAID == patientA.id and match.patientBID == patientB.id) or  (match.patientBID == patientA.id and match.patientAID == patientB.id):
            return True
    return False

def fetchHPOTerms():
    sql = "SELECT hpo_id, relevancy_score FROM patients_phenotype"

    cur.execute(sql)
    rows = cur.fetchall()

    terms = {}
    for row in rows:
        terms[row[0]] = row[1]

    return terms

class Match:
    def __init__(self, patientAID, patientBID, ABScore, BAScore):
        self.patientAID = patientAID
        self.patientBID = patientBID
        self.ABScore = ABScore
        self.BAScore = BAScore

    def writeToDB(self):
        sql = "INSERT INTO patients_match (patient1_id, patient2_id, score12, score21) VALUES (" +  str(self.patientAID) +", "+ str(self.patientBID) +", "+ str(self.ABScore) +", "+ str(self.BAScore) +  ")"
        cur.execute(sql)

    def updateDB(self):
        sql = "update patients_match set score12 = " + str(self.ABScore) + ", score21 = " + str(self.BAScore) + " where patient1_id = " + str(self.patientAID) + " and patient2_id = " + str(self.patientBID) 
        cur.execute(sql)
    
def getMatchPercent(hpoTerms, patient1, patient2):
    return matchSelectedTermsToPatient(
        hpoTerms, patient1, generateTermSet(patient2)
    )

def matchSelectedTermsToPatient(hpoTerms, patient, termList):
    matchNumerator = 0
    matchDenominator = 0
    for selectedTerm in patient.phenotype_set.all():
        matchDenominator += (selectedTerm.relevancy_score * hpoTerms[selectedTerm.hpo_id])
        bestScore = selectedTerm.findBestMatch(termList)
        if bestScore == NO_MATCH:
            bestScore = selectedTerm.matchAncestorsToPatient(termList)
        matchNumerator += (bestScore * selectedTerm.relevancy_score)
    return matchNumerator/matchDenominator

class Patient:
    def __init__(self, id):
        self.id = id
        self.terms = self.getTerms()

    def getTerms(self):
        terms = []
        termSQL = "SELECT hpo_id, relevancy_score FROM patients_phenotype where patient_id = "+ str(self.id)
        cur.execute(termSQL)
        termRows= cur.fetchall()
        for tRow in termRows:
            term = PhenoTerm(tRow[0], tRow[1])
            terms.append(term)
        return terms

    def generateTermSet(self):
        allTerms = []
        for term in self.terms:
            if term not in allTerms:
                allTerms.append(term)
            for parent in term.getAllParents():
                if parent not in allTerms:
                    allTerms.append(parent)
        return allTerms

class PhenoTerm:
    def __init__(self, id, weight):
        self.id = id
        self.score = self.getScore()
        self.weight = weight

    def getScore(self):
        sql = "SELECT score FROM hpo_term where id = " + "\""+ self.id + "\""
        cur.execute(sql)
        row = cur.fetchone()
        return row[0]

    def getAllParents(self):
        allParents = []
        sql = "SELECT parent_id FROM hpo_lineage where id = " + "\""+ self.id + "\""
        cur.execute(sql)
        rows= cur.fetchall()
        for row in rows:
            allParents.append(PhenoTerm(row[0], self.score))
        return allParents

    def findBestMatch(self, termList):
        bestScore = NO_MATCH
        for t in termList:
            if t.id == self.id:
                if self.score > bestScore:
                    bestScore = t.score
        return bestScore

    def matchAncestorsToPatient(self, termList):
        bestScore = NO_MATCH
        for parent in self.getAllParents():
            matchScore =  parent.findBestMatch(termList)
            if matchScore > bestScore:
                bestScore = matchScore
        return bestScore

def main():
    parser = argparse.ArgumentParser(
        description = 'Match a patient to all other patients in the GeneYenta DB'
    )

    parser.add_argument('-id', '--patient_id', nargs='?')

    args = parser.parse_args()

    patient_id = args.patient_id

    patient = Patient.objects.get(pk=patient_id)

    terms = patient.phenotype_set.all()

    print "Patient info"
    print patient.id
        for t in terms:
            print t.id
    print ""
    print "trying to match"
    matches = matchPatientToAll(patient)
    print ""
    print "All matched pairs:"
    for m in matches:
        print str(m.patientAID) +" " + str(m.patientBID) + " 12Score = " + str(m.ABScore) + " 21Score = "+str(m.BAScore)

if __name__ == "__main__":
    main()
