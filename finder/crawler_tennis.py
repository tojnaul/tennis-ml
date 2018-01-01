#!/usr/bin/python

import urllib, json, psycopg2, datetime

i = 663;
while (i < 1000):
    date = datetime.datetime.today().date() - datetime.timedelta(days=i);
    i = i+1;
    print str(datetime.datetime.utcnow()) + " - " + str(date) + " - " + str(i);
    url = "https://www.sofascore.com/tennis//"+str(date)+"/json?_=150637836"
    # print url
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    conn = psycopg2.connect("host=0.0.0.0 dbname=tennis user=postgres password=pwd")
    cur = conn.cursor()

    tournaments = {}
    try:
        for tournament in data["sportItem"]["tournaments"]:
            # print "Tournament: " + tournament["tournament"]["name"]

            if tournament["season"] == "" or tournament["season"] == None:
                continue

            if "uniqueId" in tournament["tournament"]:
                tournamentId = tournament["tournament"]["uniqueId"]
                tournamentSeason = tournament["season"]["id"]
                tournamentUrl = "https://www.sofascore.com/u-tournament/"+str(tournamentId)+"/season/"+str(tournamentSeason)+"/json?_=150637874"
                normal = True
            else:
                tournamentId = tournament["tournament"]["id"]
                tournamentSeason = tournament["season"]["id"]
                tournamentUrl = "https://www.sofascore.com/tournament/"+str(tournamentId)+"/"+str(tournamentSeason)+"/standings/json?_=150654972"
                normal = False

            # print tournamentUrl
            responseTournament = urllib.urlopen(tournamentUrl)
            dataTournament = json.loads(responseTournament.read())

            if normal:
                if dataTournament["tournamentInfo"] != None and \
                                "tennisTournamentInfo" in dataTournament["tournamentInfo"] and \
                                "info" in dataTournament["tournamentInfo"]["tennisTournamentInfo"] and \
                                dataTournament["tournamentInfo"]["tennisTournamentInfo"]["info"] != None:
                    for info in dataTournament["tournamentInfo"]["tennisTournamentInfo"]:
                        if info["name"] == "Ground type":
                            tournaments[str(tournamentId)] = info["value"]

            if str(tournamentId) not in tournaments:
                tournaments[str(tournamentId)] = "NA"

            if "tournamentInfo" in dataTournament and dataTournament["tournamentInfo"] != None and "host" in dataTournament["tournamentInfo"]:
                    country = dataTournament["tournamentInfo"]["host"]["country"]
            else:
                country = "NA"
            if "uniqueTournament" in dataTournament:
                name = dataTournament["uniqueTournament"]["name"]
                id = dataTournament["uniqueTournament"]["id"]
            else:
                name =  dataTournament["tournament"]["name"]
                id = dataTournament["tournament"]["id"]

            tournamentMatch = {
                'name' : name,
                'country' : country,
                'surface' : tournaments[str(tournamentId)][:2],
                'id' : id,
                'season' : dataTournament["season"]["id"]
                }

            selectStatement = "SELECT count(*) FROM player.tournament where id = %(id)s and season = %(season)s"
            select = cur.execute(selectStatement, tournamentMatch)
            # print selectStatement
            # print tournamentMatch
            result = cur.fetchone()

            if (result[0] == 0):
                insertstatement = "INSERT INTO player.tournament (id, season, \"Name\", country, surface) " \
                                  "values(%(id)s, %(season)s, %(name)s, %(country)s, %(surface)s)"
                # values = str(event["homeTeam"]["id"]) + ","+str(event["awayTeam"]["id"]) + \
                #          ", array"+str(homeScore)+", array"+str(awayScore)+","+ str(tournamentId) + ",'cl','"+str(datetime.datetime.now())+"', 1, 'R16'"
                # print insertstatement;
                cur.execute(insertstatement,tournamentMatch)

            selectStatement = "SELECT id_local FROM player.tournament where id = %(id)s and season = %(season)s"
            cur.execute(selectStatement, tournamentMatch)
            result = cur.fetchone()
            tournamentLocalId = result[0]


            for event in tournament["events"]:
                if "/" not in event["homeTeam"]["name"] and event["status"]["type"] == "finished" and "winnerCode" in event:
                    # print event["homeTeam"]["name"] + " vs " + event["awayTeam"]["name"]

                    player1 = {
                        'id' : event["homeTeam"]["id"],
                        'name' : event["homeTeam"]["name"]
                    }
                    player2 = {
                        'id' : event["awayTeam"]["id"],
                        'name' : event["awayTeam"]["name"]
                    }

                    selectStatement = "SELECT count(*) FROM player.player where id = %(id)s"
                    select = cur.execute(selectStatement, player1)
                    result = cur.fetchone()

                    if (result[0] == 0):
                        insertstatement = "INSERT INTO player.player (id, Name) " \
                                          "values(%(id)s, %(name)s)"
                        cur.execute(insertstatement,player1)

                    selectStatement = "SELECT count(*) FROM player.player where id = %(id)s"
                    select = cur.execute(selectStatement, player2)
                    result = cur.fetchone()

                    if (result[0] == 0):
                        insertstatement = "INSERT INTO player.player (id, Name) " \
                                          "values(%(id)s, %(name)s)"
                        cur.execute(insertstatement,player2)

                    homeScore = []
                    awayScore = []
                    for key in event["homeScore"]:
                        if "period" in key and "TieBreak" not in key:
                            homeScore.append(event["homeScore"][key])

                    for key in event["awayScore"]:
                        if "period" in key and "TieBreak" not in key:
                            awayScore.append(event["awayScore"][key])

                    # print homeScore
                    # print awayScore

                    # print event["homeTeam"]["name"]

                    if "roundInfo" in event:
                        round = event["roundInfo"]["name"]
                    else:
                        round = "NA"

                    playerMatch = {
                        'player1_id' : str(player1["id"]),
                        'player2_id' : str(player2["id"]),
                        'player1sets' : homeScore,
                        'player2sets' : awayScore,
                        'tournament_id' : str(tournamentLocalId),
                        'surface' : tournaments[str(tournamentId)][:2],
                        'date' : str(datetime.datetime.fromtimestamp(int(event["startTimestamp"])).date()),
                        'winner' : int(event["winnerCode"]),
                        'round' : round
                    }

                    selectStatement = "SELECT count(*) FROM player.match where player1_id = %(player1_id)s and " \
                                      "player2_id = %(player2_id)s and date = %(date)s"
                    select = cur.execute(selectStatement, playerMatch)
                    result = cur.fetchone()

                    if (result[0] == 0):
                        insertstatement = "INSERT INTO player.match values(%(player1_id)s, %(player2_id)s, %(player1sets)s, " \
                                          "%(player2sets)s, %(tournament_id)s, %(surface)s, %(date)s, %(winner)s, %(round)s)"
                        cur.execute(insertstatement,playerMatch)

    finally:
        conn.commit()
        conn.close()

