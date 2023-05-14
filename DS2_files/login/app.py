from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('password')

app = Flask("login")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="login", user="postgres", password="postgres", host="login_persistence")
        print("DB connection successful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def login_exists(username, password):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM login (WHERE username = %s AND password = %s);", (username, password))
    return bool(cur.fetchone()[0])  # Either True or False

def register(username, password):
    if not login_exists(username, password):
        cur = conn.cursor()
        cur.execute("INSERT INTO login (username, password) VALUES (%s, %s);", (username, password))
        conn.commit()
        return True
    return False

class Register(Resource):
    def post(self):
        args = flask_request.args
        return register(args['username'], args['password'])

class Login(Resource):
    def get(self):
        args = flask_request.args
        return login_exists(args['username'], args['password'])

api.add_resource(Register, '/login/register')
api.add_resource(Login, '/login/login')