import urllib, json

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
testdb = client.test

tournamentssource = testdb.tournaments3
tournamentsoutput = testdb.tournaments4

unwind = "$sportItem.tournaments.events"

limit = 1000;
offset = 0;
# rest = list(tournamentssource.aggregate( [ { "$unwind" : unwind }, {"$limit" : offset}]))

rest = list(tournamentssource.find({}).limit(offset))

for r in rest:
    id = r["sportItem"]["tournaments"]["events"]["id"]
    url = "http://www.sofascore.com/event/" + str(id) + "/json?"
    print url
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    r["eventInfo"] = data

    client = MongoClient("mongodb://localhost:27017")
    db = client.test

    result = tournamentsoutput.insert_one(r)

while len(rest) > 0:

    offset = offset + limit;

    print "length : " + str(len(rest))
    print "offset : " + str(offset)
    # rest = list(tournamentssource.aggregate( [
    #     { "$unwind" : unwind },
    #     {"$skip" : offset},
    #     {"$limit" : 5000}
    # ]))
    rest = list(tournamentssource.find({}).skip(offset).limit(limit))

    for r in rest:
        print r["sportItem"]["tournaments"]["events"]["id"]


