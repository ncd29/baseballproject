library(shiny)
library(RMySQL)
if(!exists("convertOddsToPercentage", mode="function")) source("calculateProfit.R")

# establishes connection, only contains dates before 2014
con <- dbConnect(MySQL(),dbname="Baseball", host="localhost",
                 username="ncd29sp16",password="davenport"
                 ,default.file="/Applications/MAMP/tmp/my.cnf")
# need to add in my.cnf folder to get working again
# -----------------------------------------------------------
# This file is a Shiny app for making baseball predictions
# -----------------------------------------------------------

today = Sys.Date()
year = substr(today,1,4)
month = substr(today,6,7)
day = substr(today,9,10)
# for 538 - get all games from 2016, this is hardcoded for now
games <- as.data.frame(dbGetQuery(con,paste("SELECT GAME_ID,HOME_PREDICTION,AWAY_PREDICTION FROM 
                      predictions WHERE PREDICTION_FROM = 'fivethirtyeight.com'
                      AND GAME_ID LIKE '%2016",month,day,"%'",sep="")))

# the data frame for storing the actual odds
odds <- data.frame("AwayOdds"=numeric(),"HomeOdds"=numeric(),stringsAsFactors = FALSE)

n <- shinyUI(fluidPage(
  titlePanel(paste("Baseball Predictions for ",year,month,day)),
  
  sidebarLayout(
    
    sidebarPanel(
      # enter odds in format +135,-145
      h1("Enter odds here"),
      
      lapply(1:length(rownames(games)),function(i) {
        textInput(paste("game",i,sep=""),games[i,1])
      })
    ),
    mainPanel(
      submitButton("submit"),
      uiOutput("out"),
      
      lapply(1:length(rownames(games)),function(i) {
        textOutput(paste("game",i,sep=""))
      })
    )
  )
))

d <- shinyServer(
  function(input, output) {
    # get the inputted odds
    output$out <- renderUI({ 
      lapply(1:length(rownames(games)),function(i) {
        odds[i,1] = substr(input[[paste("game",i,sep="")]],1,4)
        #print(paste(odds[i,1]))
        odds[i,2] = substr(input[[paste("game",i,sep="")]],6,9)
        #print(as.numeric(odds[i,2]))
      #})
      #lapply(1:length(rownames(games)),function(i) {
      #output[[paste("game",i,sep="")]] <- renderText({
      if (!(odds[i,1] == "")) {
        awayLine = convertOddsToPercentage(as.numeric(odds[i,1]))
        homeLine = convertOddsToPercentage(as.numeric(odds[i,2]))
        awayPrediction = games[i,]$AWAY_PREDICTION - .04
        homePrediction = games[i,]$HOME_PREDICTION - .04
        print(awayPrediction)
        print(awayLine)
        if (awayPrediction >= awayLine) {
          HTML(paste("For game",games[i,]$GAME_ID,": ","bet on the away team.","The edge over the betting line is",substr(as.character(awayPrediction-awayLine),1,6)),sep="<br/>")
        }
        else if (homePrediction >= homeLine) {
          HTML(paste("For game",games[i,]$GAME_ID,": ","bet on the home team.","The edge over the betting line is",substr(as.character(homePrediction-homeLine),1,6)),sep="<br/>")
        }
        else {
          HTML(paste("For game",games[i,]$GAME_ID,": ","don't bet on either team.","There is no edge over the betting line."),sep="<br/>")
        }
      }
      else {
        HTML(paste("wating for input"),sep="<br/>")
      }
       # })
    })
  })
})
shinyApp(ui = n, server = d)

#dbDisconnect(con)
