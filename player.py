from gmusicapi import Mobileclient
import getpass
import subprocess
from flask import Flask, request, render_template, flash
from wtforms import Form, TextField,TextAreaField, validators, StringField, SubmitField


app = Flask(__name__)

class ReusableForm(Form):
	songTitle = TextField('Song Title:', validators=[validators.required()])
	artistName = TextField('Artist:', validators=[validators.required()])

@app.route("/", methods=['GET', 'POST'])
def playSong():
    form = ReusableForm(request.form)

    print form.errors
    if request.method == 'POST':
        songTitle = request.form['songTitle']
        artistName = request.form['artistName']
        print "Playing %s by %s" % (songTitle, artistName)
        
        registeredDevices = client.get_registered_devices()
	
        #Picking LG device by default for now
        deviceID = registeredDevices[0]['id']

        #Search for song
        searchQuery = songTitle + "+" + artistName
        searchResults = client.search(searchQuery, max_results=5)
        topResult = searchResults['song_hits'][0]['track']
        streamURL = client.get_stream_url(topResult['storeId'], deviceID[2:])
        subprocess.call(['mpv', streamURL])

    return render_template('index.html', form=form)


if __name__ == "__main__":
    client = Mobileclient()

    gmusicUsername = raw_input('Enter Google Play Music username: ')
    gmusicPassword = getpass.getpass('Enter password: ')
    loggedIn = client.login(gmusicUsername, gmusicPassword, Mobileclient.FROM_MAC_ADDRESS)

    if loggedIn:
        print "Successfully logged in"
        app.run(debug=True)
    else:
        print "Failed to login"

