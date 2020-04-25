# si507_finalproject
Final Project for SI507

This repo contains code for an "Artist Coverage Application." 
The application calls the Spotify, iTunes, and Twitter API to collate the number of songs and albums available on each platform for a given artist. The application collates these results for the user, as well as the most recent tweet by the artist, then displays them in a simple UI. 

Inside the repo you will find the final python file ('artist_comps.py'), as well as the Flask templates used for the UI component. 
Within the python file, there is code that will create your database for you. 

This application requires the following packages to be installed: requests, spotipy, flask, plotly

This application requires the following to work properly: 

To run this program, you will need to obtain authorization from the Twitter, Spotify, and iTunes API.
For Twitter you will need: API Key, API Secret, Access Token, Access Token Secret. 
For Spotify, you will need to install the Spotipy package and obtain your Client ID and Client Secret.
For iTunes, no authentication is required, so you can call the endpoint without further authorization. 

Brief instructions on how to interact with the program as a user: 

Please input the artist you are most interested in (example: Leon Bridges), then select the option you would like to display your results. Press submit and your results will be displayed in your preferred format. You have four options for your output: (1) Simple Plot, (2) Detailed Plot, (3) Table, (4) All Info. Each option will render a different page displaying the information you have selected. The simple plot displays a simple bar plot with the results, while the detailed plot is a more advanced, intuitive view of the data. The table option displays the data in its raw format, as well as contains the most recent tweet of the selected artist. The final view displays all of this information: the raw data in a table format, the detailed plot, and the most recent tweet. After viewing your results, feel free to return to the home page and view your results in a new format. 

