# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from PyLyrics import *
import pygn
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import json
from PIL import Image
import urllib.request
import io
import os
import sys
from tinytag import TinyTag
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TRCK, TDRC, TALB, USLT, TCON, TRCK, error

# ID3 info:
# APIC: picture
# TIT2: title
# TPE1: artist
# TRCK: track number
# TALB: album
# USLT: lyric
# TCON: Genre
# TDRL: Release

#clientID = "1998383831-B98F57CEBB466A2285795666C3346964"
#userID = pygn.register(clientID)
#print(userID)

toplevel = None
def Song_Metadata(Folder_Dir, tkwindow):
    global Error_Songs, folder, current_Song, error, Folder_Director

    #Creates folder if not exist
    if not os.path.exists(Folder_Dir + "/Cover Arts"):
        os.makedirs(Folder_Dir + "/Cover Arts")

    Folder_Director = Folder_Dir
    #Songs without enough information
    Error_Songs = []

    #Gets Gracenote API Information
    Gracenote_Info = open("Gracenote UserID.txt", "r")
    Gracenote_Lines = Gracenote_Info.readlines()
    Gracenote_UserID = Gracenote_Lines[1].rstrip('\n')
    Gracenote_ClientID = Gracenote_Lines[4].rstrip('\n')

    #Gets Directory of MP3 files
    folder = os.listdir(Folder_Dir)
    for i in range(len(folder)-1, -1, -1):
        if folder[i].endswith(".mp3") == False:
            del folder[i]

    pb = ttk.Progressbar(tkwindow, length=200, maximum=20)
    pb.grid(row=2, column=0)
    pb["maximum"] = len(folder)

    for i in range(len(folder)):
        current_Song = i + 1
        song_Dir = Folder_Dir + folder[i]

        pb["value"] = current_Song
        Label(tkwindow, text=str(current_Song) + "/" + str(len(folder)) + " Done").grid(row=2, column=1)
        tkwindow.update()

        id3 = ID3(song_Dir)

        temp = folder[i]
        if ("(" in folder[i]):
            temp = folder[i].split("(")[0]
        if("ft" in folder[i]):
            temp = folder[i].split("ft")[0]


        tag = TinyTag.get(Folder_Dir + temp)


        song_Artist = tag.artist
        song_Name = tag.title
        
        if song_Artist == None or song_Name == None:
            Art_and_Title = namecheck(folder[i])
            song_Artist = Art_and_Title[0]
            song_Name = Art_and_Title[1]

            if song_Artist == None or song_Name == None:
                Error_Songs.append(Folder_Dir + folder[i])
            
        if song_Artist != None and song_Name != None:
            #Gets Metadata and Lyrics for Song
            metadata = pygn.search(clientID = Gracenote_ClientID, userID = Gracenote_UserID, artist= song_Artist, album= "", track= song_Name)
            #print(json.dumps(metadata, sort_keys=True, indent=4))

            try:
                Title = metadata.get("track_title")

            except Exception:
                Title = song_Name

            try:
                Artist = metadata.get("album_artist_name")

            except Exception:
                Artist = song_Artist

            try:
                Album = metadata.get("album_title")

            except Exception:
                Album = None

            try:
                Album_Year = metadata.get("album_year")

            except Exception:
                Album_Year = None

            try:
                Genre_Num = sum(map(len, metadata.get("genre").values())) / 2

            except Exception:
                Genre_Num = None

            try:
                Track = metadata.get("tracks")[0].get("track_number")

            except Exception:
                Track = None
                pass

            Genre = []
            try:
                for i in range(1, int(Genre_Num + 1)):
                    Genre.append(metadata.get("genre").get(str(i)).get("TEXT"))
                Genre = list(set(Genre))

            except Exception:
                pass

            try:
                #Gets image URL and opens it
                Artist_URL = metadata.get("artist_image_url")
                Album_URL = metadata.get("album_art_url")

            except Exception:
                pass
            
            #Artist Picture
            try:
                with urllib.request.urlopen(Artist_URL) as url:
                    Artist_URL = io.BytesIO(url.read())
                    
                    Artist_Pic = Image.open(Artist_URL)
                    #Artist_Pic.show()
                    
            except Exception:
                pass
            
            #Album Picture
            try:
                with urllib.request.urlopen(Album_URL) as url:
                    Album_URL = io.BytesIO(url.read())
                    Album_Cover_Directory = Folder_Dir + "/Cover Arts/" + Album + " cover.jpg"
                    urllib.request.urlretrieve(metadata.get("album_art_url"), Album_Cover_Directory)
                    Album_Pic = Image.open(Album_URL)
                    
                    #Changes Album Picture
                    Album_data = open(Album_Cover_Directory, 'rb').read()
                    id3.add(APIC(3, 'image/jpeg', 3, 'Front cover', Album_data))
                    #Album_Pic.show()
            
            except Exception:
                pass
            
            #def Output_Song_Info():
                #print(" ")
                #print("Song Title =", Title)
                #print("Artist =", Artist)
                #print("Album =", Album)
                #print("Album Release Year =", Album_Year)
                #print("Genre =", ", ".join(Genre))
                #print(" ")
            
            #Gets lyrics of Song
            try:
                lyrics = PyLyrics.getLyrics(metadata.get("album_artist_name"), metadata.get("track_title"))
                lyrics_Title = (metadata.get("track_title") + " by " + metadata.get("album_artist_name"))
                
            except Exception:
                
                try:
                    lyrics = PyLyrics.getLyrics(song_Artist, song_Name)
                    lyrics_Title = song_Name + " by " + song_Artist
                    
                except Exception:
                    lyrics = None
                    pass
                
                pass
            
            #print(" ")
            #print(lyrics)
            #print(" ")

            try:
                id3.add(TALB(text = Album))

            except Exception:
                pass

            try:
                id3.add(TIT2(text = Title))

            except Exception:
                pass

            try:
                id3.add(TPE1(text = Artist))

            except Exception:
                pass

            try:
                id3.add(TCON(text = ", ".join(Genre)))

            except Exception:
                pass

            try:
                id3.add(TDRC(text = Album_Year))

            except Exception:
                pass

            try:
                id3.add(USLT(lang = "eng", text = lyrics_Title + "\n\n" + lyrics))

            except Exception:
                pass

            try:
                id3.add(TRCK(text = Track))

            except Exception:
                pass

            id3.save()

    if len(Error_Songs) != 0:
        Popup(Folder_Dir)
