from gmusicapi import Mobileclient
from spotipy import oauth2
from spotipy import Spotify
from spotipy import util
import secrets
import sys

GOOGLE_PROVIDER = 'google'
SPOTIFY_PROVIDER = 'spotify'

class Track(object):
    def __init__(self, track_id, source, **kwargs):
        self.id = track_id
        self.source = source
        self.title = kwargs['title']
        self.artist = kwargs['artist']
        self.album = kwargs.get('album', None)
        self.year = kwargs.get('year', None)
        self.playlist = kwargs.get('playlist', None)
        self.duration = kwargs.get('duration', None)

    @staticmethod
    def from_google_track(track_dict):
        return Track(track_id=track_dict['id'],
                    source=GOOGLE_PROVIDER,
                    title=track_dict['track']['title'],
                    artist=track_dict['track']['albumArtist'],
                    album=track_dict['track']['album'],
                    year=track_dict['track']['year'])

    def __eq__(self, compared_track):
        if self.title != compared_track.title: return False
        if self.artist != compared_track.title: return False
        if self.album and compared_track.album:
            if self.album != compared_track.album: return False
        if self.year and compared_track.year:
            if self.year != compared_track.year: return False
        if self.duration and compared_track.duration:
            if self.duration != compared_track.duration: return False

        return True

    def search(self, search_method, provider):
        query = '{} {}'.format(self.artist, self.title)
        search_result = search_method(query)

        if provider == GOOGLE_PROVIDER:
            return [ Track.from_google_track(item['track']) for item in search_result['track_hits'] ]
        else:
            raise NotImplementedError


api = Mobileclient()
api.login(secrets.GMUSIC_EMAIL, secrets.GMUSIC_PASSWORD, Mobileclient.FROM_MAC_ADDRESS)
skip_playlist = []
gmusic_playlist_names = [ (playlist['name'], playlist['id']) for playlist in api.get_all_playlists() if str(playlist['name']) not in skip_playlist ]
# get spotify playlists

gmusic_tracks = []
for playlist in api.get_all_user_playlist_contents():
    if str(playlist['name']) not in skip_playlist:
        for track in playlist['tracks']:
            gmusic_tracks.append(Track.from_google_track(track))



# api.create_playlist(name, description=None)
# api.add_tracks_to_playlist(playlist_id, tracks_ids)
spotify_client_id = secrets.SPOTIFY_CLIENT_ID
spotify_client_secret = secrets.SPOTIFY_CLIENT_SECRET
spotify_redirect_uri = secrets.SPOTIFY_REDIRECT_URI
# login
# get playlist - skip specified ones
# create/update playlist
spotify_tracks = []
sp_oauth = oauth2.SpotifyOAuth(spotify_client_id, spotify_client_secret, spotify_redirect_uri, scope='user-library-read', cache_path='.cache-bogdan.music')

token = util.prompt_for_user_token(secrets.SPOTIFY_USER, 'user-library-read', 
                                   client_id=spotify_client_id,
                                   client_secret=spotify_client_secret)


sp_api = Spotify(auth=token)

found_tracks = []
not_found_tracks = []
for track in spotify_tracks:
    search_result = track.search(api.search, GOOGLE_PROVIDER)
    found = False
    for item in search_result:
        if track == item:
            item.playlist = track.playlist
            found_tracks.append(item)
            found = True
            break
    if not found: not_found_tracks.append(track)




