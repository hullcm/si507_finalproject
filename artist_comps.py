from requests_oauthlib import OAuth1
import requests
import secrets
import twitter_secrets
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
import spotipy.util as util
import os
import json
from flask import Flask, render_template, request
import plotly.graph_objects as go



#call Spotify API
SPOTIPY_CLIENT_ID = secrets.client_id
SPOTIPY_CLIENT_SECRET = secrets.client_secret
scope = 'user-library-read'

def get_spotify_info(search_terms):
    '''Calls spotify artists API and returns information on selected artist.
    Parses data and returns only relevant data for this application.

    Parameters
    -----------
    search_terms: str
        the string representation of the artist to be searched

    Returns
    --------
    dict
        dictionary containing each album by the artist and the number of songs on each album
    '''

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
   # song_counts['artist'] = search_terms
    print('spotify_save_results', song_counts)
    del song_counts['']
    return song_counts


def spotify_count_pres(data):
    '''Generates the count of albums and songs for Spotify results.

    Parameters
    -----------
    data: dict
        the string representation of the artist to be searched

    Returns
    --------
    dict
        dictionary containing each album by the artist and the number of songs on each album
    '''
    length = []
    songs = sum(data.values())
    length.append(songs)
    albums = len(data.keys())
    length.append(albums)
    return length

## Call iTunes API
BASE_URL = "https://itunes.apple.com/search"
DB_NAME = 'final_project.sqlite'

def get_data(url, params=None):
    '''Calls iTunes API given a valid API link and returns the json
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
    artist: string
        The artist the data represents

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
            artist_info['artist'] = artist
            return artist_info


def count_data(data, artist):
    '''Generates the count of albums and songs for iTunes results.

    Parameters
    -----------
    data: dict
        the string representation of the artist to be searched
    artist: string
        The artist the data represents

    Returns
    --------
    dict
        dictionary containing each album by the artist and the number of songs on each album
    '''
    final_counts = {}
    final_counts['artist'] = artist
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


def itunes_count_for_pres(data):
    '''Generates the final count of albums and songs for iTunes results for final presentation.

    Parameters
    -----------
    data: dict
        the string representation of the artist to be searched

    Returns
    --------
    list
        list containing each album by the artist and the number of songs on each album
    '''
    length = []
    for key, value in data.items():
        if key == 'songs':
            total_songs = len(value)
            length.append(total_songs)
        if key == 'albums':
            count = 0
            for item in value:
                count += 1
            total_albums = count
            length.append(total_albums)
    return length

## Call Twitter API & Return most recent tweet
TWITTER_BASE_URL = "https://api.twitter.com/1.1/users/search.json"

client_key = twitter_secrets.TWITTER_API_KEY
client_secret = twitter_secrets.TWITTER_API_SECRET
access_token = twitter_secrets.TWITTER_ACCESS_TOKEN
access_token_secret = twitter_secrets.TWITTER_ACCESS_TOKEN_SECRET

oauth = OAuth1(client_key,
            client_secret=client_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret)

def get_tweet(name):
    '''Calls the Twitter API, searches for the latest tweet by the selected artist,
    and returns the most recent tweet. 

    Parameters
    -----------
    name: string
        The name of the artist the data represents

    Returns
    --------
    string
        the most recent tweet by the selected artist
    '''
    params = 'q=' + name + ''
    response = requests.get(TWITTER_BASE_URL, params, auth=oauth)
    results = response.json()
    recent_tweet = results[0]['status']['text']
    print(recent_tweet)
    return recent_tweet


## create SQL database with appropriate schema
def create_db():
    '''Executes the specified query to create the
    database, the new tables, and close the database connection

    Parameters
    -----------
    None

    Returns
    --------
    None
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


## define functions for caching
CACHE_FILENAME = 'artists_cache.json'

def open_cache():
    '''Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    If the cache file doesn't exist, creates a new cache dictionary.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    '''Saves the current state of the cache to disk.
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    fw = open(CACHE_FILENAME,"w")
    fw.write(json.dumps(cache_dict))
    fw.close()


def make_request_with_cache(url, params=None):
    '''Makes an api request if request is not stored in the cache.
    
    Parameters
    -----------
    url: str
        url for the API to be called
    params: dict
        parameters for the API call

    Returns
    -------
    str
        the text results from the API call
    '''
    if params != None:
        zcode = params
        url_to_store = url + zcode
        if url_to_store in CACHE_DICT:
            print('Using Cache', url_to_store)
            print(CACHE_DICT[url_to_store])
            return CACHE_DICT[url_to_store]
        else:
            print('Fetching')
            if 'spotify' in url:
                data = get_spotify_info(params)
                print('spotify_fetch', data)
                CACHE_DICT[url_to_store] = data
                print(CACHE_DICT[url_to_store])
                save_cache(CACHE_DICT)
            elif 'itunes' in url:
                data = get_data(url, params="term=" + params + '')
                data = parse_itunes_data(data, params)
                print('itunes data: ', data)
                CACHE_DICT[url_to_store] = data
                #print(CACHE_DICT[url_to_store])
                save_cache(CACHE_DICT)
            elif 'twitter' in url:
                CACHE_DICT[url_to_store] = get_tweet(params)
                save_cache(CACHE_DICT)
            return CACHE_DICT[url_to_store]


