from flask import Flask, redirect, request, session, jsonify, url_for
from dotenv import load_dotenv
import os
import requests

app1 = Flask(__name__)
app1.secret_key = "SECRET_KEY"

load_dotenv()


client_id = os.getenv("CLIENT_ID")
redirect_uri = os.getenv("REDIRECT_URI")
client_secret = os.getenv("CLIENT_SECRET")
scope = "user-read-private user-read-email playlist-read-private user-read-recently-played user-follow-read user-read-currently-playing user-top-read"

@app1.route("/")
def index():
    return "This is the link: <a href = '/login' >LINK TO SPOTIFY</a>"


@app1.route("/login")
def login():
    authorization_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope
    }

    return redirect(authorization_url + "?" + "&".join([f"{key}={value}" for key, value in params.items()]))

@app1.route("/callback")
def callback():
    code = request.args.get("code")
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(token_url, data= data)
    if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            session["access_token"] = access_token
 # Store access token in session
            return redirect("/getdata")
    else:
            return "Error: Unable to authenticate user"

@app1.route("/getdata")
def get_data():
    access_token = session.get("access_token")
    print(access_token)
    if access_token:
        # Retrieve user ID
        user_id = get_user_id(access_token)
        if user_id:
            # Retrieve user's playlists
            user_playlists = get_user_playlists(access_token, user_id)
            fllw_artists = followed_artists(access_token)
            currently = get_currently_played(access_token)
            top_artists = get_user_top_artists(access_token)
            top_tracks = get_user_top_tracks(access_token)
            user = get_userprofile(access_token)
            return jsonify(user) 
        else:
            return "Error: Unable to retrieve user ID"
    else:
        return redirect("/login")

def get_user_id(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data.get("id")
    else:
        return None

def get_userprofile(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me/following?type=artist", headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data['artists']['total']
    else:
        return None
    
def get_user_playlists(access_token, user_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"https://api.spotify.com/v1/users/{user_id}/playlists", headers=headers)
    if response.status_code == 200:
        playlists_data = response.json()
        """
        playlists = playlists_data.get("items", [])
        return [{playlist['id']: playlist['name']} for playlist in playlists[:2]] 
        """
        return playlists_data.get("items", [])
    else:
        return None
    

def get_currently_played(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)
    if response.status_code == 200:
        currently_played = response.json()
        return currently_played
    else:
        return None

def followed_artists(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me/following", headers=headers)
    if response.status_code == 200:
        artists = response.json()
        return artists
    else:
        return None
    
def get_user_top_artists(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "time_range": "long_term"
    }
    response = requests.get("https://api.spotify.com/v1/me/top/artists", params= params, headers = headers)
    if response.status_code == 200:
        top_artist = response.json()
        return top_artist
        #return top_artist['items'][1]['images'][0]['url']

def get_user_top_tracks(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "time_range": "long_term"
    }
    response = requests.get("https://api.spotify.com/v1/me/top/tracks", params= params, headers = headers)
    if response.status_code == 200:
        top_tracks = response.json()
        #return top_tracks['items'][1]['artists'][0]['name']
        return top_tracks['items'][0]        

if __name__ == "__main__":
    app1.run(debug = True)


