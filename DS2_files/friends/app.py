from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
import requests

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
    # print("test 1", flush=True)
    if (friend,) not in all_friends(username):

        existing = False

        # we need to be sure that if the other microservice is not up, we can still continue with our application
        try:
            existing = requests.get(f"http://login:5000/login/exists?username={friend}").json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass
        # print(existing, flush=True)

        if existing:
            # print("test 3", flush=True)
            cur = conn.cursor()
            cur.execute("INSERT INTO friends (username, friend) VALUES (%s, %s);", (username, friend))
            conn.commit()

            # we made a friend, we want to send this to the feed to remember this awesome moment forever
            try:
                activity = f"You have made a new friend: '{friend}'"
                requests.post(f"http://feed:5000/feed/add?username={username}&activity={activity}")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                pass

            return True
    return False


def all_friends(username):
    cur = conn.cursor()
    cur.execute(f"SELECT friend FROM friends WHERE username = %s;", (username,))
    return cur.fetchall()

class Add(Resource):
    def post(self):
        args = flask_request.args
        return add_friend(args['username'], args['friend'])

class Friends(Resource):
    def get(self):
        args = flask_request.args
        return all_friends(args['username'])

api.add_resource(Add, '/friends/add')
api.add_resource(Friends, '/friends/friends')