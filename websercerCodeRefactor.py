from random import randint
import yeelight, pafy, vlc, urllib, subprocess
from flask import Flask, jsonify , render_template, request
from subprocess import Popen
from ast import literal_eval
from colorsys import hsv_to_rgb
from re import findall
from time import sleep
app = Flask(__name__)

##flask webpage {

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/music')
def music():
    return render_template("music.html")

@app.route('/musicApi',methods=['POST'])
def musicApi():
    if request.method=='POST':
        data=request.data.decode('utf8')
        data=data.split(',')
        if data[0]=='PS':
            setSong(data[1])         
        elif data[0]=='AQ':
            addToQue(data[1])       
        elif data[0]=='CQ':
            clearQue()
        elif data[0]=='FT':
            return jsonify(fetchThumbnail(data[1]))
        elif data[0]=='TL':
            toggleLooping()
        elif data[0]=='TP':
            togglePause()
        elif data[0]=='SF':
            skip('F')
        elif data[0]=='SB':
            skip('B')
        elif data[0]=='PSPL':
            playSpotifyPlaylist(data[1])
        elif data[0]=='TSHFL':
            toogleShufflePlay()
        return'succsess'
        


        

    ##Yeelight specific webpages and fetch request responders {

@app.route('/lights')
def lights():
    return render_template("lights.html")

@app.route('/bulbapi',methods=['POST'])
def bulbApi():
    if request.method=='POST':
        if bulbs==[]:
            establishBulbConncection()    
        data=request.data.decode('utf-8')
        data=data.split(',')
        if data[0]=='CLC':
            changeBulbColour(data[1],True)
            return 'succsess'
        elif data[0]=='TL':
            toggleBulb()
            return 'succsess'
        elif data[0]=='SLS':
            saveBulbState()
            return 'succsess'
        elif data[0]=='LLS':
            return 'succsess'
        elif data[0]=='SeLS':
            setBulbState()
            return 'succsess'
        else:
            return 'invalid'
    else: 
        return 'invalid'


@app.route('/bulbapi/colors',methods=['POST','GET'])
def BulbDataToLightsHTML():
    if request.method=='GET':
         return jsonify(fetchSavedBulbStateColours())
    elif request.method=='POST':
        if bulbs==[]:
            establishBulbConncection()    
        data=int(request.data.decode('utf-8'))
        targetState=fetchSavedBulbStates()[data]
        setBulbState(dictToState(targetState))
        return 'succsess'
    else:
        return 'invalid'
    ## }


    ## Alarm window{
@app.route('/alarm')
def alarm():
    return render_template("alarm.html",passedData=fetchSavedAlarmStates())
    # }

@app.route('/alarmAPI',methods=['POST'])
def alarmAPI():
    if request.method=='POST':
        data=request.data.decode('utf8')
        data=data.split(',')
        if data[0]=='SNS':
            setNewAlarmSong(data[1])
        elif data[0]=='SNT':
            setNewAlarmTime(data[1])
        elif data[0]=='TAP':
            toggleAlarmProgram(data[1])
        return'succsess'
## }





##yeelight bulb handeling functions {
bulbs=[]
lightPath="python\superVillianRoomCode\webserver\static\data\savedLightStates.txt"
def establishBulbConncection(): 
    bulbData=yeelight.discover_bulbs()
    global bulbs
    for i in bulbData:
        bulbs.append(yeelight.Bulb(i.get('ip')))
def toggleBulb():
    for i in bulbs:
        i.toggle()

def changeBulbColour(value,isHex):
    if isHex==True:
        value=value.replace('#','')
        value=value.replace('\"','')
        r,g,b=tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
        h,s,v=rgb_to_hsv(r,g,b)

    for i in bulbs:
        i.set_hsv(h,s,v)
      
def saveBulbState():
    with open(lightPath,'r') as fl:
        fileContent=fl.readlines()
        sampleBulb=bulbs[0] 
        fileContent.append(str(sampleBulb.get_properties()))
        fileContent.append('\n')
    with open(lightPath,'w') as fl:
        fl.writelines(fileContent)

def dictToState(dictionary):
    brightness=int(dictionary.get('bright'))
    colourTemp=int(dictionary.get('ct'))
    hue=int(dictionary.get('hue'))
    saturation=int(dictionary.get('sat'))
    colorMode=int(dictionary.get('color_mode'))
    return brightness,colourTemp,hue,saturation,colorMode

def setBulbState(values):
    brightness,colourTemp,hue,saturation,colorMode=values
    for i in bulbs:
        i.set_brightness(brightness)
        if colorMode==1:
            i.set_hsv(hue,saturation,brightness)
        elif colorMode ==2:
            i.set_color_temp(colourTemp)
        else:
            print('color mode error')

def fetchSavedBulbStates():
    with open(lightPath,'r') as fl:
        fileContent=fl.readlines()
        listOfSavedBulbStates=[]
        for i in fileContent:
            dictionary=literal_eval(i.replace('\n',''))
            listOfSavedBulbStates.append(dictionary)
        return listOfSavedBulbStates

