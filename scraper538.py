'''
This is a web scraper that gathers baseball predictions
from fivethirtyeight.com and stores them in the baseball DB
for comparison to actual results.
This scraper scrapes games that have finished and stores the 
results in the database.  scraper538predict.py pulls information
on predictions in the future
'''

# TODO: rerun b/c may have missed red sox, blue jays and white sox
import scraper538constants

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
			# TODO: add query to Update games table where gameid = gameid to the scores to
			# keep track of how well the predicitons have been doing
			try:
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
			except:
				try:
					queryData = {
						'game_id': GAME_IDbackup,
						'homeProb': homeProb,
						'awayProb': awayProb,
						'from':"fivethirtyeight.com",
					}

					cursor.execute(query,queryData)
				except:
					print "query failed"
			DB.commit()

runScript()

DB.close()	

