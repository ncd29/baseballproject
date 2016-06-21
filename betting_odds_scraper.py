''' 
This scrapes betting data from donbest and stores it in 
MySQL database for later use.  The data records the teams,
the line for each team, and the over under for the game 
''' 
# TODOS:
# - insert into DB
# - put DB connection in config and gitignore it for this and poker project
# - fix over under Bug

# BETTING DATA DONE LOADING FOR YEARS 2011 - 2013

import mysql.connector
import unicodedata
import requests
import bs4
from bs4 import BeautifulSoup

# CONSTANTS - fix the dates after done for reuse
STARTDATE2011 = "20110331" #intial val = "20110331" overwritten due to errors (restarts)
ENDDATE2011 = "20111028"
STARTDATE2012 = "20120423" #skips a few games, and a few MIA games
ENDDATE2012 = "20121028"
STARTDATE2013 = "20130603"
ENDDATE2013 = "20131030"
STARTDATE2014 = "20140322"
STARTDATE2015 = "20150405"
STARTDATE2016 = "20160403"
URL = "http://feeds.donbest.com/ScoresWebApplication/servicePage.jsp?type=SCHED&leagueId=5&schedDate="
DB = mysql.connector.connect(user='root',password='root',host='localhost',database='Baseball',
    unix_socket="/Applications/MAMP/tmp/mysql/mysql.sock")

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
	if day < 10:
		day = "0" + str(day)
	else:
		day = str(day)
	if month < 10:
		month = "0" + str(month)
	else:
		month = str(month)
	year = str(year)
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
	# leave commented out for years greater than 2011, FLO switched to MIA in 2012
	# if "MIA" in abbr:
	# 	s = "FLO"
	if "CWS" in abbr:
		s = "CHA"
	if "TAM" in abbr:
		s = "TBA"
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
	odds = int(odds)
	if odds >= -145:
		underdogOdds = odds * -1 - 10
	elif odds >= -180:
		underdogOdds = odds * -1 - 15
	elif odds >= -195:
		underdogOdds = odds * -1 - 20
	elif odds >= -265:
		underdogOdds = odds * -1 - 30
	else:
		underdogOdds = odds * -1 - 40
	return underdogOdds
# end helper functions

