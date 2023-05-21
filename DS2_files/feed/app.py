import datetime

from flask import Flask, jsonify, make_response
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
import requests

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('activity')
parser.add_argument('amount')

app = Flask("feed")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="feed", user="postgres", password="postgres", host="feed_persistence")
        print("DB connection successful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def add_activity(username, activity):
    cur = conn.cursor()
    time = datetime.datetime.now()
    cur.execute(f"INSERT INTO feed (username, activity, activity_time) values (%s, %s, %s);", (username, activity, time))
    return True

def get_feed(username, amount):
    cur = conn.cursor()
    cur.execute(f"SELECT username, activity, activity_time FROM feed WHERE username = %s ORDER BY activity_time DESC LIMIT %s;", (username, amount))
    temp = cur.fetchall()
    # return make_response(jsonify({"message" : "ok", "feed": temp}), 200)
    temp_dict = jsonify({"data" : temp})
    return temp_dict
class AddToFeed(Resource):
    def post(self):
        args = flask_request.args
        return add_activity(args['username'], args['activity'])

class GetFeed(Resource):
    def get(self):
        args = flask_request.args
        temp = get_feed(args['username'], args['amount'])
        return temp

api.add_resource(AddToFeed, '/feed/add')
api.add_resource(GetFeed, '/feed/get')
