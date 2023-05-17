from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
import requests

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('playlist')
parser.add_argument('artist')
parser.add_argument('title')
parser.add_argument('playlist_id')

app = Flask("playlist")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="playlist", user="postgres", password="postgres", host="playlist_persistence")
        print("DB connection successful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

""" 
Get the entire playlist of a certain user 
:param: username : string that is the name of logged in user that wants to make the playlist
:param: playlist : name of the playlist in string format
:return: list of songs
"""
def get_playlist(playlist_id):
    cur = conn.cursor()
    cur.execute(f"SELECT title, artist FROM playlist_songs WHERE playlist_id = %s;", (playlist_id,))
    return cur.fetchall()

"""
If the playlist does not yet exist, make a new table for the playlist.
:param: username : string that is the name of logged in user that wants to make the playlist
:param: playlist : name of the playlist in string format
:return: boolean that indicates if the playlist is created or not
"""
def make_playlist(username, playlist):
    if not playlist_exists(username, playlist):
        cur = conn.cursor()
        cur.execute("INSERT INTO playlist (username, playlist) VALUES (%s, %s);", (username, playlist))
        conn.commit()
        return True
    return False

def add_to_playlist(playlist_id, artist, title):
        # check if the songs exists
    existing = requests.get(f"http://songs:5000/songs/exist?title={title}&artist={artist}")
    if existing:
        cur = conn.cursor()
        cur.execute("INSERT INTO playlist_songs (playlist_id, artist, title) VALUES (%s, %s, %s);", (playlist_id, artist, title))
        conn.commit()
        return True
    return False

"""
check if a playlist exists. If this exists it cannot be made
:param: username : string of user of which the playlist should be
:param: playlist : name of the playlist
:return: boolean that indicates if the playlist exists
"""
def playlist_exists(username, playlist):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM playlist WHERE username = %s AND playlist = %s;", (username, playlist))
    return bool(cur.fetchone()[0])  # Either True or False

def get_all_playlists(username):
    cur = conn.cursor()
    cur.execute("SELECT playlist_id, playlist FROM playlist WHERE username = %s;", (username,))
    return cur.fetchall()

def get_id_title(playlist_id):
    cur = conn.cursor()
    cur.execute("SELECT playlist_id, playlist FROM playlist WHERE playlist_id = %s", (playlist_id,))
    return cur.fetchall()

class Create(Resource):
    def post(self):
        args = flask_request.args
        return make_playlist(args['username'], args['playlist'])

class Add(Resource):
    def post(self):
        args = flask_request.args
        return add_to_playlist(args['playlist_id'], args['artist'], args['title'])

class ViewPlaylist(Resource):
    def get(self):
        args = flask_request.args
        return get_playlist(args['playlist_id'])

class AllPlaylists(Resource):
    def get(self):
        args = flask_request.args
        return get_all_playlists(args['username'])

class GetIdTitle(Resource):
    def get(self):
        args = flask_request.args
        return get_id_title(args['playlist_id'])

api.add_resource(Create, '/playlist/create')
api.add_resource(Add, '/playlist/add')
api.add_resource(ViewPlaylist, '/playlist/view')
api.add_resource(AllPlaylists, '/playlist/all')
api.add_resource(GetIdTitle, '/playlist/title')