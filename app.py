from flask import Flask, flash, redirect, render_template, request, url_for, session, jsonify
from dotenv import load_dotenv
from flask_session import Session
from datetime import datetime, timedelta
import os
import requests
import json
import random


app = Flask(__name__)
app.secret_key = "secret_key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


load_dotenv()

client_id = os.getenv("CLIENT_ID")
redirect_uri = os.getenv("REDIRECT_URI")
client_secret = os.getenv("CLIENT_SECRET")
scope = "user-read-private user-read-email playlist-read-private user-read-recently-played user-top-read user-follow-read user-read-currently-playing user-read-playback-state user-modify-playback-state"


def get_user_id_and_access_token():
    access_token = session.get("access_token")
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            return user_data['id'], access_token, user_data['display_name'], user_data['images'][0]['url'], user_data['images'][1]['url'],user_data['followers']['total']
        else:
            return None

def get_followed_artists():
    access_token = session.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me/following?type=artist", headers=headers)
    if response.status_code == 200:
        fllwed_artists = response.json()
        return fllwed_artists['artists']['total']
    else:
        return None
    
def get_user_top_artists_tracks():
    access_token = session.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "time_range": "long_term",
        "limit": 50
    }
    response_artists = requests.get("https://api.spotify.com/v1/me/top/artists", params= params, headers = headers)
    response_tracks = requests.get("https://api.spotify.com/v1/me/top/tracks", params= params, headers = headers)
    if response_artists.status_code == 200 and response_tracks.status_code == 200:
        top_artists = response_artists.json()
        top_tracks = response_tracks.json()
    
        all_tracks = []
    
        for track in top_tracks['items']:
            duration_seconds = track['duration_ms'] / 1000
            duration_minutes = duration_seconds // 60
            rest_seconds = duration_seconds % 60
            rest_seconds = '0' + f"{str(rest_seconds)[0]}"
            all_tracks.append({'track_name': track['name'],
                               'artist': track['album']['artists'][0]['name'],
                               'cover_url': track['album']['images'][0]['url'],
                               'album_name': track['album']['name'],
                               'duration': f"{int(duration_minutes)}:{rest_seconds}",
                               'uri': track['uri']
                               })
        all_artists = []
        for artist in top_artists['items']:
            all_artists.append({'name': artist['name'], 
                                'cover_url': artist['images'][0]['url'],
                                'id': artist['id']
                                })
        return all_artists, all_tracks
        
def get_user_playlists(access_token, user_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    response_playlists = requests.get(f"https://api.spotify.com/v1/users/{user_id}/playlists", headers=headers)
    if response_playlists.status_code == 200:
        playlist_data = response_playlists.json()
        extract_infos = []
        user_infos = get_user_id_and_access_token()
        user_name = user_infos[2]
        user_image = user_infos[3]
        if 'items' in playlist_data:
            for item in playlist_data['items']:
                if 'images' in item and item['images'] != None:
                    extract_infos.append({
                                        'name': item['name'],
                                        'img': item['images'][0]['url'],
                                        'id': item['id'],
                                        'owner': item['owner']['display_name']
                                        })
        your_playlists = []
        liked_playlists = []
        for playlist in extract_infos:
            if playlist['owner'] == '4ndr31🐉':
                your_playlists.append(playlist)
            else:
                liked_playlists.append(playlist)
        random.shuffle(liked_playlists)
        random.shuffle(your_playlists)
        return liked_playlists, your_playlists
    else:
        return None

def get_recently_played(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "limit": 50
    }
    response_recently_played = requests.get("https://api.spotify.com/v1/me/player/recently-played", params= params, headers=headers)
    if response_recently_played.status_code == 200:
        played = response_recently_played.json()  
        recently_played = []    
        for item in played['items']:
            album_name = item['track']['album']['name']
            #print(item['track']['name'])
            cover_url = item['track']['album']['images'][0]['url']
            if 'context' in item and item['context'] is not None and 'type' in item['context']:
                if item['context']['type'] == 'playlist':
                    playlist_id = str(item['context']['uri'].split(":")[-1])
                    response_get_playlist = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}", headers=headers)
                    if response_get_playlist.status_code == 200:
                        playlist_info = response_get_playlist.json()
                        playlist_name = playlist_info['name']
                        playlist_cover = playlist_info['images'][0]['url']
                        playlist_id = playlist_info['id']
                        if not any(entry['album_playlist_name'] == playlist_name for entry in recently_played):
                            recently_played.append({'album_playlist_name': playlist_name, 
                                                    'cover': playlist_cover, 
                                                    'type': item['context']['type'],
                                                    'id': playlist_id})
                elif item['context']['type'] == 'album':
                    if item['track']['album']['album_type'] == 'album':
                        if not any(entry['album_playlist_name'] == album_name for entry in recently_played):
                            recently_played.append({'album_playlist_name': album_name, 
                                                    'cover': cover_url,  
                                                    'type': item['context']['type'],
                                                    'id': item['track']['album']['id']})
                    elif item['track']['album']['album_type'] == 'single':
                        if item['track']['album']['total_tracks'] == 1 :
                            if not any(entry['album_playlist_name'] == album_name for entry in recently_played):
                                recently_played.append({'album_playlist_name': album_name, 
                                                        'cover': cover_url,  
                                                        'type': 'track',
                                                        'id': item['track']['id']})
                        else:
                            if not any(entry['album_playlist_name'] == album_name for entry in recently_played):
                                recently_played.append({'album_playlist_name': album_name,
                                                        'cover': cover_url, 
                                                        'type': 'album',
                                                        'id': item['track']['album']['id']})
            else:
                #played['items'][0]['track']['album']['total_tracks']
                if item['track']['album']['album_type'] == 'album':
                    if not any(entry['album_playlist_name'] ==  album_name for entry in recently_played):
                        recently_played.append({'album_playlist_name': album_name,
                                                 'cover': cover_url, 
                                                 'type': item['track']['album']['album_type'],
                                                  'id': item['track']['album']['id'] })
                elif item['track']['album']['album_type'] == 'single':
                    if not any(entry['album_playlist_name'] == item['track']['name'] for entry in recently_played):
                        recently_played.append({'album_playlist_name':
                                                 item['track']['name'], 
                                                 'cover': cover_url, 
                                                 'type': item['track']['album']['album_type'],
                                                  'id': item['track']['id'] })
            
        recently_played = recently_played[:8]
        random.shuffle(recently_played)
        return recently_played
    else:
        return None

