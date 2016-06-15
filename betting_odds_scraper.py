''' 
This scrapes betting data from donbest and stores it in 
MySQL database for later use.  The data records the teams,
the line for each team, and the over under for the game 
''' 
# TODOS:
# - get git set up for poker project
# - test helpers and main script
# - insert into DB

import game
import unicodedata
import requests
import bs4
from bs4 import BeautifulSoup

# CONSTANTS
STARTDATE2011 = "20110331"
STARTDATE2012 = "20120328"
STARTDATE2013 = "20130331"
STARTDATE2014 = "20140322"
STARTDATE2015 = "20150405"
STARTDATE2016 = "20160403"
URL = "http://feeds.donbest.com/ScoresWebApplication/servicePage.jsp?type=SCHED&leagueId=5&schedDate="

# helper functions
'''
increments the date to put in the url by one day
returns the next day as a string in the same format as the input
@param - date: the date to increment, in format 'yyyymmdd'
'''
def incrementDate(date):
	year = int(date[0:4])
	month = int(date[4:6])
	day = int(date[6:8])
	if month == 1 and day == 31:
		month = "02"
		day = "01"
	# don't worry about leap years, since it's offseason 
	elif month == 2 and day == 28:
		month = "03"
		day = "01"
	elif month == 3 and day == 31:
		month = "04"
		day = "01"
	elif month == 4 and day == 30:
		month = "05"
		day = "01"
	elif month == 5 and day == 31:
		month = "06"
		day = "01"
	elif month == 6 and day == 30:
		month = "07"
		day = "01"
	elif month == 7 and day == 31:
		month = "08"
		day = "01"
	elif month == 8 and day == 31:
		month = "09"
		day = "01"
	elif month == 9 and day == 30:
		month = "10"
		day = "01"
	elif month == 10 and day == 31:
		month = "11"
		day = "01"
	elif month == 11 and day == 30:
		month = "12"
		day = "01"
	else:
		if month == 12 and day == 31:
			month = "01"
			day = "01"
			year += 1
		else:
			day += 1
	day = str(day)
	month = str(month)
	year = str(month)
	return year + month + day 

"""
converts the team abbreviation used by the website
to the one used by the database 
@param - abbr: the string to change if neccessary
returns the converted abbreviation as a string
"""
def convertAbbr(abbr):
	s = abbr
	if "SDG" in abbr:
		s = "SDN"
	if "STL" in abbr:
		s = "SLN"
	if "SFO" in abbr:
		s = "SFN"
	if "LOS" in abbr:
		s = "LAN"
	if "NYY" in abbr:
		s = "NYA"
	if "LAA" in abbr:
		s = "ANA"
	if "KAN" in abbr:
		s = "KCA"
	if "CUB" in abbr:
		s = "CHN"
	if "NYM" in abbr:
		s = "NYN"
	if "MIA" in abbr:
		s = "FLO"
	if "CWS" in abbr:
		s = "CHA"
	return s

""" 
checks if an item occurs multiple times in a list
@param - l: the list
@param - item: the item to check 
returns true if the list contains the item more than once
"""
def isDuplicate(l,item):
	counter = 0
	for i in l:
		if i == item:
			counter += 1
	if counter > 1:
		return True

"""
uses the favored teams odds to estimate the away team's odds 
based on the way Bovada tends to have their odds for baseball games
i.e. -120 usually means 110 for the underdog
-155 means +140, -185 means +165, -220 might mean +190
@param - odds: the favorite's odds
returns the odds of the underdog
"""
def estimateUnderdogOdds(odds):
	if odds >= -150:
		underdogOdds = odds * -1 + 10
	elif odds >= -180:
		underdogOdds = odds * -1 + 15
	elif odds >= -195:
		underdogOdds = odds * -1 + 20
	elif odds >= -270:
		underdogOdds = odds * -1 + 30
	else:
		underdogOdds = odds * -1 + 40
# end helper functions

