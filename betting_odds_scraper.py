''' 
This scrapes betting data from donbest and stores it in 
MySQL database for later use.  The data records the teams,
the line for each team, and the over under for the game 
''' 
# TODOS:
# - make sure team abbreviations are compatible with current ones in DB
# - get git set up for this and poker project

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
				teamNames.append(teamName)
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
				teamNames.append(teamName)
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

	 # convert team names correctly

	 # concatenate team name with date, add 0, check for double header

	 # get the favored odds, calculate underdog odds using helper function

	 # get the over under

	 # get the over/under odds, calculate the other odds, should just be odds *-1 -10








# starts the script
getData(URL+STARTDATE2011,STARTDATE2011)
