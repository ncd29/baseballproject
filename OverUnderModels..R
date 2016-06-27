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
