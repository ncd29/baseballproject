'''
This is a web scraper that gathers baseball predictions
from fivethirtyeight.com and stores them in the baseball DB
for comparison to actual results.
This scraper scrapes games that are in the future and stores the
GAMEID and betting predictions.  scraper538.py pulls information
from already completed games
'''

# TODO: script works but query needs fixing, probably the games one
import scraper538constants
from scraper538constants import * 
import datetime
from datetime import *

# constants
TODAY = date.today()

# parse the html to get each teams prob of winning
def runScript():
	for team in teams:
		print team
		request = requests.get(URL + team + "/")
		soup = BeautifulSoup(request.content)

		played = soup.find("div",{"id":"unplayed"})
		games = played.find_all("div",{"class":"games"})

		# double header checks
		dates = []
		counter = 0
		for game in games:
			oldDate = game.find("div",{"class":"date"}).contents[0]
			# if date already seen means it's a double header, add 2
			ending = "0"
			if oldDate in dates:
				ending = "2" 
			dates.append(oldDate)
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
			GAME_ID = createGameID(oldDate,home.lower()) + ending
			# if date is not today or before today, break for this team
			print GAME_ID
			print home
			year = int(GAME_ID[3:7])
			month = int(GAME_ID[7:9])
			day = int(GAME_ID[9:11])
			newDate = date(year,month,day)
			# only insert new games that have not been inserted already 
			if newDate > TODAY:
				break
			# if counter > 2:
			# 	break
			# handles doubleheaders
			GAME_IDbackup = createGameID(oldDate,home.lower()) + "1"
			homeProb = "0." + homeProb[:2]
			awayProb = "0." + awayProb[:2]
			homeProb = float(homeProb)
			awayProb = float(awayProb)
			print GAME_ID
			print homeProb
			print awayProb
			# insert into DB
			cursor = DB.cursor()
			#TODO insert the new game id into games first
			try:
				query2 = ("INSERT INTO games "
					"(GAME_ID) "
					"VALUES (%(game_id)s)")

				query2data = {
					'game_id': GAME_ID,
				}

				cursor.execute(query2,query2data)

				query = ("INSERT INTO predictions "
					 "(GAME_ID,HOME_PREDICTION,AWAY_PREDICTION,PREDICTION_FROM) "
					 "VALUES (%(game_id)s, %(homeProb)s, %(awayProb)s, %(from)s)")

			
				queryData = {
					'game_id': GAME_ID,
					'homeProb': homeProb,
					'awayProb': awayProb,
					'from': "fivethirtyeight.com",
				}

				cursor.execute(query,queryData)
				print "query succeeded"
			except:
				print "query failed"
			DB.commit()
			counter = counter + 1

runScript()

DB.close()