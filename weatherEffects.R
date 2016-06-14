# source("config.R")

# -----------------------------------------------------------------

# This file regresses total score on wind speed for each direction.
# The relationship between wind direction and score seems meaningful,
# but the relationshup between wind speed and score does not.  It also
# regresses total score against temperature. There is a statistically
# significant relationship between temperature and score

# CREATES: 
# - regression results for score on wind speed for each direction
# - regression results for score on temperature

# Takes 1 minute to loop right now

# NOTE: 
# - Arizona, Houston, Miami, Milwaukee, Seattle, and Toronto have retractable roofs
# - Tampa Bay always has a roof
# - weather effects should not be taken into account for these games, so it 
# - doesn't need to be checked each time, since they usually seem to be closed

# -----------------------------------------------------------------

#downloads data from MySQL and manipulates it for display in a Shiny App
library(RMySQL)

# establishes connection, only contains dates before 2010
con <- dbConnect(MySQL(),dbname="Baseball", host="localhost",
                 username="ncd29sp16",password="davenport",
                 default.file="/Applications/MAMP/tmp/my.cnf")

# file for testing various regressions on runs scored

# gets a vector of all the games
games <- as.data.frame(dbGetQuery(con, "SELECT GAME_ID,AWAY_SCORE_CT,HOME_SCORE_CT,TEMP_PARK_CT,
                                  WIND_DIRECTION_PARK_CD,WIND_SPEED_PARK_CT FROM games"))

# this is a dataframe set up to test the relationship
# between wind direction, speed and total score
windEffects <- data.frame("TotalScore"=numeric(), "WindDirection"=numeric(), "WindSpeed"=numeric(),
                          stringsAsFactors = FALSE)

# data frame to test relationship between score and temperature
tempEffects <- data.frame("TotalScore" = numeric(), "Temperature"=numeric(),stringsAsFactors = FALSE)

# for each game, add to the data frame
for (i in 1:length(rownames(games))) {
    # total score
    windEffects[i,1] = games[i,]$HOME_SCORE_CT + games[i,]$AWAY_SCORE_CT
    tempEffects[i,1] = games[i,]$HOME_SCORE_CT + games[i,]$AWAY_SCORE_CT
    
    # number specifying wind direction
    windEffects[i,2] = games[i,]$WIND_DIRECTION_PARK_CD
    
    # wind speed
    windEffects[i,3] = games[i,]$WIND_SPEED_PARK_CT
    
    # temperature
    tempEffects[i,2] = games[i,]$TEMP_PARK_CT
}

for (i in 1:8) {
    # create a data frame just for that direction
    direction <- as.data.frame(windEffects[which(windEffects$WindDirection == i),])
    
    # create the linear model
    windModel <- lm(direction$TotalScore ~ direction$WindSpeed)
    # uncomment this line to print the summary of each regression
    # print(summary(windModel))
    
    # TODO: add these results to a data frame and store in csv or some format
}

tempModel <- lm(tempEffects$TotalScore ~ tempEffects$Temperature)

dbDisconnect(con)

