library(RMySQL)

# establishes connection, only contains dates before 2010
con <- dbConnect(MySQL(),dbname="Baseball", host="localhost",
                 username="ncd29sp16",password="davenport",
                 default.file="/Applications/MAMP/tmp/my.cnf")

# -----------------------------------------------------------------

# This file tests to see if there is a trend in total runs scored
# over the years 2000-2009, it should be tested continuosly as more
# years are added.

# CREATES: a data frame of average total runs per game for each year

# -----------------------------------------------------------------

# gets a vector of all the games
games <- as.data.frame(dbGetQuery(con, "SELECT GAME_ID,AWAY_SCORE_CT,HOME_SCORE_CT FROM games"))

# data frame to store the runs per game for each year
# Row 1 = 2000 Row 2 = 2001 etc.
runsPerGame <- data.frame("RunsPerGame"=numeric(),
                          stringsAsFactors = FALSE)

# keeps track of the number of games in that year, need to change length for more years
counter = vector(mode = "numeric", length = 10)

# for each game, add the value to the total count for that year
for (i in 1:length(rownames(games))) {
  gameID = games[i,]$GAME_ID
  year = as.numeric(substr(gameID,4,7))
  
  # the index for the row in runsPerGame 1 = 2000 2 = 2001 etc.
  index = year - 1999
  
  # increment the total score
  if (is.na(runsPerGame[index,])) {
    runsPerGame[index,] = games[i,]$HOME_SCORE_CT + games[i,]$AWAY_SCORE_CT
  }
  else { 
    runsPerGame[index,] = runsPerGame[index,] + games[i,]$HOME_SCORE_CT + games[i,]$AWAY_SCORE_CT
  }
  counter[index] = counter[index] + 1
}

# divide by total games to finish data frame
for (i in 1:length(rownames(runsPerGame))) {
  runsPerGame[i,] = runsPerGame[i,]/counter[i]
  rownames(runsPerGame)[i] = i + 1999
}

dbDisconnect(con)

