from requests_oauthlib import OAuth1
import requests
import secrets
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
import spotipy.util as util
import os

#call Spotify API
SPOTIPY_CLIENT_ID = secrets.client_id
SPOTIPY_CLIENT_SECRET = secrets.client_secret
scope = 'user-library-read'

def get_spotify_info(search_terms):
    # token = util.prompt_for_user_token(username='Chloe Hull', scope=scope,
    # client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=' ')
    # spotify = spotipy.Spotify(auth=token)
    # return spotify
    # os.putenv("SPOTIPY_CLIENT_ID", SPOTIPY_CLIENT_ID)
    # os.putenv("SPOTIPY_CLIENT_SECRET", SPOTIPY_CLIENT_SECRET)

    client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    results = sp.search(q='artist:' + search_terms, type='artist')
    artist_uri = results['artists']['items'][0]['uri']
   
    albums = sp.artist_albums(artist_uri, album_type='album')
    song_counts = {}
    album_name = ''
    track_total = ''
    for item in albums['items']:
        for key, value in item.items():
            if key == 'name':
                album_name = value
            if key == 'total_tracks':
                track_total = value
            song_counts[album_name] = track_total
    artist = albums['items'][0]['artists'][0]['name']
    song_counts['artist'] = artist
    del song_counts['']
    return song_counts
    
        # albums = results['items']
    # while results['next']:
    #     results = sp.next(results)
    #     albums.extend(results['items'])

    # for album in albums:
    #     print(album['name'])


## Call iTunes API
BASE_URL = "https://itunes.apple.com/search"
DB_NAME = 'final_project.sqlite'


def get_data(url, params=None):
    '''Calls API given a valid API link and returns the json
    representation of the data.

    Parameters
    -----------
    url: str
        The base URL of the API to be called
    params: str
        The terms to be searched for in the API call

    Returns
    --------
    dict
        The results of the API call represented in a dictionary.

    '''
    resp = requests.get(BASE_URL, params = params).json()
    if resp['resultCount'] == 0:
        print("There are no results for this search.")
        exit()
    else:
        return resp

def parse_itunes_data(data, artist):
    '''Parses through a dictionary of all data called from the API. Returns
    the relevant data and categorizes each object into the correct media
    type: song, movie, or other media.

    Parameters
    -----------
    data: dict
        The data to be parsed, cleaned, and categorized

    Returns
    --------
    dict
        A dictionary with key-value pairs for songs, movies, and other media

    '''
    songs_list = []
    movies_list = []
    other_list = []
    final_dict = {}
    song_names = []
    album_names = []
    artist_info = {}
    for key, value in data.items():
        if key == 'results':
            for item in value:
                for key, value in item.items():
                    if key == 'kind' and value == 'song':
                        #   new_item = Song(json=item)
                        songs_list.append(item)
                    if key == 'trackName':
                        song_names.append(value)
                    elif key == 'kind' and value == 'feature-movie':
                      #  new_m_item = Movie(json=item)
                        movies_list.append(item)
                    if key == 'collectionName':
                        album_names.append(value)
                    elif key == 'kind':
                       # new_o_list = Media(json=item)
                        other_list.append(item)
            final_dict['song'] = songs_list
            final_dict['movie'] = movies_list
            final_dict['other'] = other_list
            artist_info['songs'] = list(dict.fromkeys(song_names))
            artist_info['albums'] = list(dict.fromkeys(album_names))
            return artist_info

def count_data(data, artist):
    '''
    INSERT DOCSTRING
    '''
    final_counts = {}
    final_counts['artist'] = params
    for key, value in data.items():
        count_songs = 0
        count_albums = 0
        if key == 'songs':
            for item in value:
                count_songs += 1
            final_counts['song'] = count_songs
        if key == 'albums':
            for item in value:
                count_albums += 1
            final_counts['albums'] = count_albums
    return final_counts


## Call Twitter API





