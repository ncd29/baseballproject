'''
This is a web scraper that gathers baseball predictions
from teamrankings.com and stores them in the baseball DB
for comparison to actual results
'''
# TODO remove prints

import mysql.connector
import unicodedata
import requests
import bs4
from bs4 import BeautifulSoup
from betting_odds_scraper import incrementDate

# CONSTANTS
URL = "https://www.teamrankings.com/mlb/ranking/predictive-by-other/?date="
DB = mysql.connector.connect(user='root',password='root',host='localhost',database='Baseball',
    unix_socket="/Applications/MAMP/tmp/mysql/mysql.sock")
STARTDATE = "20130331"
ENDDATE = "20131101"

# helper functions

""" 
inserts dashes into the date to convert the date into 
the format required by the url
@ param - date: the date
"""
def insertDashes(date):
	year = date[:4]
	month = date[4:6]
	day = date[6:]
	return year + "-" + month + "-" + day

"""
converts the team name on teamrankings to the format used by DB
@param - team: team name on teamrankings
"""
def convertTeamName(team):
	# convert the team name to correct abbreviation
	teamName = ""
	if team == "LA Angels":
		teamName = "ANA"
	if team == "Baltimore":
		teamName = "BAL"
	if team == "Boston":
		teamName = "BOS"
	if team == "Chi Sox":
		teamName = "CHA"
	if team == "Cleveland":
		teamName = "CLE"
	if team == "Detroit":
		teamName = "DET"
	if team == "Kansas City":
		teamName = "KCA"
	if team == "Minnesota":
		teamName = "MIN"
	if team == "NY Yankees":
		teamName = "NYA"
	if team == "Oakland":
		teamName = "OAK"
	if team == "Seattle":
		teamName = "SEA"
	if team == "Tampa Bay":
		teamName = "TBA"
	if team == "Texas":
		teamName = "TEX"
	if team == "Toronto":
		teamName = "TOR"
	if team == "Arizona":
		teamName = "ARI"
	if team == "Atlanta":
		teamName = "ATL"
	if team == "Chi Cubs":
		teamName = "CHN"
	if team == "Cincinnati":
		teamName = "CIN"
	if team == "Colorado":
		teamName = "COL"
	if team == "Miami":
		teamName = "MIA"
	if team == "Houston":
		teamName = "HOU"
	if team == "LA Dodgers":
		teamName = "LAN"
	if team == "Milwaukee":
		teamName = "MIL"
	if team == "NY Mets":
		teamName = "NYN"
	if team == "Philadelphia":
		teamName = "PHI"
	if team == "Pittsburgh":
		teamName = "PIT"
	if team == "San Diego":
		teamName = "SDN"
	if team == "SF Giants":
		teamName = "SFN"
	if team == "St. Louis":
		teamName = "SLN"
	if team == "Washington":
		teamName = "WAS"
	return teamName
# end helper functions

# parse the html on each date to get the ratings for that day
def run(date):
	# get the data from the page and store in dict format
	request = requests.get(URL + insertDashes(date))
	soup = BeautifulSoup(request.content)
	rows = soup.find_all("tr")
	ratings = {}
	counter = 0
	for row in rows:
		# this means row is not a team row or all teams have been seen
		if row.find_all("a") != [] and counter < 30:
			teamName = row.find("a").contents[0]
			teamName = convertTeamName(str(unicodedata.normalize('NFKD',unicode(teamName)).encode('ascii','ignore')))
			print teamName
			rating = float(str(row.find("td",{"class":"text-right"}).contents[0]))
			print rating
			ratings[teamName] = rating
			counter += 1
	# get the relevant games on this date from DB
	cursor = DB.cursor(buffered = True)

	query =  "SELECT GAME_ID,AWAY_TEAM_ID,HOME_TEAM_ID FROM games WHERE GAME_ID LIKE %s"
	
	cursor.execute(query,("%"+date+"%",))
	
	games = []
	awayTeams = []
	homeTeams = []
	counter = 0
	for (GAME_ID,AWAY_TEAM_ID,HOME_TEAM_ID) in cursor:
		print counter
		cursor2 = DB.cursor()
		awayRating = float(ratings[str(AWAY_TEAM_ID)])
		homeRating = float(ratings[HOME_TEAM_ID]) + .3 # for home field adv.
		# the average difference in runs the home team is expected over the away team
		homeAdvantage = homeRating - awayRating
		homeProb = .512 + homeAdvantage * .1
		awayProb = .512 - homeAdvantage * .1
		print GAME_ID
		print homeProb
		print awayProb
		try: 
			insertQuery = ("INSERT INTO predictions "
						 "(GAME_ID,HOME_PREDICTION,AWAY_PREDICTION,PREDICTION_FROM) "
						 "VALUES (%(game_id)s, %(homeProb)s, %(awayProb)s, %(from)s)")

				
			insertQueryData = {
				'game_id': GAME_ID,
				'homeProb': homeProb,
				'awayProb': awayProb,
				'from': "teamrankings.com",
			}

			cursor2.execute(insertQuery,insertQueryData)
			print "query succeeded"
		except:
			print "query failed"
		counter += 1

		DB.commit()

# run the script from start until end date
date = STARTDATE
while date != ENDDATE:
	run(date)
	date = incrementDate(date)

DB.close()