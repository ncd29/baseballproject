library(RMySQL)
# trick for only loading the file/script if it is not already in the namespace
if(!exists("convertOddsToPercentage", mode="function")) source("calculateProfit.R")

# establishes connection, only contains dates before 2014
con <- dbConnect(MySQL(),dbname="Baseball", host="localhost",
                 username="ncd29sp16",password="davenport",
                 default.file="/Applications/MAMP/tmp/my.cnf")

# -----------------------------------------------------------
# This file is for checking what the profit would be on 538 predictions
# -----------------------------------------------------------

# for 538
#games <- as.data.frame(dbGetQuery(con, "SELECT HOME_SCORE_CT,AWAY_SCORE_CT,HOME_ODDS,
 #                           AWAY_ODDS,HOME_PREDICTION,AWAY_PREDICTION FROM games 
  #                          INNER JOIN betting_data ON games.GAME_ID = betting_data.GAME_ID 
   #                 INNER JOIN predictions ON betting_data.GAME_ID = predictions.GAME_ID
     #                 AND predictions.PREDICTION_FROM = 'fivethirtyeight.com'"))

# for teamrankings
games <- as.data.frame(dbGetQuery(con, "SELECT HOME_SCORE_CT,AWAY_SCORE_CT,HOME_ODDS,
                           AWAY_ODDS,HOME_PREDICTION,AWAY_PREDICTION FROM games 
                          INNER JOIN betting_data ON games.GAME_ID = betting_data.GAME_ID 
                 INNER JOIN predictions ON betting_data.GAME_ID = predictions.GAME_ID
                 AND predictions.PREDICTION_FROM = 'teamrankings.com'"))

profits = 0
print(length(rownames(games)))
for (i in 1:length(rownames(games))) {
  homePercentage = convertOddsToPercentage(games[i,]$HOME_ODDS)
  awayPercentage = convertOddsToPercentage(games[i,]$AWAY_ODDS)
  # add artifical adjustments to test
  #homePrediction = games[i,]$HOME_PREDICTION + .05
  #awayPrediction = games[i,]$AWAY_PREDICTION - .05
  homePrediction = games[i,]$HOME_PREDICTION
  awayPrediction = games[i,]$AWAY_PREDICTION
  homeRuns = games[i,]$HOME_SCORE_CT
  awayRuns = games[i,]$AWAY_SCORE_CT
  # checks for not betting under certain condition
  if (FALSE) {
    profit = 0
  }
  else {
    # bet on home team
    if (homePrediction > homePercentage) {
      if (homeRuns > awayRuns) {
        profit = calculateProfit(games[i,]$HOME_ODDS)
      }
      else {
        profit = -1
      }
    }
    else if (awayPrediction > awayPercentage) {
      if (awayRuns > homeRuns) {
        profit = calculateProfit(games[i,]$AWAY_ODDS)
      }
      else {
        profit = -1
      }
    }
    else {
      profit = 0
    }
  }
  profits = profits + profit
}

# only 2.739 % ROI without any adjustments :(
# .71 % ROI with .02% home adjustment, only gets worse if add more
# adjusting positively for away teams improved a little, but not beyond 4% ROI
# 2.85 % if remove games where home team has > 70% predictions
# teamRankings had just under 0 ROI!
print(profits/(length(rownames(games)))*100)
dbDisconnect(con)