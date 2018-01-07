from flask import Flask, jsonify
import psycopg2, json
import datetime

app = Flask(__name__)

conn = psycopg2.connect("host=0.0.0.0 dbname=tennis user=postgres password=pwd")
cur = conn.cursor()

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

@app.route('/tennis/players/<int:player_id>', methods=['GET'])
def get_player(player_id):
    selectStatement = "SELECT * FROM player.match where player1_id = %(id)s or player2_id = %(id)s"
    cur.execute(selectStatement, {'id' : player_id})
    result = cur.fetchall();
    columns = ['home', 'away', 'sets_home', 'sets_away', 'tournament_id', 'surface', 'date', 'winner', 'round']
    players = []
    for row in result:
        players.append(dict(zip(columns, row)))

    return json.dumps(players, indent=4, sort_keys=True, default=str)

if __name__ == '__main__':
    app.run(port=5002)