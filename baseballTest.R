# source("config.R")

#downloads data from MySQL and manipulates it for display in a Shiny App
library(RMySQL)

# establishes connection, only contains dates before 2010
con <- dbConnect(MySQL(),dbname="Baseball", host="localhost",
                 username="ncd29sp16",password="davenport",
                 default.file="/Applications/MAMP/tmp/my.cnf")

# gets a vector of all the teams
teamIDs <- as.vector(dbGetQuery(con, "SELECT TEAM_ID FROM teams WHERE
                                   YEAR_ID = '2000'"))

# this data frame contains avg runs scored, home and away, for each team,
# and the differences in those values
dfHomeAway <- data.frame("Team"=character(),"avgRunsHome"=numeric(),
                         "avgRunsAway"=numeric(),"AvgRunsScoredDiff"=numeric(),
                         "avgRunsAllowedHome"=numeric(),"avgRunsAllowedAway"=numeric(),
                         "AvgRunsAllowedDiff"=numeric(),stringsAsFactors = FALSE)

# this data frame contains the difference in runs scored/allowed depending on the ballpark
# positive means batter friendly, negative means pitcher friendly
# this is the expected increase/decrease in runs scored EACH team can expect due to 
# the ballpark, independent of Home/Away
ballparkEffects <- data.frame("Team"=character(),"ParkAdvantage"=numeric(),stringsAsFactors = FALSE)

for (i in 1:length(col(teamIDs))) {
  # use query to create dataframe
  team <- teamIDs[i,]
  query1 <- paste("SELECT HOME_SCORE_CT FROM 
                  games WHERE HOME_TEAM_ID ='",team,"'",sep = "")
  query2 <- paste("SELECT AWAY_SCORE_CT FROM 
                  games WHERE AWAY_TEAM_ID ='",team,"'",sep = "")
  query3 <- paste("SELECT AWAY_SCORE_CT FROM 
                  games WHERE HOME_TEAM_ID ='",team,"'",sep = "")
  query4 <- paste("SELECT HOME_SCORE_CT FROM 
                  games WHERE AWAY_TEAM_ID ='",team,"'",sep = "")
  dfRunsScoredHome <- as.data.frame(dbGetQuery(con, query1))
  dfRunsScoredAway <- as.data.frame(dbGetQuery(con, query2))
  dfRunsAllowedHome <- as.data.frame(dbGetQuery(con, query3))
  dfRunsAllowedAway <- as.data.frame(dbGetQuery(con, query4))
  avgRunsHome <- mean((sum(dfRunsScoredHome$HOME_SCORE_CT))/length(col(dfRunsScoredHome)))
  avgRunsAway <- mean((sum(dfRunsScoredAway$AWAY_SCORE_CT))/length(col(dfRunsScoredAway)))
  avgRunsAllowedHome <- mean((sum(dfRunsAllowedHome$AWAY_SCORE_CT))/length(col(dfRunsAllowedHome)))
  avgRunsAllowedAway <- mean((sum(dfRunsAllowedAway$HOME_SCORE_CT))/length(col(dfRunsAllowedAway)))
  # the difference in runs scored away vs. home
  avgHomeAdvantageRunsScored <- avgRunsHome - avgRunsAway
  # the difference in runs allowed away vs. home
  avgHomeAdvantageRunsAllowed <- avgRunsAllowedHome - avgRunsAllowedAway
  dfHomeAway[i,] <- c(as.character(team),avgRunsHome,avgRunsAway,avgHomeAdvantageRunsScored,
                      avgRunsAllowedHome,avgRunsAllowedAway,avgHomeAdvantageRunsAllowed)
  ballparkAdvantage <- (avgHomeAdvantageRunsScored + avgHomeAdvantageRunsAllowed)/2
  ballparkEffects[i,] <- c(as.character(team),ballparkAdvantage)
  
  # TODO: store these results 
}

dbDisconnect(con)



