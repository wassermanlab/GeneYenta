import math
import MySQLdb

threshold = .75
db=MySQLdb.connect(host="localhost",user="gyadmin",passwd="gnytdmpw",db="GeneYenta")
cur = db.cursor()

class Service:
	_instance = None
	def __init__(self):
		if _instance != None:
			return _instance
		self.cases = self.getCases()
		self.matches = self.getMatches()
		_instance = self
		
	def getMatches(self):
		matches = []
		sql = "SELECT * FROM matches"
		cur.execute(sql)
		row = cur.fetchall()
		for row in rows
			matches.append(Match(row[1],row[0],row[2],row[3]))
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
				if caseA == caseB or alreadyMatched(caseA, caseB):
					continue
				ABScore = caseA.getMatchPercent(caseB)
				BAScore = caseB.getMatchPercent(caseA)
				newMatch = Match(caseA, caseB, ABScore, BAScore)
				matches.append(newMatch)
				newMatch.writeToDB()

	def alreadyMatched(self, caseA, caseB):
		for match in self.matches:
			if (match.caseA == caseA and match.caseB == caseB) or  (match.caseB == caseA and match.caseA == caseB):
				return True
		return False

class Match:
	def _init_(self, caseA, caseB, ABScore, BAScore):
		self.caseA = caseA
		self.caseB = caseB
		self.ABScore = ABScore
		self.BAScore = BAScore
	
	def writeToDB(self, caseA, caseB, ABScore, BAScore):
		sql = "INSERT INTO matches (CaseA, CaseB, ABScore, BAScore) VALUES (" + caseA +", "+ caseB +", "+ ABScore +", "+ BAScore +  ")"
		cur.execute(sql)

class Case:
	def __init__(self, id, terms):
		self.id = id
		self.terms = self.getTerms()

	def getTerms(self):
		terms = []
		termSQL = "SELECT hpo_id, relevancy_score FROM cases_phenotype where patient_id = "+ self.id
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
			if bestScore == -1:
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
		bestScore = -1
		for t in termList:
			if t.id == self.id:
				if self.score > bestScore:
					bestScore = t.score
		return bestScore

	def matchAncestorsToCase(self, termList):
		bestScore = -1
		for parent in self.getAllParents():
			matchScore =  parent.findBestMatch(termList)
			if matchScore > bestScore:
				bestScore = matchScore
		return bestScore

def main():
	term = PhenoTerm("HP_0007010", 1) 
	print "Case x from y's perspective:"
	print y.getMatchPercent(x)
	print "Case y from x's perspective:"
	print x.getMatchPercent(y)
	print "Their mutual match average:"
	print (x.getMatchPercent(y) + y.getMatchPercent(x))/2
	print "Their mutual match sqr root:"
	print math.sqrt(x.getMatchPercent(y) * y.getMatchPercent(x))

if __name__ == "__main__":
	main()
