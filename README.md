# si507_finalproject
Final Project for SI507

This repo contains code for an "Artist Coverage Application." 
The application calls the Spotify, iTunes, and Twitter API to collate interesting results for the user, then displays them in a simple UI. 
This application requires the following packages to be installed: requests, spotipy, flask, plotly

Inside the repo you will find the final python file ('artist_comps.py'), as well as the Flask templates used for the UI component. 
Within the python file, there is code that will create your database for you. 

To run this program, you will need to obtain authorization from the Twitter, Spotify, and iTunes API.
For Twitter you will need: API Key, API Secret, Access Token, Access Token Secret. 
For Spotify, you will need to install the Spotipy package and obtain your Client ID and Client Secret.
For iTunes, no authentication is required, so you can call the endpoint without further authorization. 
