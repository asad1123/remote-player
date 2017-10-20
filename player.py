from gmusicapi import Mobileclient
import getpass
import subprocess
from flask import Flask, request, render_template, flash
from wtforms import Form, TextField,TextAreaField, validators, StringField, SubmitField
import threading
import Queue


app = Flask(__name__)
songInfo ={}
songQueue = Queue.Queue()
mutex = threading.Lock()

class ReusableForm(Form):
	songTitle = TextField('Song Title:', validators=[validators.required()])
	artistName = TextField('Artist:', validators=[validators.required()])

@app.route("/", methods=['GET', 'POST'])
def findSong():
    form = ReusableForm(request.form)

    print form.errors
    if request.method == 'POST':
        songInfo['songTitle'] = request.form['songTitle']
        songInfo['artistName'] = request.form['artistName']
        print "Playing %s by %s" % (songInfo['songTitle'], songInfo['artistName'])
        registeredDevices = client.get_registered_devices()
        #Picking LG device by default for now
        songInfo['deviceID'] = registeredDevices[0]['id']
        songQueue.put(songInfo)        
        mutex.acquire()
        playSong(songQueue.get())
        
    return render_template('index.html', form=form)

def playSong(songInfo):
    #Search for song
    searchQuery = songInfo['songTitle'] + "+" + songInfo['artistName']
    searchResults = client.search(searchQuery, max_results=5)
    topResult = searchResults['song_hits'][0]['track']
    streamURL = client.get_stream_url(topResult['storeId'], songInfo['deviceID'][2:])
    subprocess.call(['mpv', streamURL])
    mutex.release()
    
if __name__ == "__main__":
    client = Mobileclient()
    gmusicUsername = raw_input('Enter Google Play Music username: ')
    gmusicPassword = getpass.getpass('Enter password: ')
    loggedIn = client.login(gmusicUsername, gmusicPassword, Mobileclient.FROM_MAC_ADDRESS)
    
    app.run(host = '0.0.0.0', debug=True)

    if loggedIn:
        print "Successfully logged in"
    else:
        print "Failed to login"