def fetchSavedBulbStateColours():
    ListOfSavedBulbStates=fetchSavedBulbStates()
    ListOfSavedColours=[]
    for i in ListOfSavedBulbStates:
        h,s,v=i.get('hue'),i.get('sat'),i.get('bright')
        if i.get('color_mode')=='1':
            ListOfSavedColours.append(F_hsv_to_rgb(h,s,v))
        elif i.get('color_mode')=='2':
            ListOfSavedColours.append(F_hsv_to_rgb(0,0,v))
    return ListOfSavedColours

def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100
    return h, s, v

def F_hsv_to_rgb(h,s,v):
    h,s,v=int(h),int(s),int(v)
    return tuple(round(i * 255) for i in hsv_to_rgb(h/360,s/100,v/100))
## }

## music functions{
songQue=[]
queIndex=1
looping=False
shuffle=False
activeMedia=None

def findYoutubeVideo(serchPhrase):
    search_keyword=str(serchPhrase).replace(" ","+")
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_keyword)
    video_ids = findall(r"watch\?v=(\S{11})", html.read().decode())
    return("https://www.youtube.com/watch?v=" + video_ids[0])

def setSong(serchPhrase):
    global activeMedia,songQue,queIndex
    if activeMedia==None:
        playSong(serchPhrase)
    else:
        url=findYoutubeVideo(serchPhrase)
        video = pafy.new(url)
        best = video.getbestaudio()
        songQue.insert(queIndex,best)
        activeMedia.stop()
    
        

def playSong(serchPhrase):
    global activeMedia, songQue
    url=findYoutubeVideo(serchPhrase)
    video = pafy.new(url)
    best = video.getbestaudio()
    media = vlc.MediaPlayer(best.url)
    media.play()
    if serchPhrase not in songQue:
        songQue.append(serchPhrase)
    activeMedia=media
    while media.is_playing()==False:
        sleep(0.25)
    while media.is_playing():
        sleep(1)
    activeMedia=None
    playNextInQue()


def playNextInQue():
    global songQue, looping,queIndex,activeMedia
    if queIndex<len(songQue):
        if shuffle==True:
            randIndex=randint(0,len(songQue)-1)
            song=songQue[randIndex]
        else:
            song=songQue[queIndex]
        queIndex=queIndex+1
        playSong(song)
        
    else:
        if looping==True:
            queIndex=0
            playNextInQue()
        else:
            queIndex=0
            clearQue()
            activeMedia=None

    

def addToQue(serchPhrase):
    global songQue
    songQue.append(serchPhrase)

def toggleLooping():
    global looping
    looping = not looping

def toogleShufflePlay():
    global shuffle
    shuffle = not shuffle

def clearQue():
    global songQue
    songQue=[]

def togglePause():
    global activeMedia
    if activeMedia==None:
        pass
    else:
        if activeMedia.is_playing():
            activeMedia.set_pause(1)
        else:
            activeMedia.set_pause(0)
    
def skip(direction):
    global activeMedia,songQue,queIndex
    if direction=='F':
        pass
    elif direction=='B':
        queIndex=queIndex-2
        if queIndex<0:
            queIndex=(len(songQue)-1)
    try:
        activeMedia.stop()
    except:
        pass
        

def fetchThumbnail(serchPhrase):
    url=findYoutubeVideo(serchPhrase)
    video = pafy.new(url)
    thumbNailLink=video.thumb
    return thumbNailLink

def playSpotifyPlaylist(link):
    global activeMedia,songQue,queIndex
    request=urllib.request.Request(link)
    webpage=urllib.request.urlopen(request)
    webpageHTML=webpage.read().decode("utf-8")
    target="class=\"EntityRowV2__Link-sc-ayafop-8 cGmPqp\">([^<]*).+?(?=href=\"/artist/)[^>]*>([^<]*)"
    songNames=findall(target,webpageHTML)
    for i in songNames:
        addToQue(i)
    if activeMedia==None:
        queIndex=queIndex-1
        playNextInQue()
    
  
## }

## alarm fuctions{ 
alarmPath="python/superVillianRoomCode/webserver/static/data/alarmInformation.txt"
alarmProgramPath="python/superVillianRoomCode/webserver/alarmCode.py"
envPath="python\superVillianRoomCode\webserver\env\Scripts\python.exe"
alarmProgramProcess=None
def setNewAlarmSong(songName):
    alarmFileContent=open(alarmPath,'r').readlines()
    alarmFileContent[0]=songName+'\n'
    with open(alarmPath,"w") as alarmFile:
        alarmFile.writelines(alarmFileContent)

def setNewAlarmTime(Time):
    alarmFileContent=open(alarmPath,'r').readlines()
    alarmFileContent[1]=Time+'\n'
    with open(alarmPath,"w") as alarmFile:
        alarmFile.writelines(alarmFileContent)
        
def fetchSavedAlarmStates():
    alarmFileContent=open(alarmPath,'r').readlines()
    for i in range(len(alarmFileContent)):
        alarmFileContent[i]=alarmFileContent[i].replace('\n','')
    return alarmFileContent

def toggleAlarmProgram(state):
    global alarmProgramProcess,envPath,alarmProgramPath
    if state=='T':
        alarmProgramProcess=Popen([envPath,alarmProgramPath])
    elif state=='F':
        try:
            alarmProgramProcess.terminate()
        except AttributeError:
            pass


##}
if __name__ == '__main__':
    app.run(host="0.0.0.0")