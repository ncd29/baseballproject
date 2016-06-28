library(RMySQL)
# trick for only loading the file/script if it is not already in the namespace
if(!exists("convertOddsToPercentage", mode="function")) source("calculateProfit.R")

# establishes connection, only contains dates before 2014
con <- dbConnect(MySQL(),dbname="Baseball", host="localhost",
                 username="ncd29sp16",password="davenport",
                 default.file="/Applications/MAMP/tmp/my.cnf")

# -----------------------------------------------------------
# This file is for checking what the profit would be on over/under models
# -----------------------------------------------------------

# gets the teamIDs - figure out how to merge MIA and FLO
teamIDs <- as.vector(dbGetQuery(con, "SELECT DISTINCT TEAM_ID FROM teams WHERE
                                   YEAR_ID = '2011'"))

overUnderProfits = data.frame("Team"=character(),"Profit"=numeric(),stringsAsFactors = FALSE)

for (i in 1:length(col(teamIDs))) {
  teamName = teamIDs[i,]
  overUnderProfits[i,1] = teamName
  overOdds <- as.data.frame(dbGetQuery(con,paste("SELECT OVER_UNDER,OVER_ODDS,HOME_SCORE_CT,AWAY_SCORE_CT
    FROM betting_data INNER JOIN games ON games.GAME_ID = betting_data.GAME_ID 
    WHERE games.GAME_ID LIKE '%",teamName,"%' AND games.TEMP_PARK_CT > 70 ",sep = "")))
  if (length(rownames(overOdds)) > 0) {
    for (j in 1:length(rownames(overOdds))) {
      overUnder = overOdds[j,]$OVER_UNDER
      odds = overOdds[j,]$OVER_ODDS
      totalScore = overOdds[j,]$HOME_SCORE_CT + overOdds[j,]$AWAY_SCORE_CT
      if (totalScore > overUnder) {
        profit = calculateProfit(odds)
      }
      else {
        profit = -1
      }
      if (!is.na(overUnderProfits[i,2])) {
        overUnderProfits[i,2] = overUnderProfits[i,2] + profit
      }
      else {
        overUnderProfits[i,2] = profit
      }
    }
  }
}