"""
gets the data from the specific URL page and inserts into the database
@param - url: the specific url to get the data from
@param - date: the date of the games
"""
def getData(url,date):
	request = requests.get(url)
	soup = BeautifulSoup(request.content)
	# contains the team names
	greyTeams = soup.find_all("td",{"class":"scores-greybg-team"})
	whiteTeams = soup.find_all("td",{"class":"scores-whitebg-team"})
	# contains the betting info
	greyData = soup.find_all("td",{"class":"scores-greybg"})
	whiteData = soup.find_all("td",{"class":"scores-whitebg"})

	# data for the loops

	# teamNames = [away team, home team ...]
	teamNames = []

	# bettingData = [over/under,favorite line] e.g [7o15,-115] = [7o+115,-115] could also
	# be e.g [favorite line, over/under] e.g [-140, 81/2u] - assume this means 100
	bettingData = []

	# start the loops
	counter = 0
	for td in greyTeams:
		if counter % 2 == 0:
			teamName = td.contents[0]
			if type(teamName) == bs4.element.Tag:
				teamName = teamName.contents
				if len(teamName) > 0:
					teamName = teamName[0]
			teamName = str(unicodedata.normalize('NFKD',unicode(teamName)).encode('ascii','ignore'))
			if teamName != " " and len(teamName) > 2:
				# print teamName
				teamNames.append(convertAbbr(teamName))
		counter += 1
	counter = 0
	for td in whiteTeams:
		if counter % 2 == 0:
			teamName = td.contents[0]
			if type(teamName) == bs4.element.Tag:
				teamName = teamName.contents
				if len(teamName) > 0:
					teamName = teamName[0]
			teamName = str(unicodedata.normalize('NFKD',unicode(teamName)).encode('ascii','ignore'))
			if teamName != " " and len(teamName) > 2:
				# print teamName
				teamNames.append(convertAbbr(teamName))
		counter += 1
	counter = 0
	seen = False 
	for td in greyData:
		counter += 1
		if (counter + 1) % 16 == 0:
			data = td.contents[0]
			data = str(unicodedata.normalize('NFKD',unicode(data)).encode('ascii','ignore'))
			if data != " ":
				bettingData.append(data)
	counter = 0
	seen = False 
	for td in whiteData:
		counter += 1
		if (counter + 1) % 16 == 0:
			data = td.contents[0]
			data = str(unicodedata.normalize('NFKD',unicode(data)).encode('ascii','ignore'))
			if data != " ":
				bettingData.append(data)
	for item in teamNames:
	    print item
	print "halfway"
	for item in bettingData:
	 	print item

	# concatenate team name with date, add 0, check for double header
	doubleheader = False
	duplicateCount = 0
	duplicateItem = ""
	for i in range(0,len(teamNames)):
		# pass on odd
		if i % 2 != 0:
			pass
		else:
			GAME_ID = teamName + date + "0"
			if isDuplicate(teamNames,item) and duplicateItem == item and duplicateCount % 2 == 1:
				duplicateCount += 1
				GAME_ID = teamName + date + "2"
			if isDuplicate(teamNames,item) and duplicateItem != item:
				GAME_ID = teamName + date + "1"
				doubleheader = True
				duplicateCount += 1
				duplicateItem = item
			
	# get the favored odds, calculate underdog odds using helper function
	games = []
	for i in range(0,len(bettingData)):
		item = bettingData[i]
		if item[0] == "-":
			# if item is away team and favored
			if i % 2 == 0:
				awayOdds = item
				# use function to get home team odds
				homeOdds = estimateUnderdogOdds(awayOdds)
			# if item is home team and favored
			else:
				homeOdds = item
				awayOdds = estimateUnderdogOdds(homeOdds)
		# item is over/under line
		else:
			if "u" in item:
				u = item.find("u")
				runs = item[:u]
				odds = int(item[u+1])
				if "12" in runs:
					overUnder = float(runs[0]) + 0.5
				else:
					overUnder = float(runs[0])
				# odds come as something like 15, so add 100
				underOdds = odds + 100
				# odds here are always positiv, so * -1 and subtract -10
				overOdds = underOdds * -1 - 10
			elif "o" in item:
				o = item.find("o")
				runs = item[:o]
				odds = int(item[o+1])
				if "12" in runs:
					overUnder = float(runs[0]) + 0.5
				else:
					overUnder = float(runs[0])
				# odds come as something like 15, so add 100
				overOdds = odds + 100
				# odds here are always positiv, so * -1 and subtract -10
				underOdds = overOdds * -1 - 10
			# means that over/under even odds, assume this means -105, -105
			else:
				if "12" in item:
					overUnder = float(item[0]) + 0.5
				else:
					overUnder = float(item[0])
				overOdds = -105
				underOdds = -105
		# create the game Object and add to list
		game = Game(GAME_ID,homeOdds,awayOdds,overUnder,overOdds,underOdds)
		games.append(game)
	# insert into database






# starts the script
getData(URL+STARTDATE2011,STARTDATE2011)
