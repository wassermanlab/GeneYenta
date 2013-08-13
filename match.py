import math
import argparse
import MySQLdb

# Maybe these should be passed in as command line arguments
GY_DB_HOST = 'localhost'
GY_DB_USER = 'gyadmin'
GY_DB_PASS = 'gnytdmpw'
GY_DB_NAME = 'GeneYenta'

NO_MATCH = -1

class Match:
    def __init__(self, patient1_id, patient2_id, score12, score21):
        self.patient1_id = patient1_id
        self.patient2_id = patient2_id
        self.score12 = score12
        self.score21 = score21

class Patient:
    def __init__(self, id):
        self.id = id
        self.terms = self.getTerms()

    def getTerms(self, db):
        terms = []
        termSQL = "SELECT hpo_id, relevancy_score FROM cases_phenotype where patient_id = "+ str(self.id)
        cur = db.cursor()
        cur.execute(termSQL)
        termRows= cur.fetchall()
        for tRow in termRows:
            term = PhenoTerm(tRow[0], tRow[1])
            terms.append(term)
        return terms
        
    def getMatchPercent(self, patient):
        return self.matchSelectedTermsToPatient(patient.generateTermSet())

    def matchSelectedTermsToPatient(self, termList):
        matchNumerator = 0
        matchDenominator = 0
        for selectedTerm in self.terms:
            matchDenominator+= (selectedTerm.score * selectedTerm.weight)
            bestScore = selectedTerm.findBestMatch(termList)
            if bestScore == NO_MATCH:
                bestScore = selectedTerm.matchAncestorsToPatient(termList)
            matchNumerator += (bestScore * selectedTerm.weight)
        return matchNumerator/matchDenominator

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

class GYMatcher:
    def __init()__:
        db = MySQLdb.connect(
            host    = GY_DB_HOST,
            user    = GY_DB_USER,
            passwd  = GY_DB_PASS,
            db      = GY_DB_NAME
        )

        self.db = db

    def getMatches(self):
        matches = []
        sql = "SELECT * FROM cases_match"
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        print rows
        for row in rows:
            matches.append(Match(row[1],row[2],row[3],row[4]))
        return matches

    def getPatients(self):
        patients = []
        sql = "SELECT id FROM cases_patient"
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            patients.append(Patient(row[0]))
        return patients

    def DBInsertMatch(db, match):
        sql = "INSERT INTO cases_match (patient1_id, patient2_id, score12, score21) VALUES (" +  str(match.patient1_id) +", "+ str(match.patient2_id) +", "+ str(match.score12) +", "+ str(match.score21) +  ")"
        cur = db.cursor()
        cur.execute(sql)

    def DBUpdateMatch(db, match):
        sql = "update cases_match set score12 = " + str(match.score12) + ", score21 = " + str(match.score21) + " where patient1_id = " + str(match.patient1_id) + " and patient2_id = " + str(match.patient2_id) 
        cur = db.cursor()
        cur.execute(sql)

    def matchAll(self):
        patients = getPatients()

        for patient1 in patients:
            for patient2 in patients:
                if patient1.id >= patient2.id:
                    print "skipping match of " + str(patient1.id) + " and " + str(patient2.id)
                    continue 

                score12 = patient1.getMatchPercent(patient2)
                score21 = patient2.getMatchPercent(patient1)
                newMatch = Match(patient1.id, patient2.id, score12, score21)

                if self.alreadyMatched(patient1, patient2):
                    print "updating match of " + str(patient1.id) + " and " + str(patient2.id)
                    DBUpdateMatch(db, newMatch)
                else
                    print "writing match of " + str(patient1.id) + " and " + str(patient2.id)
                    DBInsertMatch(db, newMatch)
        #db.commit()

    def alreadyMatched(self, patient1, patient2):
        for match in self.matches:
            if (match.patient1_id == patient1.id and match.patient2_id == patient2.id) or  (match.patient2_id == patient1.id and match.patient1_id == patient2.id):
                return True
        return False

def main():
    parser = argparse.ArgumentParser(
        description = 'Match patient phenotypes in the GeneYenta DB. If a patient ID is provided, match that patient to all other patients, otherwise match all patients to all other patients.'
    )

    parser.add_argument('-id', '--patient_id', nargs='?', const=0, default=0)
    args = parser.parse_args()
    patient_id = args.patient_id

    if patient_id:
        matchPatient(db, patient_id)
    else:
        matchAll(db)

if __name__ == "__main__":
    main()
