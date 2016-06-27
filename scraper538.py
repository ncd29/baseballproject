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

# the teams, formatted correctly for the url
teams = ["orioles","diamondbacks","red-sox","braves","white-sox","cubs",
"indians","reds","tigers","rockies","astros","dodgers","royals","marlins"
,"angels","brewers","twins","mets","yankees","phillies","athletics",
"pirates","mariners","padres","rays","giants","rangers","cardinals",
"blue-jays","nationals"]

# parse the html to get each teams prob of winning
for team in teams:
	request = requests.get(URL + team)
	soup = BeautifulSoup(request.content)

	games = soup.find_all("div",{"class":"game"})

	for game in games:
		date = game.find("span",{"class":"no-color"}).contents[0]
		middle = game.find("span",{"class":"middle"}).contents[0]
		probs = game.find_all("div",{"class":"prob"})
		prob1 = probs[0].contents[0]
		prob2 = probs[1].contents[0]
		homeProb = prob2 
		awayProb = prob1
		if str(unicodedata.normalize('NFKD',unicode(middle)).encode('ascii','ignore')) == "vs.":
			homeProb = prob1
			awayProb = prob2
		print date
		print middle
		print prob1
		print prob2
