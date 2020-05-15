# Loops inside of Youtube playlist named X and appends songs to a list
# Gets list of user's spotify playlists
# If there's no palylist named X, creates one, if there's one adds songs to it
# With a list it gets from Youtube, searches songs on Spotify and adds them to a Spotify playlist

import sys
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import spotSecret
import spotipy # This porject could be done without spotipy module, using requests too.
import spotipy.util as util
from difflib import SequenceMatcher

class CreatePlaylist():

       def __init__(self,username,SpoPlaylistName):
              self.SpoPlaylistName = SpoPlaylistName
              self.username = username
              scope = 'playlist-read-private playlist-modify-private playlist-modify-public'
              self.token = util.prompt_for_user_token(self.username,scope,client_id=spotSecret.clientID,client_secret=spotSecret.clientSecret,redirect_uri=spotSecret.redirectUri)
              self.sp = spotipy.Spotify(auth=self.token)

       # USEFUL FUNCTIONS
       def remove_at(self, string):
              if '[' in string or '(' in string:
                     for char in string:
                            if char == '[' or char =='(':
                                   indexNumber = string.index(char)
                     deletePart = string[indexNumber:len(string)]
                     string = string.replace(deletePart,'')
                     return string.rstrip()
              else:
                     return string
       # MAIN FUNCTIONS
       # Returns list of songs in Youtube playlist
       def youtubeListSongs(self):
              songList = []
              scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

              api_service_name = "youtube"
              api_version = "v3"
              client_secrets_file = "client_secret_709643891409-dovpsc68lh7eg31k2h8ra84cdtvk10e2.apps.googleusercontent.com.json"

              # Get credentials and create an API client
              flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
              credentials = flow.run_console()
              youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

              request = youtube.playlistItems().list(
                     part="snippet,contentDetails",
                     maxResults=25,
                     playlistId="PLQPJ3i6G7W9r6npARpilkGYZuacvxf1r8"
              )
              response = request.execute()
              for item in response['items']:
                     songList.append(item['snippet']['title'])
                            
              songListClean = []
              for i in songList:
                     songListClean.append(self.remove_at(i))

              return songListClean

       # Returns list of Spotify playlists
       def spotifyPlaylists(self):
              playlistList = []
              self.playlistIdList =[]
              if self.token:
                     playlists = self.sp.user_playlists(user=self.username)
                     for playlist in playlists['items']:
                            playlistList.append(playlist['name'])
                            self.playlistIdList.append(playlist['id'])

              else: 
                     return "Can't get token for "+ self.username
              return playlistList
       
       # Creates A Spotify Playlist if It's Not Created
       def createSpotifyList(self):
              playlists = self.spotifyPlaylists()
              if type(playlists) is str:
                     print(playlists)
              else:
                     if self.SpoPlaylistName not in playlists:
                            if self.token:
                                   self.sp.user_playlist_create(user=self.username,name=self.SpoPlaylistName,public=False,description='description')

       # Looks to Spotify playlist songs
       def getSpoListSongs(self,playlistID):
              result = self.sp.user_playlist_tracks(user=self.username,playlist_id=playlistID,limit=100)
              result = result['items']
              songList = []
              for item in result:
                     songList.append(item['track']['name'])
              return songList

       # Addings songs to spotify list
       def addSongsToSpotifyList(self):
              # Searching songs in Spotify
              ytSongs = self.youtubeListSongs()
              self.createSpotifyList()
              spoLists = self.spotifyPlaylists()
              songIDList =[]

              # Getting index of newly added playlist
              playlistIndex = spoLists.index(self.SpoPlaylistName)
              playlistID = self.playlistIdList[playlistIndex]

              spoSongs = self.getSpoListSongs(playlistID=playlistID)

              # Searching Youtube songs on Spotify
              ytSongs = [song.split('-')[1].lstrip() for song in ytSongs]
              for i in range(len(ytSongs)):
                     for SpoSong in spoSongs:
                            if SpoSong in ytSongs:
                                   ytSongs.remove(SpoSong)

              for song in ytSongs:
                     result = self.sp.search(q=song,type='track')
                     songUri = result['tracks']['items'][0]['uri']
                     songIDList.append(songUri)

              self.sp.user_playlist_add_tracks(self.username,playlistID,songIDList)



if __name__ == "__main__":
    pl = CreatePlaylist('username','Playlist Name')
    pl.addSongsToSpotifyList()