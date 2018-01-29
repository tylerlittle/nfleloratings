"""
Author: Tyler Little
File: nflelocalculator.py
Created: 2018/01/25
Description: A python program to calculate elo ratings for the National Football League.
"""
import math


def main(homeTeam,awayTeam,homeTeamCR,awayTeamCR,homeScore,awayScore,seasonType):

	pd = abs(homeScore-awayScore)
	k = determineK(seasonType)
	homeTeamExpScore,awayTeamExpScore = computeExpectedScores(homeTeamCR,awayTeamCR)
	
	if homeScore > awayScore:
		elow = homeTeamCR
		elol = awayTeamCR
		homeTeamSa = 1
		awayTeamSa = 0
		movMultiplier = computeMovMultiplier(elow,elol,pd)
	
	elif homeScore < awayScore:
		elow = awayTeamCR
		elol = homeTeamCR
		homeTeamSa = 0
		awayTeamSa = 1
		movMultiplier = computeMovMultiplier(elow,elol,pd)
		
	homeTeamNR = homeTeamCR + k * movMultiplier * (homeTeamSa - homeTeamExpScore)
	awayTeamNR = awayTeamCR + k * movMultiplier * (awayTeamSa - awayTeamExpScore)
	
	print("Home Team Old Rating:",homeTeamCR)
	print("Home Team New Rating:",homeTeamNR)
	print("Visiting Team Old Rating:",awayTeamCR)
	print("Visiting Team New Rating:",awayTeamNR)
	
	return

def determineK(seasonType):
    if seasonType == "REG":
        k = 20
    elif seasonType == "POST":
        k = 24

    return k

def computeExpectedScores(homeTeamCR,awayTeamCR):
    homeTeamExpScore = homeTeamCR / (homeTeamCR + awayTeamCR)
    awayTeamExpScore = awayTeamCR / (homeTeamCR + awayTeamCR)
    
    return homeTeamExpScore,awayTeamExpScore

# Margin of Victory Multiplier
def computeMovMultiplier(elow,elol,pd):
    movMultiplier = math.log(abs(pd+1))*(2.2 / ((0.001 * (elow - elol))+2.2))

    return movMultiplier
	
