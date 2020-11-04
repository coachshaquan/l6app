#pip3 install pygame
 
from sense_hat import SenseHat
import tekore as tk
import webbrowser

from flask import Flask, render_template, url_for, redirect, request


app = Flask(__name__)

def initSense():
    sense = SenseHat()
    sense.set_rotation(180)
    return sense

        
@app.route('/')
def initShopify():
    global spotify
    client_id = '2fe3a966943f4012ba2256ec982775a2'
    client_secret = '3c1fa4284b1a4992b82345bd8499fa56'
    login_info = tk.Credentials(client_id, client_secret, redirect_uri="http://localhost:8080/")
    auth_code = login_info.user_authorisation_url(scope=tk.scope.every)
    
    if request.args.get('code'):
        token = login_info.request_user_token(request.args.get('code'))
        spotify = tk.Spotify(login_info)
        spotify.token = token
        
        playlistContext = "spotify:playlist:0butRtEHnXwecVTH2cvOcK"
        devices = spotify.playback_devices()
        device = devices[len(devices)-1]
        
        spotify.playback_start_context(playlistContext, device_id=device.id)
        
        return main()
    else:
        return redirect(auth_code)

def changeStatus():
    if not spotify.playback_currently_playing().is_playing:
        print("Resuming Music")
        spotify.playback_resume()
    else:
        print("Pausing Music")
        spotify.playback_pause()

def changeSound(increment):
    old_vol = spotify.playback().device.volume_percent
    new_vol = old_vol+increment
    if new_vol < 100 and new_vol>0:
        print("Updating Volume to " + str(new_vol) + "%")
        spotify.playback_volume(new_vol)

def changePosition(increment):
    old_time = spotify.playback_currently_playing().progress_ms
    old_time = int(old_time)
    new_time = old_time + increment
    if new_time>0:
        try:
            print("Updating Position to " + str(new_time) + " ms") 
            spotify.playback_seek(new_time)
        except:
            print("Could not update your position!")
def changeSong(direction):
    if direction>0:
        try:
            print("Queueing next song")
            spotify.playback_next()
        except:
            print("Cannot queue next song. You are at the end of your playlist")
            None
    else:
        try:
            print("Queueing previous song")
            spotify.playback_previous()
        except:
            print("Cannot queue previous song. You are at the beginning of your playlist")
            None
            
def main():
    sense = initSense()
    sense.show_message("HI")
    event = 1;
    former_event = 1;

    while event:
        event = sense.stick.wait_for_event()
        print("\x1b[1M", end="")
        #If the joystick is double tapped:
        if former_event == event.direction and event.action !="released" and former_event != "up" and former_event !="down":
            if event.direction == "middle":
                changeStatus()
            elif event.direction == "left":
                changeSong(-1)
                former_event = 0
            elif event.direction == "right":
                changeSong(1)
                former_event = 0  
        elif event.action == "pressed":
            if event.direction == "middle":
                changeStatus()
            if event.direction == "up":
                changeSound(-10)
            if event.direction == "down":
                changeSound(10)
        elif event.action == "held":
            if event.direction =="right":
                changePosition(1)
            elif event.direction =="left":
                changePosition(-1)
        elif event.action == "released" and former_event != 0:
            former_event = event.direction
        else:
            former_event = 1;
            
webbrowser.open_new("http://localhost:8080/")
app.run(host='0.0.0.0', port=8080, threaded=True)

# img =  Image.open("sprite.jpg")
# img = img.resize((8, 8), Image.BILINEAR)
# img.save("sprite_resized.jpg")
# sense.load_image("sprite_resized.jpg")

