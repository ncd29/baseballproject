library(RMySQL)

# establishes connection, only contains dates before 2010
con <- dbConnect(MySQL(),dbname="Baseball", host="localhost",
                 username="ncd29sp16",password="davenport",
                 default.file="/Applications/MAMP/tmp/my.cnf")

# -----------------------------------------------------------
# This file is for testing relationships between results and the betting line.
# -----------------------------------------------------------

# helper functions

# converts odds into the percentage of time one needs a team with these 
# odds to win in order to break even, assumes odds are in +110, etc. format
convertOddsToPercentage <- function(odds) {
  if (odds > 0) {
    percentage = 100/(odds+100)
  }
  else {
    negOdds = -1*odds
    percentage = negOdds/(negOdds+100)
  }
  return(percentage)
}

bosHomeOdds <- as.data.frame(dbGetQuery(con,"SELECT HOME_ODDS FROM betting_data INNER JOIN 
  games ON games.GAME_ID = betting_data.GAME_ID WHERE games.GAME_ID LIKE '%BOS%'"))

totalPercentage = 0
for (i in 1:length(rownames(bosHomeOdds))) {
  odds = bosHomeOdds[i,]
  percentage = convertOddsToPercentage(odds)
  totalPercentage = totalPercentage + percentage
}

winPercentBE = totalPercentage/(length(rownames(bosHomeOdds)))

wins = dbGetQuery(con,"SELECT COUNT(*) FROM betting_data INNER JOIN games
                  ON games.GAME_ID = betting_data.GAME_ID WHERE 
                  games.HOME_SCORE_CT > games.AWAY_SCORE_CT
                  AND games.GAME_ID LIKE '%BOS%'")

losses = dbGetQuery(con,"SELECT COUNT(*) FROM betting_data INNER JOIN games
                  ON games.GAME_ID = betting_data.GAME_ID WHERE 
                  games.HOME_SCORE_CT < games.AWAY_SCORE_CT
                  AND games.GAME_ID LIKE '%BOS%'")

print("win percentage needed to break even: ")
print(winPercentBE)
print("actual win percentage: ")
print(wins/(wins+losses))