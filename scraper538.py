'''
This is a web scraper that gathers baseball predictions
from fivethirtyeight.com and stores them in the baseball DB
for comparison to actual results
'''

import mysql.connector
import unicodedata
import requests
import bs4
from bs4 import BeautifulSoup

# CONSTANTS
URL = "http://projects.fivethirtyeight.com/2016-mlb-predictions/"
DB = mysql.connector.connect(user='root',password='root',host='localhost',database='Baseball',
    unix_socket="/Applications/MAMP/tmp/mysql/mysql.sock")

# the teams, formatted correctly for the url
teams = ["orioles","diamondbacks","red-sox","braves","white-sox","cubs",
"indians","reds","tigers","rockies","astros","dodgers","royals","marlins"
,"angels","brewers","twins","mets","yankees","phillies","athletics",
"pirates","mariners","padres","rays","giants","rangers","cardinals",
"blue-jays","nationals"]

# helper functions

""" 
creates a gameID of the format required by the database for insertion
into the predictions table, also converts the team into the proper 
abbreviation
@param - date: the date of the game
@param - team: the home team
returns a gameID string
"""
def createGameID(date,team):
	# convert the team name to correct abbreviation
	teamName = ""
	if team == "angels":
		teamName = "ANA"
	if team == "orioles":
		teamName = "BAL"
	if team == "red-sox":
		teamName = "BOS"
	if team == "white-sox":
		teamName = "CHA"
	if team == "indians":
		teamName = "CLE"
	if team == "tigers":
		teamName = "DET"
	if team == "royals":
		teamName = "KCA"
	if team == "twins":
		teamName = "MIN"
	if team == "yankees":
		teamName = "NYA"
	if team == "athletics":
		teamName = "OAK"
	if team == "mariners":
		teamName = "SEA"
	if team == "rays":
		teamName = "TBA"
	if team == "rangers":
		teamName = "TEX"
	if team == "blue-jays":
		teamName = "TOR"
	if team == "diamondbacks":
		teamName = "ARI"
	if team == "braves":
		teamName = "ATL"
	if team == "cubs":
		teamName = "CHN"
	if team == "reds":
		teamName = "CIN"
	if team == "rockies":
		teamName = "COL"
	if team == "marlins":
		teamName = "MIA"
	if team == "astros":
		teamName = "HOU"
	if team == "dodgers":
		teamName = "LAN"
	if team == "brewers":
		teamName = "MIL"
	if team == "mets":
		teamName = "NYN"
	if team == "phillies":
		teamName = "PHI"
	if team == "pirates":
		teamName = "PIT"
	if team == "padres":
		teamName = "SDP"
	if team == "giants":
		teamName = "SFN"
	if team == "cardinals":
		teamName = "SLN"
	if team == "nationals":
		teamName = "WAS"
	# create the actual date part of the string
	oldDate = date
	newDate = date[4:]
	date = newDate[:3]
	month = ""
	if date == "Jan":
		month = "01"
	if date == "Feb":
		month = "02"
	if date == "Mar":
		month = "03"
	if date == "Apr":
		month = "04"
	if date == "May":
		month = "05"
	if date == "Jun":
		month = "06"
	if date == "Jul":
		month = "07"
	if date == "Aug":
		month = "08"
	if date == "Sep":
		month = "09"
	if date == "Oct":
		month = "10"
	if date == "Nov":
		month = "11"
	if date == "Dec":
		month = "12"
	day = newDate[4:]
	if int(day) < 10:
		day = "0" + day
	return teamName + "2016" + month + day

# end helper functions



# parse the html to get each teams prob of winning
def runScript():
	for team in teams:
		print team
		request = requests.get(URL + team + "/")
		soup = BeautifulSoup(request.content)

		played = soup.find("div",{"id":"played"})
		games = played.find_all("div",{"class":"games"})

		# double header checks
		dates = []
		for game in games:
			date = game.find("span",{"class":"no-color"}).contents[0]
			# if date already seen means it's a double header, add 2
			ending = "0"
			if date in dates:
				ending = "2" 
			dates.append(date)
			middle = game.find("span",{"class":"middle"}).contents[0]
			probs = game.find_all("div",{"class":"prob"})
			teamNames = game.find_all("a")
			team1 = teamNames[1].contents[0]
			team2 = teamNames[0].contents[0]
			prob1 = probs[0].contents[0]
			prob2 = probs[1].contents[0]
			homeProb = prob2 
			awayProb = prob1
			home = team1
			away = team2
			if str(unicodedata.normalize('NFKD',unicode(middle)).encode('ascii','ignore')) == "vs.":
				homeProb = prob1
				awayProb = prob2
				home = team2
				away = team2
			# check dates for doubleheaders - try to enter with current ending
			# if fails, try ending in 1
			GAME_ID = createGameID(date,home.lower()) + ending
			GAME_IDbackup = createGameID(date,home.lower()) + "1"
			homeProb = "0." + homeProb[:2]
			awayProb = "0." + awayProb[:2]
			homeProb = float(homeProb)
			awayProb = float(awayProb)
			print GAME_ID
			print homeProb
			print awayProb
			# insert into DB
			cursor = DB.cursor()
			try:
				query = ("INSERT INTO predictions "
					 "(GAME_ID,HOME_PREDICTION,AWAY_PREDICTION,PREDICTION_FROM) "
					 "VALUES (%(game_id)s, %(homeProb)s, %(awayProb)s, %(from)s)")

			
				queryData = {
					'game_id': GAME_ID,
					'homeProb': homeProb,
					'awayProb': awayProb,
					'from': "fivethirtyeight.com"
				}

				cursor.execute(query,queryData)
			except:
				print "query failed"
			DB.commit()
			# except:
			# 	try:
			# 		queryData = {
			# 			'game_id': GAME_IDbackup,
			# 			'homeProb': homeProb,
			# 			'awayProb': awayProb,
			# 		}

			# 		cursor.execute(query,queryData)
			# 	except:
			# 		print "query failed"

runScript()

DB.close()	

