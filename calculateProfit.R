library(RMySQL)
# trick for only loading the file/script if it is not already in the namespace
if(!exists("convertOddsToPercentage", mode="function")) source("bettingOdds.R")

# establishes connection, only contains dates before 2014
con <- dbConnect(MySQL(),dbname="Baseball", host="localhost",
                 username="ncd29sp16",password="davenport",
                 default.file="/Applications/MAMP/tmp/my.cnf")

# -----------------------------------------------------------
# This file is for checking what the profit would be on models
# -----------------------------------------------------------

# helper functions

# calculates the PROFIT that would be earned if this bet won given the odds
# assuming $1 was bet, so $1 at +125 returns $1.25 profit
calculateProfit <- function(odds) {
  if (odds > 0) {
    profit = odds/100
  }
  else {
    negOdds = -1*odds
    profit = 100/negOdds
  }
  return(profit)
}

# teams that you could probably have made a profit betting against for their home 
# games from 2011 - 2013: PHI,SEA,MIA,ATL,BOS,ANA,CHN,COL,CHA,HOU,MIN,NYN
# team that you could probably have made a profit betting on: OAK
teamNames = c("PHI","SEA","MIA","BOS","ANA","CHN","COL","CHA","HOU","MIN","NYN","OAK")

profits = data.frame("Team"=character(),"Profit"=numeric(),stringsAsFactors = FALSE)

for (i in 1:length(teamNames)) {
  teamName = teamNames[i]
  profits[i,1] = teamName
  if (teamName == "OAK") {
    homeOdds <- as.data.frame(dbGetQuery(con,paste("SELECT HOME_ODDS,HOME_SCORE_CT,AWAY_SCORE_CT
    FROM betting_data INNER JOIN games ON games.GAME_ID = betting_data.GAME_ID 
    WHERE games.GAME_ID LIKE '%",teamName,"%'","AND games.GAME_ID LIKE '%2016%'",sep = "")))
    for (j in 1:length(rownames(homeOdds))) {
      homeOdd = homeOdds[j,]$HOME_ODDS
      homeScore = homeOdds[j,]$HOME_SCORE_CT
      awayScore = homeOdds[j,]$AWAY_SCORE_CT
      if (homeScore > awayScore) {
        profit = calculateProfit(homeOdd)
      }
      else {
        profit = -1
      }
      if (!is.na(profits[i,2])) {
        profits[i,2] = profits[i,2] + profit
      }
      else {
        profits[i,2] = profit
      }
    }
  }
  else {
    # add a where like 2016 clause to test on 2016 data
    awayOdds <- as.data.frame(dbGetQuery(con,paste("SELECT AWAY_ODDS,HOME_SCORE_CT,AWAY_SCORE_CT
    FROM betting_data INNER JOIN games ON games.GAME_ID = betting_data.GAME_ID 
    WHERE games.GAME_ID LIKE '%",teamName,"%' AND games.GAME_ID LIKE '%2016%'",sep = "")))
    for (k in 1:length(rownames(awayOdds))) {
      awayOdd = awayOdds[k,]$AWAY_ODDS
      homeScore = awayOdds[k,]$HOME_SCORE_CT
      awayScore = awayOdds[k,]$AWAY_SCORE_CT
      if (homeScore < awayScore) {
        profit = calculateProfit(awayOdd)
      }
      else {
        profit = -1
      }
      if (!is.na(profits[i,2])) {
        profits[i,2] = profits[i,2] + profit
      }
      else {
        profits[i,2] = profit
      }
    }
  }
}

dbDisconnect(con)