def get_playlist_data(access_token, playlist_id):
    headers = {'Authorization': f"Bearer {access_token}"}
    response_playlist_data = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}", headers=headers)
    if response_playlist_data.status_code == 200:
        playlist_data = response_playlist_data.json()
        return playlist_data
    else:
        return None

def get_album_data(access_token, album_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    response_album = requests.get(f"https://api.spotify.com/v1/albums/{album_id}", headers = headers)
    if response_album.status_code == 200:
        album_data = response_album.json()
        return album_data
    else:
        return None
    
def get_track_data(access_token, track_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    response_track = requests.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers = headers)
    if response_track.status_code == 200:
        track_data = response_track.json()
        return track_data
    else:
        return None

def get_artist_data(access_token, artist_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    response_artist = requests.get(f"https://api.spotify.com/v1/artists/{artist_id}", headers = headers)
    if response_artist.status_code == 200:
        artist_data = response_artist.json()
        return artist_data
    else:
        return None

def get_artist_top_tracks(access_token, artist_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    response_artist_tracks = requests.get(f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks", headers = headers)
    if response_artist_tracks.status_code == 200:
        artist_tracks = response_artist_tracks.json()
        return artist_tracks
    else:
        return None

@app.route("/playback-state")
def get_playback_state():
    if session:
        access_token = session['access_token']
        headers = {'Authorization': f"Bearer {access_token}"}
        response_player = requests.get(f"https://api.spotify.com/v1/me/player", headers=headers)
        if response_player.status_code == 200:
            player_data = response_player.json()
            duration_seconds = player_data['item']['duration_ms'] / 1000
            duration_minutes = duration_seconds // 60
            rest_seconds = duration_seconds % 60
            rest_seconds = str(rest_seconds)
            if rest_seconds[1] in '123456789':
                rest_seconds = rest_seconds[:2]
            else:
                rest_seconds = '0' + f"{rest_seconds[0]}"
            duration = f"{int(duration_minutes)}:{rest_seconds}"
            details = {
                        'song_name' : player_data['item']['name'],
                        'artist' : player_data['item']['artists'][0]['name'],
                        'image' : player_data['item']['album']['images'][0]['url'],
                        'is_playing' : player_data['is_playing'],
                        'duration' : duration,
                        'duration_ms': player_data['item']['duration_ms'],
                        'progress' : player_data['progress_ms']
            }
            return details
        else:
            return None
    else:
        return None
    

@app.context_processor
def get_playback_state():
    if session:
        access_token = session['access_token']
        headers = {'Authorization': f"Bearer {access_token}"}
        response_player = requests.get(f"https://api.spotify.com/v1/me/player", headers=headers)
        if response_player.status_code == 200:
            player_data = response_player.json()
            duration_seconds = player_data['item']['duration_ms'] / 1000
            duration_minutes = duration_seconds // 60
            rest_seconds = duration_seconds % 60
            rest_seconds = str(rest_seconds)
            if rest_seconds[1] in '123456789':
                rest_seconds = rest_seconds[:2]
            else:
                rest_seconds = '0' + f"{rest_seconds[0]}"
            duration = f"{int(duration_minutes)}:{rest_seconds}"
            details = {
                        'song_name' : player_data['item']['name'],
                        'artist' : player_data['item']['artists'][0]['name'],
                        'image' : player_data['item']['album']['images'][0]['url'],
                        'is_playing' : player_data['is_playing'],
                        'duration' : duration,
                        'progress' : player_data['progress_ms']
            }
            return dict(details = details)
        else:
            return dict(details = None)
    else:
        return dict(details = None)

@app.route('/play_song', methods = ['GET', 'PUT'])
def play_song():
    access_token = session['access_token']
    song_uri = request.json.get('song_uri')
    data = {'uris': [song_uri]}
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.put("https://api.spotify.com/v1/me/player/play", headers = headers, json = data)
    if response.status_code == 204:
        return jsonify({"message": "Playback has started"}), 200
    else:
        return jsonify({"error": "Error starting playback"}), response.status_code
      


@app.route('/add_queue', methods = ['GET', 'POST'])
def queue():
    access_token = session['access_token']
    song_uri = request.json.get('song_uri')
    data = {'uris': [song_uri]}
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post("https://api.spotify.com/v1/me/player/queue", headers = headers, json = data)
    if response.status_code == 204:
        return jsonify({"message": "Playback has started"}), 200
    else:
        return jsonify({"error": "Error starting playback"}), response.status_code
    
@app.route("/start", methods = ['GET','PUT'])
def start_playback():
    access_token = session['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.put("https://api.spotify.com/v1/me/player/play", headers = headers)
    if response.status_code == 204:
        return "Playback has started"
    else:
        return "Error starting playback"
    
@app.route("/pause", methods = ['GET','PUT'])
def pause_playback():
    access_token = session['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.put("https://api.spotify.com/v1/me/player/pause", headers = headers)    
    if response.status_code == 204:
        return "Playback has been paused"
    else:
        return "Error pausing playback"
    
@app.route("/skipnext", methods = ['GET','POST'])
def skipnext_playback():
    access_token = session['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post("https://api.spotify.com/v1/me/player/next", headers = headers)
    if response.status_code == 204:
        return "Playback has been skipped to the next song"
    else:
        return "Error skipping playback"


@app.route("/skipprevious", methods = ['GET','POST'])
def skipprevious_playback():
    access_token = session['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post("https://api.spotify.com/v1/me/player/previous", headers = headers)
    if response.status_code == 204:
        return "Playback has been skipped to the previous song"
    else:
        return "Error skipping playback"
    

@app.route("/login")
def login():
    authorization_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope,
        "prompt": "login"
    }

    return redirect(authorization_url + "?" + "&".join([f"{key}={value}" for key, value in params.items()]))



@app.route("/callback")
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
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            session["access_token"] = access_token
            session["refresh_token"] = refresh_token
            session["token_expire_at"] = datetime.now() + timedelta(seconds = token_data["expires_in"])
            #session['token_expire_at'] = datetime.now() + timedelta(seconds = 10)
            #print(session['token_expire_at'])
            return redirect("/home")
    else:
            return "Error: Unable to authenticate user"


@app.route("/refresh_token")
def refresh_token():
    refresh_token = session.get("refresh_token")
    if refresh_token:
        token_url = "https://accounts.spotify.com/api/token"
        data = { 
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret
        }

        response_refresh = requests.post(token_url, data = data)
        if response_refresh.status_code == 200:
            refresh_token_data = response_refresh.json()
            access_token = refresh_token_data['access_token']
            session['access_token'] = access_token
            session['token_expire_at'] = datetime.now() + timedelta(seconds = refresh_token_data["expires_in"])
            #session['token_expire_at'] = datetime.now() + timedelta(seconds = 10)
            #print("TOKEN HAS BEEN REFRESHED")
            return redirect(session['route'])
    return None


@app.route("/home")
def home():
    if 'access_token' not in session:
        redirect('/')
    
    session['route'] = request.path
    if datetime.now() >  session['token_expire_at']:
        #print("TOKEN EXPIRED.")
        return redirect("/refresh_token")
    
    access_token = session['access_token']

    user_infos = get_user_id_and_access_token()
    
    #return jsonify(user_infos)
    user_id = user_infos[0]
    if access_token:
        if user_id:
            return get_data_home_template(access_token, user_id)
        else:
            return "Error: Unable to retrieve user ID"
    else:
        return redirect("/login")
        
    
def get_data_home_template(access_token, user_id):
    user_infos = get_user_id_and_access_token()
    user_name = user_infos[2]
    user_image = user_infos[3]
    liked_playlists, your_playlists = get_user_playlists(access_token, user_id)  
    recently_played = get_recently_played(access_token)
    #return json.loads(played)['items'][0]['track']['album']['images'][2]['url']
    return render_template("home.html", liked_playlists = liked_playlists[:6], your_playlists = your_playlists[:6], username = user_name, profile_pic = user_image, recently_info = recently_played)
    

@app.route("/userprofile")
def userprofile():
    if 'access_token' not in session:
        redirect('/')
    
    session['route'] = request.path
    if datetime.now() >  session['token_expire_at']:
        return redirect("/refresh_token")
    
    user_infos = get_user_id_and_access_token()
    user_name = user_infos[2]
    user_img_bigger =  user_infos[4]
    #access_token = user_infos[1]
    nr_followers = user_infos[5]

    top_artists, top_tracks =  get_user_top_artists_tracks()
    nr_following = get_followed_artists()
    
    return render_template("userprofile.html", username = user_name, profile_pic = user_img_bigger, top_artists = top_artists[:5], top_tracks = top_tracks[:5], followers = nr_followers, following = nr_following)

@app.route("/see-all")
def see_all():
    if 'access_token' not in session:
        redirect('/')
    
    session['route'] = request.path
    if datetime.now() >  session['token_expire_at']:
        return redirect("/refresh_token")
    
    user_profile = get_user_id_and_access_token()
    user_name = user_profile[2]
    user_img = user_profile[3]
    access_token = user_profile[1]
    user_id = user_profile[0]
    user_top = get_user_top_artists_tracks()
    user_playlists = get_user_playlists(access_token, user_id)
    category = request.args.get('category')
    if category == 'tracks':
        see_all_item = user_top[1]
        title = 'Top Tracks'
    elif category == 'artists':
        see_all_item = user_top[0]
        title = 'Top Artists'
    elif category == 'your-playlists':
        see_all_item = user_playlists[1]
        title = 'Your Playlists'
    elif category == 'liked-playlists':
        see_all_item = user_playlists[0]
        title = 'Liked Playlists'
    return render_template("see_all.html", category = category, data = see_all_item, title = title, username = user_name, profile_pic = user_img )

@app.route("/<profile_type>/<id>")
def object_profile(profile_type, id):
    if 'access_token' not in session:
        redirect('/')
    
    session['route'] = request.path
    if datetime.now() >  session['token_expire_at']:
        return redirect("/refresh_token")
      
    user_profile = get_user_id_and_access_token() 
    user_id = user_profile[0]
    access_token = user_profile[1]
    user_name = user_profile[2]
    user_img = user_profile[3]

    if profile_type == 'single':
        track_info = get_track_data(access_token, id)
        if len(track_info['artists']) > 1:
            all_artists = []
            for artist in track_info['artists']:
                all_artists.append(artist['name'])
                owner = " • ".join(all_artists)
        else:
            owner = track_info['artists'][0]['name']

        track_img = track_info['album']['images'][0]['url']
        track_name = track_info['name']
        track_uri = track_info['uri']
        duration_seconds = track_info['duration_ms'] / 1000
        duration_minutes = duration_seconds // 60
        rest_seconds = duration_seconds % 60
        rest_seconds = str(rest_seconds)
        if rest_seconds[1] in '123456789':
            rest_seconds = rest_seconds[:2]
        else:
            rest_seconds = '0' + f"{rest_seconds[0]}"
        duration = f"{int(duration_minutes)} min, {rest_seconds} sec"
        return render_template("objectprofile.html",uri = track_uri, duration = duration, username = user_name, profile_pic = user_img, profile_type = profile_type, owner = owner, cover = track_img, name = track_name)

    elif profile_type == 'album':
        album_info = get_album_data(access_token, id)
        
        owner = album_info['artists'][0]['name']
        album_img = album_info['images'][0]['url']
        album_name = album_info['name']
        album_uri= album_info['uri']
        release_date = album_info['release_date']
        songs = []
        contor = 0
        album_duration = 0
        for track in album_info['tracks']['items']:
            track_id = track['id']
            track_info = get_track_data(access_token, track_id)
            duration_seconds = track_info['duration_ms'] / 1000
            duration_minutes = duration_seconds // 60
            rest_seconds = duration_seconds % 60
            rest_seconds = str(rest_seconds)
            if rest_seconds[1] in '123456789':
                rest_seconds = rest_seconds[:2]
            else:
                rest_seconds = '0' + f"{rest_seconds[0]}"
            songs.append({
                'name': track['name'],
                'owner': track['artists'][0]['name'],
                'cover': album_img,
                'duration': f"{int(duration_minutes)}:{rest_seconds}",
                'uri': track['uri']
            })
            contor += 1
            album_duration += track_info['duration_ms']

        if album_duration > 3600000:
            converted_duration = album_duration / (1000 * 60 * 60)
            info = f"{contor} songs, about {int(converted_duration)} hr"
        else:
            secs = album_duration / 1000
            mins = secs // 60
            rest_secs = secs % 60
            rest_secs = '0' + f"{str(rest_secs)[0]}"
            info = f"{contor} songs, {int(mins)} min, {rest_secs} sec"
                
        return render_template("objectprofile.html", object_info = info, username = user_name, profile_pic = user_img, profile_type = profile_type, songs = songs, owner = owner, cover = album_img, name = album_name, release = release_date,album_uri = album_uri)
    
    elif profile_type == 'playlist':
        playlist_info = get_playlist_data(access_token, id)
        playlist_name = playlist_info['name']
        playlist_img = playlist_info['images'][0]['url']
    
        owner = playlist_info['owner']['display_name']
        songs = []
        songs_uris = []
        contor = 0
        playlist_duration = 0
        for song in playlist_info['tracks']['items']:
            if song['track']['album']['images'] and song['track']['name'] and song['track']['artists'] and song['track']['album']['name']:
                track_id = song['track']['id']
                track = get_track_data(access_token, track_id)
                duration_seconds = track['duration_ms'] / 1000
                duration_minutes = duration_seconds // 60
                rest_seconds = duration_seconds % 60
                rest_seconds = str(rest_seconds)
                if rest_seconds[1] in '123456789':
                    rest_seconds = rest_seconds[:2]
                else:
                    rest_seconds = '0' + f"{rest_seconds[0]}"

                songs.append({
                    'name': song['track']['name'],
                    'artist': song['track']['artists'][0]['name'],
                    'album': song['track']['album']['name'],
                    'cover': song['track']['album']['images'][0]['url'],
                    'duration': f"{int(duration_minutes)}:{rest_seconds}",
                    'uri': song['track']['uri']
                })

                contor += 1
                playlist_duration += track['duration_ms']
                
            else:
                continue

    
        if playlist_duration > 3600000:
            converted_duration = playlist_duration / (1000 * 60 * 60)
            info = f"{contor} songs, about {int(converted_duration)} hr"
        else:
            secs = playlist_duration / 1000
            mins = secs // 60
            rest_secs = secs % 60
            rest_secs = '0' + f"{str(rest_secs)[0]}"
            info = f"{contor} songs, {int(mins)} min, {rest_secs} sec"

        return render_template("objectprofile.html", object_info = info,  username = user_name, profile_pic = user_img, profile_type = profile_type, name = playlist_name, cover = playlist_img, owner = owner, songs = songs)
    
    elif profile_type == 'artist':
        artist_data = get_artist_data(access_token, id)
        name = artist_data['name']
        image = artist_data['images'][0]['url']
        artist_top_tracks = get_artist_top_tracks(access_token, id)
       
        all_artists_top = []
        for track in artist_top_tracks['tracks']:
            duration_seconds = track['duration_ms'] / 1000
            duration_minutes = duration_seconds // 60
            rest_seconds = duration_seconds % 60
            rest_seconds = str(rest_seconds)
            if rest_seconds[1] in '123456789':
                rest_seconds = rest_seconds[:2]
            else:
                rest_seconds = '0' + f"{rest_seconds[0]}"
            duration = f"{int(duration_minutes)}:{rest_seconds}"
            all_artists_top.append({
                    'song_name': track['name'],
                    'img': track['album']['images'][0]['url'],
                    'duration': duration,
                    'album': track['album']['name'],
                    'uri': track['uri']
            })
            

        return render_template("objectprofile.html", profile_type = profile_type, username = user_name, profile_pic = user_img, name = name, image = image, all_tracks = all_artists_top)
            

@app.route("/")
def index():
    if 'access_token' not in session:
        return render_template("index.html")
    else:  
        return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    #sau session.pop('acces_token', None)
    return redirect("/")







if __name__ == "__main__":
    app.run(debug = True)







