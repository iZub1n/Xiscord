import os
import json
from collections import deque
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_session import Session
from flask_socketio import SocketIO, emit, send, join_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app, async_mode = None)

app.secret_key = "hello"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# vars
dNamesList=[]
channelsList=["General","Beyblade"]
channelsMessages = {}
channelsMessages["General"]= []
channelsMessages["Beyblade"]= []

@app.route("/db")
def debug():
    return str(channelsMessages["General"])

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/chat", methods=["POST","GET"])
def login():
    if "user" not in session:
        if request.method=="POST":
            displayname = request.form.get("displayName")

            if displayname in dNamesList:
                return render_template("index.html" ,alert="Display name already exists!")

            dNamesList.append(displayname)
            session["user"] = displayname
            return render_template("channel.html",  channels= channelsList, dname=session['user'])
        else:
            return redirect("/")
    else:
        return render_template("channel.html", channels= channelsList, dname=session['user'])

@app.route("/logout", methods=["POST","GET"])
def logout():
    if "user" not in session:
        return redirect(url_for("index"))

    displayname=session.pop("user", None)
    if displayname in dNamesList:
        dNamesList.remove(displayname)
    return redirect("/")

@app.route("/error")
def error():
    if "user" not in session:
        return redirect(url_for("index"))
    
    displayname = session['user']
    if displayname in dNamesList:
        return True
    return False

@app.route('/loadChannels')
def loadChannels():
    return jsonify(channelsList)

@app.route("/legalChannel")
def legalChannel():
    if "user" not in session:
        return redirect(url_for("index"))

    newChannel = request.form.get("newChannelName")
    res=[]
    if newChannel in channelsList:
        res.append(False)
        return jsonify(res)
    res.append(True)
    return jsonify(res)

@app.route("/Error", methods=['GET','POST'])
def create():
    if "user" not in session:
        return redirect(url_for("index"))

    newChannel = request.form.get("newChannelName")

    if request.method == "POST":
        if request.form['action']=='addChannel':
            if newChannel.lower() in (nc.lower() for nc in channelsList):
                return render_template("chatPage.html" ,dname=session['user'] ,alert="Channel name already exists!", channels= channelsList, cname=session.get('current_channel'))
            channelsList.append(newChannel)
            channelsMessages[newChannel]= []
            return redirect("/chat/" + newChannel)

@app.route("/chat/<channel>", methods=['GET','POST'])
def joinChannel(channel):
    if "user" not in session:
        return redirect(url_for("index"))
    
    if channel not in channelsList:
        session['current_channel'] = "General"
        return redirect("/chat/General")

    session["currentChannel"] = channel
    if request.method == "POST":
        
        return redirect("/")
    else: 
         session['current_channel'] = channel
         return render_template("chatPage.html", channels= channelsList, cname=channel, messages=channelsMessages[channel], dname=session['user'])
    
@app.route('/loadChannelMessages/<channel>', methods=["POST"])
def loadChannelMessages(channel):
    return jsonify(channelsMessages[channel])

@socketio.on("send message")
def sendMessage(data, timestamp):
    room = session.get('current_channel')
    message = data["message"]
    channelsMessages[room].append([timestamp, session.get('user'), message])
    join_room(room)
    if len(channelsMessages[room])>100:
        channelsMessages[room].pop(0)

    emit("announce message", {'user': session.get('user'), 'timestamp': timestamp, 'message': message}, room=room)
    