"""
gets the data from the specific URL page and inserts into the database
@param - url: the specific url to get the data from
@param - date: the date of the games
@param - noError: condition that signifies whether 
"""
def getData(url,date):
	print date
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
			# print "greyTeam = " + teamName
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
			# print "whiteTeam = " + teamName
		counter += 1
	counter = 0
	seen = False 
	for td in greyData:
		counter += 1
		try:
			if (counter + 1) % 16 == 0:
				data = td.contents[0]
	 			data = str(unicodedata.normalize('NFKD',unicode(data)).encode('ascii','ignore'))
				if data != " ":
					bettingData.append(data)
				# print "greyData = " + data
		except: 
			print "failed when scraping data"	
	counter = 0
	seen = False 
	for td in whiteData:
		counter += 1
		try:
			if (counter + 1) % 16 == 0:
				data = td.contents[0]
				data = str(unicodedata.normalize('NFKD',unicode(data)).encode('ascii','ignore'))
				if data != " ":
					bettingData.append(data)
				# print "whiteData = " + data
		except: 
			print "failed when scraping data"
	# for item in teamNames:
	#     print item
	# print "halfway"
	# for item in bettingData:
	#  	print item

	# concatenate team name with date, add 0, check for double header
	games = []
	duplicateCount = 0
	duplicateItems = []
	for i in range(0,len(teamNames)):
		item = teamNames[i]
		# pass on odd
		if i % 2 == 0:
			pass
		else:
			GAME_ID = item + date + "0"
			if isDuplicate(teamNames,item) and duplicateCount % 2 == 0 and item not in duplicateItems:
				duplicateCount += 1
				GAME_ID = item + date + "1"
				duplicateItems.append(item)
			elif isDuplicate(teamNames,item) and item in duplicateItems:
				GAME_ID = item + date + "2"
				duplicateCount += 1
			elif isDuplicate(teamNames,item) and item not in duplicateItems:
				GAME_ID = item + date + "1"
				duplicateItems.append(item)
				duplicateCount += 1
			games.append([GAME_ID])
			
	# get the favored odds, calculate underdog odds using helper function
	overUnder = ""
	overOdds = ""
	underOdds = ""
	counter = 0
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
			try:
				games[counter].append(homeOdds)
				games[counter].append(awayOdds)
			except:
				# betting data has overreached that of the games, fail
				print "failed: bettingData too long"
			counter += 1

	counter = 0
	for i in range(0,len(bettingData)):
		# item is over/under line
		overUnder = ""
		overOdds = ""
		underOdds = ""
		item = bettingData[i]
		insert = False
		if "u" in item:
			u = item.find("u")
			runs = item[:u]
			odds = int(item[u+1:])
			if int(runs[0]) == 1:
				overUnder = float(runs[:2])
			else:
				overUnder = float(runs[0])
			if "12" in runs:
				overUnder += 0.5
			# odds come as something like 15, so add 100
			underOdds = odds + 100
			# odds here are always positive, so * -1 and subtract -10
			overOdds = underOdds * -1 - 10
			insert = True
		elif "o" in item:
			o = item.find("o")
			runs = item[:o]
			odds = int(item[o+1:])
			if "12" in runs:
				overUnder = float(runs[0]) + 0.5
			else:
				overUnder = float(runs[0])
			# odds come as something like 15, so add 100
			overOdds = odds + 100
			# odds here are always positiv, so * -1 and subtract -10
			underOdds = overOdds * -1 - 10
			insert = True
		# means that over/under even odds, assume this means -105, -105
		else:
			if "-" not in item:
				try: 
					if "12" in item:
						overUnder = float(item[0]) + 0.5
					else:
						overUnder = float(item[0])
				except:
					# means it failed as written so not a game data
					overUnder = 0.0
				overOdds = -105
				underOdds = -105
				insert = True
		if insert:
			try:
				games[counter].append(overUnder)
				games[counter].append(overOdds)
				games[counter].append(underOdds)
			except:
				print "failed: betting data too long"
			counter += 1

	# insert into database
	cursor = DB.cursor()
	for game in games:
		try:
			query = ("INSERT INTO betting_data " 
				"(GAME_ID,HOME_ODDS,AWAY_ODDS,OVER_UNDER,OVER_ODDS,UNDER_ODDS )"
				"VALUES (%(game_id)s, %(home_odds)s, %(away_odds)s, %(over_under)s, %(over_odds)s, %(under_odds)s)")

			print game[0]
			# print game[1]
			# print game[2]
			# print game[3]
			# print game[4]
			# print game[5]

			queryData = {
				'game_id': game[0],
				'home_odds': game[1],
				'away_odds': game[2],
				'over_under': game[3],
				'over_odds': game[4],
				'under_odds': game[5], 
			} 

			cursor.execute(query,queryData)
		except:
			# if it fails pass, but don't break
			print "insert failed: " + str(game[0])

		DB.commit()
	
	# # recursively call next date, stop after 2013 for now
	if date == ENDDATE2011:
		nextDate = STARTDATE2012
	elif date == ENDDATE2012:
		nextDate = STARTDATE2013
	elif date == ENDDATE2013:
		print "done"		
	else:
		nextDate = incrementDate(date)
		getData(URL+nextDate,nextDate)
		# try except to avoid errors
		# erorrs = False
		# try:
		# 	getData(URL+nextDate,nextDate)
		# except:
		# 	nextDate = incrementDate(nextDate)
		# 	errors = True
		# 	while errors:
		# 		try:
		# 			getData(URL+nextDate,nextDate)
		# 			errors = False
		# 		except:
		# 			nextDate = incrementDate(nextDate)

# starts the script - already done 2011-2012
getData(URL+STARTDATE2013,STARTDATE2013)

# close connection when done
DB.close()

