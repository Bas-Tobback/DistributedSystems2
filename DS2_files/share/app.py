from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
import requests

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('friend')
parser.add_argument('playlist')

app = Flask("share")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="share", user="postgres", password="postgres", host="share_persistence")
        print("DB connection successful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def share_playlist(playlist_id, username):
    existing = requests.get(f"http://login:5000/login/exists?username={username}").json()

    if existing:
        if not already_shared(playlist_id, username):
            cur = conn.cursor()
            cur.execute("INSERT INTO share (playlist_id, username) VALUES (%s, %s);", (playlist_id, username))
            conn.commit()
            return True
    return False

def already_shared(playlist_id, username):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM share WHERE playlist_id = %s AND username = %s", (playlist_id, username))
    return bool(cur.fetchone()[0])

def shared_with(username):
    existing = requests.get(f"http://login:5000/login/exists?username={username}").json()

    if existing:
        cur = conn.cursor()
        cur.execute(f"SELECT playlist_id FROM share WHERE username = %s;", (username,))
        playlists = cur.fetchall()

        print(playlists, flush=True)

        shared_with_me = []

        for playlist_id in playlists:
            response = requests.get(f"http://playlist:5000/playlist/title?playlist_id={playlist_id[0]}").json()
            shared_with_me.append(response[0])

        print(shared_with_me, flush=True)
        return shared_with_me
    return []

class Share(Resource):
    def post(self):
        args = flask_request.args
        return share_playlist(args['playlist_id'], args['username'])

class SharedWith(Resource):
    def get(self):
        args = flask_request.args
        return shared_with(args['username'])

api.add_resource(Share, '/share/share')
api.add_resource(SharedWith, '/share/shared_with')