## create SQL database with appropriate schema
def create_db():
    '''
    INSERT DOCSTRING
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    drop_spotify_sql = 'DROP TABLE IF EXISTS "Spotify_Artists"'
    drop_itunes_sql = 'DROP TABLE IF EXISTS "Itunes_Artists"'
    drop_master_sql = 'DROP TABLE IF EXISTS "Master_Table"'

    
    create_spotify_artist_sql = '''
        CREATE TABLE IF NOT EXISTS "Spotify_Artists" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "ArtistName" TEXT NOT NULL,
            "SongsAvailable" INTEGER NOT NULL,
            "AlbumsAvailable" INTEGER NOT NULL
        )
    '''
    create_itunes_artist_sql = '''
        CREATE TABLE IF NOT EXISTS "Itunes_Artists" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "ArtistName" TEXT NOT NULL,
            "SongsAvailable" INTEGER NOT NULL,
            "AlbumsAvailable" INTEGER NOT NULL
        )
    '''
    create_master_table_sql = '''
        CREATE TABLE IF NOT EXISTS "Master_Table" (
            "Id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "ArtistName(Spotify)" INTEGER NOT NULL,
            "SongsAvailable(Spotify)" INTEGER NOT NULL,
            "AlbumsAvailable(Spotify)" INTEGER NOT NULL,
            "ArtistName(iTunes)" INTEGER NOT NULL,
            "SongsAvailable(iTunes)" INTEGER NOT NULL,
            "AlbumsAvailable(iTunes)" INTEGER NOT NULL
        )
    '''
    # cur.execute(drop_spotify_sql)
    # cur.execute(drop_itunes_sql)
    # cur.execute(drop_master_sql)
    cur.execute(create_spotify_artist_sql)
    cur.execute(create_itunes_artist_sql)
    cur.execute(create_master_table_sql)
    conn.commit()
    conn.close()


## store data from each API call in appropriate format in database
# (store "Musician Name", "# of Songs", "# of albums", "# of other media")
def insert_itunes(data):
    '''
    INSERT DOCSTRING
    '''
    artist_name = data['artist']
    song_count = data['song']
    album_count = data['albums']
    insert_itunes_sql = '''
        INSERT INTO Itunes_Artists
        VALUES (Null, ?, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(insert_itunes_sql,
        [
            artist_name,
            song_count,
            album_count
        ]
        )
    conn.commit()
    conn.close()

def insert_spotify(data):
    '''
    INSERT DOCSTRING
    '''
    artist_name = data['artist']
    song_count = 0
    album_count = 0
    del data['artist']
    for key, value in data.items():
        song_count += value
        album_count += 1
    insert_spotify_sql = '''
        INSERT INTO Spotify_Artists
        VALUES (Null, ?, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(insert_spotify_sql,
        [
            artist_name,
            song_count,
            album_count
        ]
        )
    conn.commit()
    conn.close()


def insert_master_sql(artist):
    '''
    INSERT DOCSTRING
    '''
    # create SQL queries to get IDs and populate master table
    select_spotify_id_sql = '''
    SELECT Id, SongsAvailable, AlbumsAvailable FROM Spotify_Artists
    WHERE ArtistName = ?
    '''

    select_itunes_id_sql = '''
    SELECT Id, SongsAvailable, AlbumsAvailable FROM Itunes_Artists
    WHERE ArtistName = ?
    '''

    insert_master_sql = '''
        INSERT INTO Master_Table
        VALUES (NULL, ?, ?, ?, ?, ?, ?)
    '''
   
    #get ID for both Spotify & iTunes
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(select_spotify_id_sql, (artist,))
    res = cur.fetchone()
    spotify_id = res[0]
    spotify_songs = res[1]
    spotify_albums = res[2]
    cur.execute(select_itunes_id_sql, (artist,))
    res = cur.fetchone()
    itunes_id = res[0]
    itunes_songs = res[1]
    itunes_albums = res[1]
    cur.execute(insert_master_sql, [spotify_id, spotify_songs, spotify_albums, itunes_id, itunes_songs, itunes_albums])
    conn.commit()
    conn.close()





## create interactive user interface



## create plotly & flask output

if __name__ == '__main__':
    create_db()
    params = 'Kacey Musgraves'
    data = get_data(BASE_URL, params="term=" + params + '')
    data = parse_itunes_data(data, params)
    data = count_data(data, params)
    insert_itunes(data)
    data = get_spotify_info(params)
    print(data)
    insert_spotify(data)
    insert_master_sql(params)

