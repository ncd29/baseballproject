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
# end helper functions

# gets the teamIDs
teamIDs <- as.vector(dbGetQuery(con, "SELECT DISTINCT TEAM_ID FROM teams WHERE
                                   YEAR_ID = '2011'"))

# add MIA in for years after 2012, Florida Marlins switched to Miami Marlins
teamIDs[31,] = "MIA"

# this data frame stores the difference in win percentage required to break even at home
# against the actual win percentage, and shows the teams with the larger gaps

homeBreakeven <- data.frame("Team"=character(),"BreakevenWinPct"=numeric(),
                            "ActualWinPct"=numeric(),"Difference"=numeric(),
                            stringsAsFactors = FALSE)

for (i in 1:length(col(teamIDs))) {
  teamName = teamIDs[i,]
  homeOdds <- as.data.frame(dbGetQuery(con,paste("SELECT HOME_ODDS FROM betting_data 
    INNER JOIN games ON games.GAME_ID = betting_data.GAME_ID 
    WHERE games.GAME_ID LIKE '%",teamName,"%'",sep = "")))
  
  # not sure if this needed yet
  awayOdds <- as.data.frame(dbGetQuery(con,paste("SELECT AWAY_ODDS FROM betting_data 
    INNER JOIN games ON games.GAME_ID = betting_data.GAME_ID 
    WHERE games.GAME_ID LIKE '%",teamName,"%'",sep = "")))
  
  totalPercentageHome = 0
  totalPercentageAway = 0
  for (j in 1:length(rownames(homeOdds))) {
    hodds = homeOdds[j,]
    aodds = awayOdds[j,]
    percentageHome = convertOddsToPercentage(hodds)
    totalPercentageHome = totalPercentageHome + percentageHome
    percentageAway = convertOddsToPercentage(aodds)
    totalPercentageAway = totalPercentageAway + percentageAway
  }
  
  # win percent at home required to have breakeven expectation (EV = 0)
  winPercentBE = totalPercentageHome/(length(rownames(homeOdds)))
  
  wins = dbGetQuery(con,paste("SELECT COUNT(*) FROM betting_data INNER JOIN games
                    ON games.GAME_ID = betting_data.GAME_ID WHERE 
                    games.HOME_SCORE_CT > games.AWAY_SCORE_CT
                    AND games.GAME_ID LIKE '%",teamName,"%'",sep = ""))
  
  losses = dbGetQuery(con,paste("SELECT COUNT(*) FROM betting_data INNER JOIN games
                    ON games.GAME_ID = betting_data.GAME_ID WHERE 
                    games.HOME_SCORE_CT < games.AWAY_SCORE_CT
                    AND games.GAME_ID LIKE '%",teamName,"%'",sep = ""))
  
  actualWinPct = wins/(wins+losses)
  homeBreakeven[i,1] = teamName
  homeBreakeven[i,2] = winPercentBE
  homeBreakeven[i,3] = actualWinPct
  homeBreakeven[i,4] = winPercentBE - actualWinPct
}

dbDisconnect(con)