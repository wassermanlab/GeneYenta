import math
import MySQLdb

NO_MATCH = -1
threshold = .75
db=MySQLdb.connect(host="localhost",user="gyadmin",passwd="gnytdmpw",db="GeneYenta")
cur = db.cursor()

class Service:
	def __init__(self):
		self.cases = self.getCases()
		self.matches = self.getMatches()

	def getMatches(self):
		matches = []
		sql = "SELECT * FROM cases_match"
		cur.execute(sql)
		rows = cur.fetchall()
		print rows
		for row in rows:
			matches.append(Match(row[1],row[2],row[3],row[4]))
		return matches

	def getCases(self):
		cases = []
		sql = "SELECT id FROM cases_patient"
		cur.execute(sql)
		rows= cur.fetchall()
		for row in rows:
			cases.append(Case(row[0]))
		return cases

	def matchAll(self):
		for caseA in self.cases:
			for caseB in self.cases:
				if (caseA.id == caseB.id or self.alreadyMatched(caseA, caseB)):
					print "match already exists"
					continue
				ABScore = caseA.getMatchPercent(caseB)
				BAScore = caseB.getMatchPercent(caseA)
				newMatch = Match(caseA, caseB, ABScore, BAScore)
				self.matches.append(newMatch)
				newMatch.writeToDB()
				print "matchWritten"

	def alreadyMatched(self, caseA, caseB):
		for match in self.matches:
			if (match.caseAID == caseA.id and match.caseBID == caseB.id) or  (match.caseBID == caseA.id and match.caseAID == caseB.id):
				return True
		return False

class Match:
	def __init__(self, caseAID, caseBID, ABScore, BAScore):
		self.caseAID = caseAID
		self.caseBID = caseBID
		self.ABScore = ABScore
		self.BAScore = BAScore

	def writeToDB(self):
		sql = "INSERT INTO cases_match (patient1_id, patient2_id, score12, score21) VALUES (" +  str(self.caseA.id) +", "+ str(self.caseB.id) +", "+ str(self.ABScore) +", "+ str(self.BAScore) +  ")"
		cur.execute(sql)

class Case:
	def __init__(self, id):
		self.id = id
		self.terms = self.getTerms()

	def getTerms(self):
		terms = []
		termSQL = "SELECT hpo_id, relevancy_score FROM cases_phenotype where patient_id = "+ str(self.id)
		cur.execute(termSQL)
		termRows= cur.fetchall()
		for tRow in termRows:
			term = PhenoTerm(tRow[0], tRow[1])
			terms.append(term)
		return terms
		
	def getMatchPercent(self, case):
		return self.matchSelectedTermsToCase(case.generateTermSet())

	def matchSelectedTermsToCase(self, termList):
		matchNumerator = 0
		matchDenominator = 0
		for selectedTerm in self.terms:
			matchDenominator+= (selectedTerm.score * selectedTerm.weight)
			bestScore = selectedTerm.findBestMatch(termList)
			if bestScore == NO_MATCH:
				bestScore = selectedTerm.matchAncestorsToCase(termList)
			matchNumerator += (bestScore * selectedTerm.weight)
		return matchNumerator/matchDenominator

	def generateTermSet(self):
		allTerms = []
		for term in self.terms:
			if (term not in allTerms):
				allTerms.append(term)
			for parent in term.getAllParents():
				if (parent not in allTerms):
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

	def matchAncestorsToCase(self, termList):
		bestScore = NO_MATCH
		for parent in self.getAllParents():
			matchScore =  parent.findBestMatch(termList)
			if matchScore > bestScore:
				bestScore = matchScore
		return bestScore

def main():
	s = Service()
	print "Case info"
	for c in s.cases:
		print c.id
		for t in c.terms:
			print t.id
	print ""
	print "trying to match"
	s.matchAll()
	print ""
	print "All matched tuples:"
	for m in s.matches:
		print str(m.caseAID) +" " + str(m.caseBID)

if __name__ == "__main__":
	main()
