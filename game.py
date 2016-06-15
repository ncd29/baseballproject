"""
Python file for representing a game object to
make insertion into the database easier
"""

class Game:

	def __init__(self,gameId,homeOdds,awayOdds,overUnder,overOdds,underOdds):
		self.gameId = gameId
		self.homeOdds = homeOdds
		self.awayOdds = awayOdds
		self.overUnder = overUnder
		self.overOdds = overOdds
		self.underOdds = underOdds
