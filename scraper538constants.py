""" Helper functions and constants file for 538 scrapers """

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
	if team == "red sox":
		teamName = "BOS"
	if team == "white sox":
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
	if team == "blue jays":
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
	return str(teamName + "2016" + month + day)

# end helper functions