#Song_Metadata("/Users/xXskri113Xx/Desktop/Music Data/")


def Popup(dirname):
    global toplevel
    toplevel = Toplevel()
    Label(toplevel, text= Error_Songs[0].replace(Folder_Director, "")).grid(row=0)
    Label(toplevel, text="Could Not Be Recongnized").grid(row=1)
    Label(toplevel, text="Please Manually Input Song Title").grid(row=2)
    Label(toplevel, text="and Artist Name").grid(row=3)
    Label(toplevel, text="Song Title").grid(row=4)
    songpopup = Entry(toplevel)
    songpopup.grid(row=5, column=0)
    Label(toplevel, text="Artist Name").grid(row=6)
    artistpopup = Entry(toplevel)
    artistpopup.grid(row=7, column=0)
    Button(toplevel, text='Search', command = lambda: Song_Metadata_Error(dirname, artistpopup.get(), songpopup.get())).grid(row=8, column=0, pady=4)

def Song_Metadata_Error(Folder_Dir, song_Artist, song_Name):
    global Error_Songs, folder, current_Song, error
    toplevel.destroy()

    song_Dir = Error_Songs[0]
    del Error_Songs[0]
    id3 = ID3(song_Dir)

    #Gets Gracenote API Information
    Gracenote_Info = open("Gracenote UserID.txt", "r")
    Gracenote_Lines = Gracenote_Info.readlines()
    Gracenote_UserID = Gracenote_Lines[1].rstrip('\n')
    Gracenote_ClientID = Gracenote_Lines[4].rstrip('\n')

    # Gets Metadata and Lyrics for Song
    metadata = pygn.search(clientID=Gracenote_ClientID, userID=Gracenote_UserID, artist=song_Artist, album="",
                           track=song_Name)
    # print(json.dumps(metadata, sort_keys=True, indent=4))

    Title = metadata.get("track_title")
    Artist = metadata.get("album_artist_name")
    Album = metadata.get("album_title")
    Album_Year = metadata.get("album_year")
    Genre_Num = sum(map(len, metadata.get("genre").values())) / 2
    Genre = []
    Track = metadata.get("tracks")[0].get("track_number")

    for i in range(1, int(Genre_Num + 1)):
        Genre.append(metadata.get("genre").get(str(i)).get("TEXT"))
    Genre = list(set(Genre))

    # Gets image URL and opens it
    Artist_URL = metadata.get("artist_image_url")
    Album_URL = metadata.get("album_art_url")

    # Artist Picture
    try:
        with urllib.request.urlopen(Artist_URL) as url:
            Artist_URL = io.BytesIO(url.read())

            Artist_Pic = Image.open(Artist_URL)
            # Artist_Pic.show()

    except Exception:
        pass

    # Album Picture
    try:
        with urllib.request.urlopen(Album_URL) as url:
            Album_URL = io.BytesIO(url.read())
            Album_Cover_Directory = Folder_Dir + "/Cover Arts/" + Album + " cover.jpg"
            urllib.request.urlretrieve(metadata.get("album_art_url"), Album_Cover_Directory)
            Album_Pic = Image.open(Album_URL)

            # Changes Album Picture
            Album_data = open(Album_Cover_Directory, 'rb').read()
            id3.add(APIC(3, 'image/jpeg', 3, 'Front cover', Album_data))
            # Album_Pic.show()

    except Exception:
        pass

        # def Output_Song_Info():
        # print(" ")
        # print("Song Title =", Title)
        # print("Artist =", Artist)
        # print("Album =", Album)
        # print("Album Release Year =", Album_Year)
        # print("Genre =", ", ".join(Genre))
        # print(" ")

    # Gets lyrics of Song
    try:
        lyrics = PyLyrics.getLyrics(metadata.get("album_artist_name"), metadata.get("track_title"))
        lyrics_Title = (metadata.get("track_title") + " by " + metadata.get("album_artist_name"))

    except Exception:

        try:
            lyrics = PyLyrics.getLyrics(song_Artist, song_Name)
            lyrics_Title = song_Name + " by " + song_Artist

        except Exception:
            lyrics = None
            pass

        pass

    # print(" ")
    # print(lyrics)
    # print(" ")

    id3.add(TALB(text=Album))
    id3.add(TIT2(text=Title))
    id3.add(TPE1(text=Artist))
    id3.add(TCON(text=", ".join(Genre)))
    id3.add(TDRC(text=Album_Year))
    id3.add(USLT(lang="eng", text = lyrics_Title + "\n\n" + lyrics))
    id3.add(TRCK(text=Track))
    id3.save()

    if len(Error_Songs) != 0:
        Popup(Folder_Dir)

def format(a, s):
   s = re.sub(r'\([^)]*\)', '', s)                 #removing the parenthesis ex. (LYRIC)
   s = re.sub(r'\[[^)]*\]', '', s)                 #removing the brackets ex. [OFFICIAL]
   s = s.replace(".mp3", "")                       #removing the .mp3
   if "&" in a:
       a, otherartist = a.split("&")               #use the first artist if there are multiple
   if "ft." in s:
       s, featuringartist = s.split("ft.")         #remove featuring artists after ft. and feat.
   if "feat." in s:
       s, featuringartist = s.split("feat.")
   return a, s


def namecheck(f):
   f = f.lower()
   try:
       artist, song = f.split("-")
   except ValueError:
       #print(f + " doesn't work")           #if the song is unorthodox and doesn't have the -, initiate manual entry when finished
        return [None, None]
   artist, song = format(artist, song)
   return [artist.replace("_", "").lower(), song.replace("_", "").lower()]




