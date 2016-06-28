import sys
sys.path.insert(0,'../') # moves directory back one for testing
from scraper538 import *
""" Testing File for scraper538.py """

def testcreateGameID():
	id1 = createGameID("Mon Apr 6","mariners")
	if id1 != "SEA20160406":
		print id1
		return 0
	id2 = createGameID("Mon May 31","red-sox")
	if id2 != "BOS20160531":
		print id2
		return 0
	id3 = createGameID("Mon Jun 6","cubs")
	if id3 != "CHN20160606":
		print id3
		return 0
	id4 = createGameID("Mon Jul 10","nationals")
	if id4 != "WAS20160710":
		print id4
		return 0
	id5 = createGameID("Mon Aug 1","blue-jays")
	if id5 != "TOR20160801":
		print id5
		return 0
	print "createGameID passed"
	return 1

def main():
	print "Starting Tests"

	correct = 0
	totalTests = 1

	correct += testcreateGameID()

	print "Passed " + str(correct) + " out of " + str(totalTests) + " tests."

# start script with a call to main
main()