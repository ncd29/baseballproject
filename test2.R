library(RMySQL)

# establishes connection, only contains dates before 2010
con <- dbConnect(MySQL(),dbname="Baseball", host="localhost",
                 username="ncd29sp16",password="davenport",
                 default.file="/Applications/MAMP/tmp/my.cnf")

# -----------------------------------------------------------------

# This file tests to see if there is a trend in total runs scored
# over the years 2000-2010, it should be tested continuosly as more
# years are added.

# -----------------------------------------------------------------



