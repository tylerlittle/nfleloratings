"""
Author: Tyler Little
File: nflelocalculator.py
Created: 2018/01/25
Description: A python program to calculate elo ratings for the National Football League.
"""
import math
import mysql.connector

def main():
    cursor,connection = connectToDatabase()
    cursor,nflData = fetchAllNflData(cursor)
    for game in nflData:
        homeTeamCR,awayTeamCR=getCurrentRankings(game,cursor)
        seasonYear,seasonWeek,seasonType,homeTeam,homeScore,awayScore,awayTeam,pd = setGameVars(game)
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
            
        homeTeamNR,awayTeamNR = computeNewRatings(homeTeamCR,awayTeamCR,k,movMultiplier,homeTeamSa,awayTeamSa,homeTeamExpScore,awayTeamExpScore)
        updateRatings(cursor,homeTeamNR,homeTeam,awayTeamNR,awayTeam)

    displayFinalRatings(cursor)
    disconnectDatabaseAndCursor(connection,cursor)
    
    return

def connectToDatabase():

    connection = mysql.connector.connect(user='root',password='toor',host='127.0.0.1',database='nfldatabase')
    cursor = connection.cursor(buffered=True)

    return cursor,connection

def disconnectDatabaseAndCursor(connection,cursor):
    cursor.close()
    connection.close()
    
    return

def fetchAllNflData(cursor):
    queryNflData = ("SELECT * FROM nfldata;")
    cursor.execute(queryNflData)
    nflData = cursor.fetchall()

    return cursor,nflData

def getCurrentRankings(game,cursor):
        queryCurrentRankings = ("SELECT currentranking FROM currentrankings join teams ON currentrankings.id = teams.team_id WHERE team_name = %(teamName)s;")
        cursor.execute(queryCurrentRankings, {'teamName': game[4]})
        data = cursor.fetchone()
        homeTeamCR = data[0]
        cursor.execute(queryCurrentRankings, {'teamName': game[7]})
        data = cursor.fetchone()
        awayTeamCR = data[0]
        print("HomeTeamCR: " + str(homeTeamCR) + "   AwayTeamCR: " + str(awayTeamCR))

        return homeTeamCR,awayTeamCR

def setGameVars(game):
    seasonYear = game[1]
    seasonWeek = game[2]
    seasonType = game[3]
    homeTeam = game[4]
    homeScore = game[5]
    awayScore = game[6]
    awayTeam = game[7]
    pd = abs(game[5]-game[6])

    print("SeasonYear:",str(seasonYear))
    print("Week:",str(seasonWeek))
    print("SeasonType:",seasonType)
    print("HomeTeam:",homeTeam)
    print("HomeScore:",str(homeScore))
    print("AwayScore:",str(awayScore))
    print("AwayTeam:",awayTeam)

    return seasonYear,seasonWeek,seasonType,homeTeam,homeScore,awayScore, \
           awayTeam,pd

def determineK(seasonType):
    if seasonType == "REG":
        k = 20
    elif seasonType == "POST":
        k = 21

    print("k-factor: " + str(k))

    return k

def computeExpectedScores(homeTeamCR,awayTeamCR):
    homeTeamExpScore = 1 / (1 + (pow(10,((awayTeamCR-homeTeamCR)/ 400))))
    awayTeamExpScore = 1 / (1 + (pow(10,((homeTeamCR-awayTeamCR)/ 400))))
    print("HomeTeamExpScore: " + str(homeTeamExpScore) + "       AwayTeamExpScore: " + str(awayTeamExpScore))

    return homeTeamExpScore,awayTeamExpScore

def computeMovMultiplier(elow,elol,pd):
    movMultiplier = math.log(abs(pd+1))*(2.2 / ((0.001 * (elow - elol))+2.2))

    return movMultiplier

def computeNewRatings(homeTeamCR,awayTeamCR,k,movMultiplier,homeTeamSa,awayTeamSa,homeTeamExpScore,awayTeamExpScore):
    homeTeamNR = homeTeamCR + k * movMultiplier * (homeTeamSa - homeTeamExpScore)
    awayTeamNR = awayTeamCR + k * movMultiplier * (awayTeamSa - awayTeamExpScore)

    print("HomeTeamNR: " + str(homeTeamNR) + "      AwayTeamNR: " + str(awayTeamNR))

    return homeTeamNR,awayTeamNR

def updateRatings(cursor,homeTeamNR,homeTeam,awayTeamNR,awayTeam):
    queryUpdateCurrentRanking = ("UPDATE currentrankings SET currentranking = %s WHERE id = (SELECT team_id FROM teams WHERE team_name = %s);")

    cursor.execute(queryUpdateCurrentRanking,(homeTeamNR,homeTeam))
    cursor.execute(queryUpdateCurrentRanking,(awayTeamNR,awayTeam))
    print("------------------------------------")
    
    return

def displayFinalRatings(cursor):
    queryFinalRatings = ("SELECT team_name,currentranking FROM teams JOIN currentrankings ON team_id=currentrankings.id ORDER BY currentranking DESC")
    cursor.execute(queryFinalRatings)
    finalRatingResults = cursor.fetchall()
    print("FINAL RATINGS")
    for row in finalRatingResults:
        print(row)

    return

main()
