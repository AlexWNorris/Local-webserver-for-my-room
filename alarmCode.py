from datetime import datetime
from re import findall
from time import sleep
import pafy, urllib, vlc

alarmPath="python/superVillianRoomCode/webserver/static/data/alarmInformation.txt"
activeMedia=None

def findYoutubeVideo(serchPhrase):
    search_keyword=str(serchPhrase).replace(" ","+")
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_keyword)
    video_ids = findall(r"watch\?v=(\S{11})", html.read().decode())
    return("https://www.youtube.com/watch?v=" + video_ids[0])

def playSong(serchPhrase):
    global activeMedia
    url=findYoutubeVideo(serchPhrase)
    video = pafy.new(url)
    best = video.getbestaudio()
    media = vlc.MediaPlayer(best.url)
    media.play()
    activeMedia=media
    while media.is_playing()==False:
        sleep(0.25)
    while media.is_playing():
        sleep(1)
    activeMedia=None


with open(alarmPath,'r') as alarmFile:
        alarmFileContent=alarmFile.readlines()
song=alarmFileContent[0].replace('\n','')
targetTime=alarmFileContent[1].replace('\n','')
while True:
    currentTime=datetime.now().strftime("%H:%M")
    if targetTime==currentTime:
        playSong(song)
    sleep(0.25)
  
        

