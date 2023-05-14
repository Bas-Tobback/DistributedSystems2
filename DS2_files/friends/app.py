from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('friend')

app = Flask("friends")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="friends", user="postgres", password="postgres", host="friends_persistence")
        print("DB connection successful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def add_friend(username, friend):
    if friend not in all_friends(username):
        cur = conn.cursor()
        cur.execute("INSERT INTO friends (username, friend) VALUES (%s, %s);", (username, friend))
        conn.commit()
        return True
    return False

def all_friends(username):
    cur = conn.cursor()
    cur.execute(f"SELECT friend FROM friends WHERE username = {username};")
    return cur.fetchall()

class Add(Resource):
    def put(self):
        args = flask_request.args
        return add_friend(args['username'], args['friend'])

class Friends(Resource):
    def get(self):
        args = flask_request.args
        return all_friends(args['username'])

api.add_resource(Add, '/friends/add')
api.add_resource(Friends, '/friends/friends')