#!/usr/bin/python

import urllib, json, datetime

url = "https://www.sofascore.com/football//2017-11-03/json"
print url
response = urllib.urlopen(url)
data = json.loads(response.read())

events = []
lg={}
matches = []

for tournament in data["sportItem"]["tournaments"]:

    for event in tournament["events"]:
        if ("odds" in event and event["odds"] != "" and event["status"]["code"] == 0):

            match = {}

            homeID = event["homeTeam"]["id"]
            awayID = event["awayTeam"]["id"]

            odds = event["odds"]

            if (tournament["season"] is None):
                continue
            seasonID = str(tournament["season"]["id"])
            leagueID = str(tournament["tournament"]["id"])
            leagueURL="https://www.sofascore.com/tournament/" +leagueID+"/"+seasonID+"/standings/tables/json"

            if leagueID not in lg:
                leagueResponse = urllib.urlopen(leagueURL)
                leaguedata = json.loads(leagueResponse.read())
                lg[leagueID] = leaguedata
                print "Analyzing league " + tournament["tournament"]["name"]
            else:
                leaguedata = lg[leagueID]



            if "standingsTables" in leaguedata and len(leaguedata["standingsTables"]) > 0 \
                    and (datetime.datetime.fromtimestamp(int(event["startTimestamp"])).date() == (datetime.datetime.today().date())):

                table = leaguedata["standingsTables"][0]
                jornada = table["round"]
                if jornada > 7:
                    for team in table["tableRows"]:
                        if team["team"]["id"] == homeID:
                            homeTeam = team
                        else:
                            if team["team"]["id"] == awayID:
                                awayTeam = team

                    homeOdds = odds["fullTimeOdds"]["regular"]["1"]["decimalValue"]
                    awayOdds = odds["fullTimeOdds"]["regular"]["2"]["decimalValue"]

                    if ((int(homeTeam["homePoints"]) > (int(awayTeam["awayPoints"]) + int(jornada/2))) and float(homeOdds) > 1.8) \
                            or ((int(awayTeam["awayPoints"]) > (int(homeTeam["homePoints"]) + int(jornada/4))) and float(awayOdds) > 1.8):
                        match["tournament"] = tournament["tournament"]["name"] + " - " + str(tournament["tournament"]["id"])
                        match["date"] = "Match day " + str(jornada)
                        match["homeTeam"] = "Home team: " +event["homeTeam"]["name"]
                        match["awayTeam"] = "Away team: " +event["awayTeam"]["name"]
                        match["homePoints"] = "Home points: " +homeTeam["homePoints"]
                        match["awayPoints"] = "Away points: " + awayTeam["awayPoints"]
                        match["homeOdds"] = "Home odds: " + str(homeOdds)
                        match["awayOdds"] = "Away odds: " + str(awayOdds)
                        match["start"] = int(event["startTimestamp"])
                        events.append(event)
                        matches.append(match)


sortedMatches = sorted(matches, key=lambda m: m["start"])

for match in sortedMatches:
    print match["tournament"]
    print match["date"]
    print match["homeTeam"]
    print match["awayTeam"]
    print match["homePoints"]
    print match["awayPoints"]
    print match["homeOdds"]
    print match["awayOdds"]
    print "Start time: " +  str(datetime.datetime.fromtimestamp(
        int(match["start"])
    ).strftime('%Y-%m-%d %H:%M:%S'))
    print "-----------------"



print str(len(events)) + " matches for today";