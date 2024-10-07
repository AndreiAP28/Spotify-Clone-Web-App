from dotenv import load_dotenv
import base64
import json
import os
import requests 


load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")



def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers= {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result=json.loads(result.content)
    token = json_result["access_token"]
    return token


print(get_token())

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

# requestting for the id of an artist
def search_for_artist(token, artist_name):
    url ="https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = requests.get(query_url, headers=headers)
    json_result=json.loads(result.content)['artists']['items'][0]['id']

    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    
    return json_result

    #return json.dumps(json_result, indent = 4)


#using the previous id get his infos
def get_artist_info(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = get_auth_header(token)
    result = requests.get(url, headers = headers)
    json_result = json.loads(result.content)
    print(json.dumps(json_result, indent = 4))

#as previous but get his top songs
def get_songs(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = requests.get(url, headers = headers)
    json_result = json.loads(result.content)['tracks'][8] #without this specific iteration, thats just an example

    print(json.dumps(json_result, indent = 4))

#as previous, using id of the searched artist, print his albums
def get_albums(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?country=US"
    headers = get_auth_header(token)
    result = requests.get(url, headers = headers)
    json_result = json.loads(result.content)

    print(json.dumps(json_result, indent = 4))


playlist_id = "3GXQN0pEToHiJYmevwZIvO"
def get_playlist(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = get_auth_header(token)
    result = requests.get(url, headers = headers)
    json_result = json.loads(result.content)
    print(json.dumps(json_result, indent = 4))

def get_user_top_items(token):
    url = f"https://api.spotify.com/v1/me/top/artists"
    headers = get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    print(json.dumps(json_result, indent = 4))

token = get_token()
"""
artist_id = search_for_artist(token, "Travis Scott")
get_artist_info(token, artist_id)
print("---------------------------------------------------\n\n\n\n\n\n")
get_songs(token, artist_id)
print("------------------------------------\n\n\n\n\n\n\n")
get_albums(token, artist_id)
print("------------------------\n\n\n\n\n")
"""
get_playlist(token, playlist_id)



