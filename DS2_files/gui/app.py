from flask import Flask, render_template, redirect, request, url_for
import requests

app = Flask(__name__)


# The Username & Password of the currently logged-in User
username = None
password = None

session_data = dict()


def save_to_session(key, value):
    session_data[key] = value


def load_from_session(key):
    return session_data.pop(key) if key in session_data else None  # Pop to ensure that it is only used once


@app.route("/")
def feed():
    # ================================
    # FEATURE 9 (feed)
    #
    # Get the feed of the last N activities of your friends.
    # ================================

    global username

    N = 10

    if username is not None:
        try:
            feed = requests.get(f"http://feed:5000/feed/get?username={username}&amount={N}").json()["data"]
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            feed = []
    else:
        feed = []

    return render_template('feed.html', username=username, password=password, feed=feed)


@app.route("/catalogue")
def catalogue():
    try:
        songs = requests.get("http://songs:5000/songs").json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        songs = []

    return render_template('catalogue.html', username=username, password=password, songs=songs)


@app.route("/login")
def login_page():

    success = load_from_session('success')
    return render_template('login.html', username=username, password=password, success=success)


@app.route("/login", methods=['POST'])
def actual_login():
    req_username, req_password = request.form['username'], request.form['password']

    # ================================
    # FEATURE 2 (login)
    #
    # send the username and password to the microservice
    # microservice returns True if correct combination, False if otherwise.
    # Also pay attention to the status code returned by the microservice.
    # ================================
    try:
        success = requests.get(f"http://login:5000/login/login?username={req_username}&password={req_password}").json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        success = False

    save_to_session('success', success)
    if success:
        global username, password

        username = req_username
        password = req_password

    return redirect('/login')


@app.route("/register")
def register_page():
    success = load_from_session('success')
    return render_template('register.html', username=username, password=password, success=success)


@app.route("/register", methods=['POST'])
def actual_register():

    req_username, req_password = request.form['username'], request.form['password']

    # ================================
    # FEATURE 1 (register)
    #
    # send the username and password to the microservice
    # microservice returns True if registration is succesful, False if otherwise.
    #
    # Registration is successful if a user with the same username doesn't exist yet.
    # ================================
    try:
        success = requests.post(f"http://login:5000/login/register?username={req_username}&password={req_password}").json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        success = False

    save_to_session('success', success)

    if success:
        global username, password

        username = req_username
        password = req_password

    return redirect('/register')


@app.route("/friends")
def friends():
    success = load_from_session('success')

    global username

    # ================================
    # FEATURE 4
    #
    # Get a list of friends for the currently logged-in user
    # ================================

    if username is None:
        friend_list = []
    else:
        try:
            friend_list = requests.get(f"http://friends:5000/friends/friends?username={username}").json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            friend_list = []

    return render_template('friends.html', username=username, password=password, success=success, friend_list=[friend[0] for friend in friend_list])


@app.route("/add_friend", methods=['POST'])
def add_friend():

    # ==============================
    # FEATURE 3
    #
    # send the username of the current user and the username of the added friend to the microservice
    # microservice returns True if the friend request is successful (the friend exists & is not already friends), False if otherwise
    # ==============================

    global username
    req_username = request.form['username']

    try:
        success = requests.post(f"http://friends:5000/friends/add?username={username}&friend={req_username}").json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        success = False

    save_to_session('success', success)

    return redirect('/friends')


@app.route('/playlists')
def playlists():
    global username

    my_playlists = []
    shared_with_me = []

    if username is not None:
        # ================================
        # FEATURE
        #
        # Get all playlists you created and all playlist that are shared with you. (list of id, title pairs)
        # ================================

        try:
            my_playlists = requests.get(f"http://playlist:5000/playlist/all?username={username}").json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            my_playlists = []

        try:
            shared_with_me = requests.get(f"http://share:5000/share/shared_with?username={username}").json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            shared_with_me = []

    return render_template('playlists.html', username=username, password=password, my_playlists=my_playlists, shared_with_me=shared_with_me)


@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    # ================================
    # FEATURE 5
    #
    # Create a playlist by sending the owner and the title to the microservice.
    # ================================
    global username
    title = request.form['title']

    try:
        requests.post(f"http://playlist:5000/playlist/create?username={username}&playlist={title}").json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pass

    return redirect('/playlists')


@app.route('/playlists/<int:playlist_id>')
def a_playlist(playlist_id):
    # ================================
    # FEATURE 7
    #
    # List all songs within a playlist
    # ================================
    try:
        songs = requests.get(f"http://playlist:5000/playlist/view?playlist_id={playlist_id}").json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        songs = []

    return render_template('a_playlist.html', username=username, password=password, songs=songs, playlist_id=playlist_id)


@app.route('/add_song_to/<int:playlist_id>', methods=["POST"])
def add_song_to_playlist(playlist_id):
    # ================================
    # FEATURE 6
    #
    # Add a song (represented by a title & artist) to a playlist (represented by an id)
    # ================================
    title, artist = request.form['title'], request.form['artist']

    try:
        requests.post(f"http://playlist:5000/playlist/add?username={username}&playlist_id={playlist_id}&artist={artist}&title={title}").json()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pass
    return redirect(f'/playlists/{playlist_id}')


@app.route('/invite_user_to/<int:playlist_id>', methods=["POST"])
def invite_user_to_playlist(playlist_id):
    # ================================
    # FEATURE 8
    #
    # Share a playlist (represented by an id) with a user.
    # ================================
    recipient = request.form['user']

    try:
        requests.post(f"http://share:5000/share/share?username={username}&playlist_id={playlist_id}&friend={recipient}")
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pass
    return redirect(f'/playlists/{playlist_id}')


@app.route("/logout")
def logout():
    global username, password

    username = None
    password = None
    return redirect('/')