## store data from each API call in appropriate format in database
# (store "Musician Name", "# of Songs", "# of albums", "# of other media")
def insert_itunes(data):
    '''Executes the specified query to insert
    the query results and close the database connection.

    Parameters
    -----------
    data: dict
        the data to be inserted into the database

    Returns
    --------
    None
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


def insert_spotify(data, artist_name):
    '''Executes the specified query to insert
    the query results and close the database connection.

    Parameters
    -----------
    data: dict
        the data to be inserted into the database

    Returns
    --------
    None
    '''
    song_count = 0
    album_count = 0    
    for key, value in data.items():
        print(key, value)
        album_count += 1
    song_count = sum(data.values())
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
    '''Executes the specified query to insert
    the query results and close the database connection.

    Parameters
    -----------
    data: dict
        the data to be inserted into the database

    Returns
    --------
    None
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


## create plotly & flask output

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html') # just the static HTML

@app.route('/handle_form', methods=['POST'])
def handle_the_form():
    artist_name = request.form['name']
    vis_type = request.form['visualization']
    
    itunes_data = make_request_with_cache('itunes', artist_name)
    itunes_data = count_data(itunes_data, artist_name)
    insert_itunes(itunes_data)
    spotify_data = make_request_with_cache('spotify', artist_name)
    insert_spotify(spotify_data, artist_name)
    spotify_data = spotify_count_pres(spotify_data)
    insert_master_sql(artist_name)
    tweet_data = make_request_with_cache('twitter', artist_name)
    print('itunes: ', itunes_data, 'spotify: ', spotify_data, 'twitter: ', tweet_data)
    if vis_type == 'plot':
        y_vals = [itunes_data['song'], spotify_data[0], itunes_data['albums'], spotify_data[1]]
        x_vals = ['iTunes Songs', 'Spotify Songs', 'iTunes Albums', 'Spotify Albums']
        data = go.Bar(
            x=x_vals,
            y=y_vals
        )
        fig = go.Figure(data=data)
        div = fig.to_html(full_html=False)
        return render_template('plot.html', plot_div=div, spotify=spotify_data)
    elif vis_type == 'detail':
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y = ['iTunes', 'Spotify'],
            x = [itunes_data['song'], spotify_data[0]],
            name='Song Counts',
            orientation='h',
            marker=dict(
                color='rgba(200, 78, 350, 0.6)',
                line=dict(color='rgba(200, 78, 139, 1.0)', width=3)
            )
        ))
        fig.add_trace(go.Bar(
            y = ['iTunes', 'Spotify'],
            x = [itunes_data['albums'], spotify_data[1]],
            name='Album Counts',
            orientation='h',
            marker=dict(
                color='rgba(58, 201, 80, 0.6)',
                line=dict(color='rgba(58, 71, 80, 1.0)', width=3)
            )
        ))
        fig.update_layout(barmode='stack')
        div = fig.to_html(full_html=False)
        return render_template('horizplot.html', plot_div=div, spotify=spotify_data)
    elif vis_type == 'all':
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y = ['iTunes', 'Spotify'],
            x = [itunes_data['song'], spotify_data[0]],
            name='Song Counts',
            orientation='h',
            marker=dict(
                color='rgba(200, 78, 350, 0.6)',
                line=dict(color='rgba(200, 78, 139, 1.0)', width=3)
            )
        ))
        fig.add_trace(go.Bar(
            y = ['iTunes', 'Spotify'],
            x = [itunes_data['albums'], spotify_data[1]],
            name='Album Counts',
            orientation='h',
            marker=dict(
                color='rgba(58, 201, 80, 0.6)',
                line=dict(color='rgba(58, 71, 80, 1.0)', width=3)
            )
        ))
        fig.update_layout(barmode='stack')
        div = fig.to_html(full_html=False)
        return render_template('allinfo.html', artist=artist_name, itunes=itunes_data,
                spotify=spotify_data, twitter=tweet_data, plot_div=div)
    else:
        return render_template('table.html', artist=artist_name, itunes=itunes_data,
                spotify=spotify_data, twitter=tweet_data)


##run application
CACHE_DICT = open_cache()
if __name__ == '__main__':
    create_db()
    app.run(debug=True)