import sys
sys.path.insert(0,'../') # moves directory back one for testing
from betting_odds_scraper import *
""" Testing File for betting_odds_scraper.py """

def testIncrementDate():
	date1 = betting_odds_scraper.incrementDate("20110409")
	if date1 != "20110410":
		return 0
	date2 = betting_odds_scraper.incrementDate("20111231")
	if date2 != "20120101":
		return 0
	date3 = betting_odds_scraper.incrementDate("20110630")
	if date3 != "20110701":
		return 0
	date4 = betting_odds_scraper.incrementDate("20110701")
	if date4 != "20110702":
		return 0
	print "passed IncrementDate"
	return 1

def testIsDuplicate():
	l = [1,3,1]
	if not betting_odds_scraper.isDuplicate(l,1):
		return 0
	if betting_odds_scraper.isDuplicate(l,3):
		return 0
	print "passed IsDuplicate"
	return 1

def testEstimateUnderdogOdds():
	underdogOdds = betting_odds_scraper.estimateUnderdogOdds("-145")
	if underdogOdds == 135:
		print "passed underdogOdds"
		return 1
	else:
		return 0


def main():
	print "Starting Tests"

	correct = 0
	totalTests = 3

	correct += testIncrementDate()
	correct += testIsDuplicate()
	correct += testEstimateUnderdogOdds()

	print "Passed " + str(correct) + " out of " + str(totalTests) + " tests."

# start script with a call to main
main()