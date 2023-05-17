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

""" 
check if the login exists, check the database for an entry with matching username and password
:param: username : string, name of user
:param: password : string, password of user
:return: boolean that indicates if the username-password combination is registered
"""
def login(username, password):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM login WHERE username = %s AND password = %s;", (username, password))
    return bool(cur.fetchone()[0])  # Either True or False

"""
check if the username is present in the registered users
:param: username : string, name of the user 
:return: boolean indicating if the user exists
"""
def login_exists(username):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM login WHERE username = %s;", (username,))
    return bool(cur.fetchone()[0])  # Either True or False

""" 
register a new user 
:param: username : string, name of user
:param: password : string, password of user
:return: boolean that indicates if the username-password combination is registered
"""
def register(username, password):
    if not login_exists(username):
        cur = conn.cursor()
        cur.execute("INSERT INTO login (username, password) VALUES (%s, %s);", (username, password))
        conn.commit()
        return True
    return False

class Register(Resource):
    """ register a new user, this will only do this if the user does not yet exist """
    def post(self):
        args = flask_request.args
        return register(args['username'], args['password'])

class Login(Resource):
    """ check if the user exists or not """
    def get(self):
        args = flask_request.args
        return login(args['username'], args['password'])

class Exists(Resource):
    def get(self):
        args = flask_request.args
        return login_exists(args['username'])

api.add_resource(Register, '/login/register')
api.add_resource(Login, '/login/login')
api.add_resource(Exists, '/login/exists')