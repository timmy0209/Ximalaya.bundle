# coding=utf-8
# Rewrite (use JSON API, other matching tweaks) by Timmy

import time
import os
import json
import os, string, hashlib, base64, re, plistlib, unicodedata
import config
from collections import defaultdict
from io import open

ARTIST_URL_WANGYI = 'http://music.163.com/api/v1/artist/'
LYRIC_URL_WANGYI = 'https://music.163.com/api/song/lyric?id='

XIMALAYA_SEARCH_BY_ALBUM = 'https://www.ximalaya.com/revision/search/main?core=album&kw='
XIMALAYA_SEARCH_ARTIST = 'https://www.ximalaya.com/revision/search/main?core=user&kw='
XIMALAYA_ARTIST_ALBUM = 'https://www.ximalaya.com/revision/user/pub?uid='
XIMALAYA_ARTIST_URL = 'https://www.ximalaya.com/revision/user/basic?uid='
XIMALAYA_TRACK_URL = 'http://mobile.ximalaya.com/mobile/v1/album/track?albumId='
XIMALAYA_ALBUM_INFO = 'https://www.ximalaya.com/revision/album/v1/simple?albumId='


# Tunables.
ARTIST_MATCH_LIMIT = 9 # Max number of artists to fetch for matching purposes.
ARTIST_MATCH_MIN_SCORE = 85 # Minimum score required to add to custom search results.
ARTIST_MANUAL_MATCH_LIMIT = 120 # Number of artists to fetch when trying harder for manual searches.  Multiple API hits.
ARTIST_SEARCH_PAGE_SIZE = 30 # Number of artists in a search result page.  Asking for more has no effect.
ARTIST_ALBUMS_MATCH_LIMIT = 3 # Max number of artist matches to try for album bonus.  Each one incurs an additional API request.
ARTIST_ALBUMS_LIMIT = 50 # Number of albums by artist to grab for artist matching bonus and quick album match.
ARTIST_MIN_LISTENER_THRESHOLD = 250 # Minimum number of listeners for an artist to be considered credible.
ARTIST_MATCH_GOOD_SCORE = 90 # Include artists with this score or higher regardless of listener count.
ALBUM_MATCH_LIMIT = 8 # Max number of results returned from standalone album searches with no artist info (e.g. Various Artists).
ALBUM_MATCH_MIN_SCORE = 75 # Minimum score required to add to custom search results.
ALBUM_MATCH_GOOD_SCORE = 92 # Minimum score required to rely on only Albums by Artist and not search.
ALBUM_TRACK_BONUS_MATCH_LIMIT = 5 # Max number of albums to try for track bonus.  Each one incurs at most one API request per album.
QUERY_SLEEP_TIME = 0.1 # How long to sleep before firing off each API request.

# Advanced tunables.
NAME_DISTANCE_THRESHOLD = 2 # How close do album/track names need to be to match for bonuses?
ARTIST_INITIAL_SCORE = 90 # Starting point for artists before bonus/deductions.
ARTIST_ALBUM_BONUS_INCREMENT = 3 # How much to boost the bonus for a each good artist/album match.
ARTIST_ALBUM_MAX_BONUS = 15 # Maximum number of bonus points to give artists with good album matches.
ARTIST_MAX_DIST_PENALTY = 40 # Maxiumum amount to penalize for Lev ratio difference in artist names.
ALBUM_INITIAL_SCORE = 92 # Starting point for albums before bonus/deductions.
ALBUM_NAME_DIST_COEFFICIENT = 5 # Multiply album Lev. distance to give it a bit more weight.
ALBUM_TRACK_BONUS_INCREMENT = 3 # How much to boost the bonus for a each good album/track match.
ALBUM_TRACK_MAX_BONUS = 20 # Maximum number of bonus points to give to albums with good track name matches.
ALBUM_TRACK_BONUS_MAX_ARTIST_DSIT = 2 # How similar do the parent artist and album search result artist need to be to ask for info?
ALBUM_NUM_TRACKS_BONUS = 1 # How much to boost the bonus if the total number of tracks match.

RE_STRIP_PARENS = Regex('\([^)]*\)')

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'origin': 'https://y.qq.com',
    'referer': 'https://y.qq.com/portal/playlist.html'
}

def Start():
  HTTP.CacheTime = CACHE_1WEEK

# Change pinyin
def multi_get_letter(str_input): 
  if isinstance(str_input, unicode): 
    unicode_str = str_input 
  else: 
    try: 
      unicode_str = str_input.decode('utf8') 
    except: 
      try: 
        unicode_str = str_input.decode('gbk') 
      except: 
        print 'unknown coding'
        return
  return_list = [] 
  #for one_unicode in unicode_str: 
   # return_list.append(single_get_first(one_unicode)) 
  #return return_list
  return single_get_first(unicode_str)

def single_get_first(unicode1): 
  str1 = unicode1.encode('gbk') 
  try:     
    ord(str1) 
    return str1 
  except: 
    asc = ord(str1[0]) * 256 + ord(str1[1]) - 65536
    if asc >= -20319 and asc <= -20284: 
      return 'a'
    if asc >= -20283 and asc <= -19776: 
      return 'b'
    if asc >= -19775 and asc <= -19219: 
      return 'c'
    if asc >= -19218 and asc <= -18711: 
      return 'd'
    if asc >= -18710 and asc <= -18527: 
      return 'e'
    if asc >= -18526 and asc <= -18240: 
      return 'f'
    if asc >= -18239 and asc <= -17923: 
      return 'g'
    if asc >= -17922 and asc <= -17418: 
      return 'h'
    if asc >= -17417 and asc <= -16475: 
      return 'j'
    if asc >= -16474 and asc <= -16213: 
      return 'k'
    if asc >= -16212 and asc <= -15641: 
      return 'l'
    if asc >= -15640 and asc <= -15166: 
      return 'm'
    if asc >= -15165 and asc <= -14923: 
      return 'n'
    if asc >= -14922 and asc <= -14915: 
      return 'o'
    if asc >= -14914 and asc <= -14631: 
      return 'p'
    if asc >= -14630 and asc <= -14150: 
      return 'q'
    if asc >= -14149 and asc <= -14091: 
      return 'r'
    if asc >= -14090 and asc <= -13119: 
      return 's'
    if asc >= -13118 and asc <= -12839: 
      return 't'
    if asc >= -12838 and asc <= -12557: 
      return 'w'
    if asc >= -12556 and asc <= -11848: 
      return 'x'
    if asc >= -11847 and asc <= -11056: 
      return 'y'
    if asc >= -11055 and asc <= -10247: 
      return 'z'
    return ''

def pinyin(str_input): 
  b = ''
  if isinstance(str_input, unicode): 
    unicode_str = str_input 
  else: 
    try: 
      unicode_str = str_input.decode('utf8')
    except: 
      try: 
        unicode_str = str_input.decode('gbk')
      except: 
        #print 'unknown coding'
        return  
  for i in range(len(unicode_str)):
    b=b+single_get_first(unicode_str[i])
  return b.upper()
  

# Score lists of artist results.  Permutes artist_results list.
def score_artists(artists, media_artist, media_albums, lang, artist_results):
  
  for i, artist in enumerate(artists):

    id = str(artist['uid'])
    #Log("??????ID:")
    #Log(id)
    # Search returns ordered results, but no numeric score, so we approximate one with Levenshtein ratio.
    #Log("????????????")
    #Log(media_artist.lower())
    dist = int(ARTIST_MAX_DIST_PENALTY - ARTIST_MAX_DIST_PENALTY * LevenshteinRatio(artist['nickname'].lower(), media_artist.lower()))
    #Log("????????????")
    #Log(artist['nickname'])
    #Log("????????????")
    #Log(dist)
    #Log("??????dist")
    #Log(dist)
    if artist['nickname'].lower() == media_artist.lower():
      dist = dist - 1
    # Fetching albums in order to apply bonus is expensive, so only do it for the top N artist matches.
    if i < ARTIST_ALBUMS_MATCH_LIMIT:
      bonus = get_album_bonus(media_albums, artist_id=id)
      #Log("????????????")
      #Log(bonus)
    else:
      bonus = 0
    Log("????????????")
    # Adjust the score.
    score = ARTIST_INITIAL_SCORE + bonus - dist
    
    Log(score)
    # Finally, apply some heuristics based on listener count. If there's only a single result, it will not include the 'listeners' key.
    # Single results tend to be a good matches. Distrust artists with fewer than N listeners if it was not a really good match.
    #
    #if len(artists) > 1 and artist.has_key('listeners') and int(artist['listeners']) < ARTIST_MIN_LISTENER_THRESHOLD and score < ARTIST_MATCH_GOOD_SCORE:
    #  Log('Skipping %s with only %s listeners and score of %s.' % (artist['name'], artist['listeners'], score))
    #  continue
    
    name = artist['nickname']
    #listeners = artist['listeners'] if artist.has_key('listeners') else '(no listeners data)'
    #Log('Artist result: ' + name + ' dist: ' + str(dist) + ' album bonus: ' + str(bonus) + ' listeners: ' + str(listeners) + ' score: ' + str(score))
    
    # Skip matches that don't meet the minimum score.  There many be many, especially if this was a manual search.
    if score >= ARTIST_MATCH_MIN_SCORE:
      artist_results.append(MetadataSearchResult(id=id, name=name, lang=lang, score=score))
    else:
      Log('Skipping artist, didn\'t meet minimum score of ' + str(ARTIST_MATCH_MIN_SCORE))
      
    # Sort the resulting artists.
    artist_results.sort(key=lambda r: r.score, reverse=True)    

# Get albums by artist and boost artist match score accordingly.  Returns bonus (int) of 0 - ARTIST_ALBUM_MAX_BONUS.
def get_album_bonus(media_albums, artist_id):
  
  Log('?????????????????????')
  bonus = 0
  albums = GetAlbumsByArtist(artist_id, albums=[], limit=ARTIST_ALBUMS_LIMIT)
  
  try:
    for a in media_albums:    
      media_album = a.lower()
      #Log("??????????????????")
      #Log(media_album)
      for album in albums:
        # If the album title is close enough to the media title, boost the score.
        #Log("???????????????")
        #Log(album['title'].lower())
        #Log("?????????")
        #Log(Util.LevenshteinDistance(media_album,album['title'].lower()))
        if Util.LevenshteinDistance(media_album,album['title'].lower()) <= NAME_DISTANCE_THRESHOLD: #????????????2
          bonus += ARTIST_ALBUM_BONUS_INCREMENT
        
        # This is a cheap comparison, so let's try again with the contents of parentheses removed, e.g. "(limited edition)"
        elif Util.LevenshteinDistance(media_album,RE_STRIP_PARENS.sub('',album['title'].lower())) <= NAME_DISTANCE_THRESHOLD:
          bonus += ARTIST_ALBUM_BONUS_INCREMENT
        
        # Stop trying once we hit the max bonus.
        if bonus >= ARTIST_ALBUM_MAX_BONUS:
          break
  
  except Exception, e:
    Log('Error applying album bonus: ' + str(e))
  if bonus > 0:
    Log('Applying album bonus of: ' + str(bonus))
  return bonus



class Ximalaya(Agent.Artist):
  name = 'Ximalaya'
  languages = [Locale.Language.Chinese]
  
  def score_by_albums(self, media, lang,local_albums_name, albums, manual=False):
    res = []
    matches = []
    for j, album in enumerate(albums):
      try:
        name = album['title']
        Log("??????????????????" + name)
        id = str(album['albumId'])
        Log("id??????" + id)
        #dist = Util.LevenshteinDistance(name.lower(),local_albums_name.lower()) * ALBUM_NAME_DIST_COEFFICIENT  #???????????????
        #Log("??????????????????")
        #Log(dist)
        score = ALBUM_INITIAL_SCORE - j * 10    #92 - ?????????
        Log("???????????????")
        Log(score)
        res.append({'id':album['uid'], 'name':album['nickname'], 'lang':lang, 'score':score,'album_id':id, 'album_name':name, 'year':1990})
      
      except:
        Log('Error scoring album.')

    if res:
      res = sorted(res, key=lambda k: k['score'], reverse=True)
      Log(res)
      for i, result in enumerate(res):
        # Fetching albums to apply track bonus is expensive, so only do it for the top N results. ????????????5???????????????????????????
        if i < ALBUM_TRACK_BONUS_MATCH_LIMIT:
          Log("id=:"+ result['album_id'])
          Log("???????????????"+ result['album_name'])
          bonus = self.get_track_bonus(media, result['album_id'], lang)
          Log(bonus)
          res[i]['score'] = res[i]['score'] + bonus
          Log(res[i]['score'])
        # Append albums that meet the minimum score, skip the rest.
        if res[i]['score'] >= ALBUM_MATCH_MIN_SCORE or manual:
          Log('Album result: ' + result['name'] + ' album bonus: ' + str(bonus) + ' score: ' + str(result['score']))
          matches.append(res[i])
        else:
          Log('Skipping %d album results that don\'t meet the minimum score of %d.' % (len(res) - i, ALBUM_MATCH_MIN_SCORE))
          break

    # Sort once more to account for track bonus and return.
    if matches:
      return sorted(matches, key=lambda k: k['score'], reverse=True)
    else:
      return matches
    
  def get_track_bonus(self, media, album_id, lang):
    track_num,tracks = GetTracks(media.id,str(album_id), lang)
    bonus = 0
    #try:
    for i, t in enumerate(media.children[0].children):  #??????15?????????????????????
      media_track = t.title.lower()
      #Log("??????????????????" + media_track)
      for j, track in enumerate(tracks):

        # If the names are close enough, boost the score.
        #Log("??????????????????" + track['title'] + "????????????")
        #Log(Util.LevenshteinDistance(track['title'].lower(), media_track))
        if Util.LevenshteinDistance(track['title'].lower(), media_track) <  5:
          bonus += ALBUM_TRACK_BONUS_INCREMENT
      if i > 10:
        break

    # If the albums have the same number of tracks, boost more.
    if abs(len(media.children) - int(track_num)) < 6:
      Log('?????????????????????6')
      bonus += 5
    
    # Cap the bonus.
    if bonus >= ALBUM_TRACK_MAX_BONUS:
      bonus = ALBUM_TRACK_MAX_BONUS

    #except:
    #  Log('Didn\'t find any usable tracks in search results, not applying track bonus.')

    if bonus > 0:
      Log('Applying track bonus of: ' + str(bonus))
    return bonus

  
  def search(self, results, media, lang, manual):

    media_albums = [a.title for a in media.children]
    Log("???????????????")
    Log(media_albums)
    
    # Handle a couple of edge cases where artist search will give bad results.
    if media.artist == '[Unknown Artist]':
      Log('?????????????????????????????????????????????')
      artist_byalbums = self.score_by_albums(media, lang,media_albums[0], SearchAlbums(media_albums[0].lower(), ALBUM_MATCH_LIMIT), manual=manual)
      for artist in artist_byalbums:
        results.Append(MetadataSearchResult(id = str(artist['id']), name= artist['name'], lang  = lang, score = int(artist['score'])))
      return
    
    if media.artist == 'Various Artists':
      results.Append(MetadataSearchResult(id = 'Various%20Artists', name= 'Various Artists', thumb = VARIOUS_ARTISTS_POSTER, lang  = lang, score = 100))
      return

    # Search for artist.
    Log('????????????: ' + media.artist)
    if manual:
      Log('Running custom search...')
    artist_results = []

    artists = SearchArtists(media.artist, ARTIST_MATCH_LIMIT)
    if artists:
      # Score the first N results.
      score_artists(artists, media.artist, media_albums, lang, artist_results)
      Log(artist_results)
      if artist_results :
        for artist in artist_results:
          results.Append(artist)
      else:
        Log('??????????????????????????????????????????????????????')
        artist_byalbums = self.score_by_albums(media, lang,media_albums[0], SearchAlbums(media_albums[0].lower(), ALBUM_MATCH_LIMIT), manual=manual)
        for artist in artist_byalbums:
          results.Append(MetadataSearchResult(id = str(artist['id']), name= artist['name'], lang  = lang, score = int(artist['score'])))
        return
    else:
      Log('??????????????????????????????????????????????????????')
      artist_byalbums = self.score_by_albums(media, lang,media_albums[0], SearchAlbums(media_albums[0].lower(), ALBUM_MATCH_LIMIT), manual=manual)
      for artist in artist_byalbums:
        results.Append(MetadataSearchResult(id = str(artist['id']), name= artist['name'], lang  = lang, score = int(artist['score'])))
      return


  def update(self, metadata, media, lang):
    artist = GetArtist(metadata.id, lang)
    
    # Name.
    try:
      metadata.title = artist['nickName']
      Log(metadata.title)
      metadata.title_sort = pinyin(metadata.title)
    except:
      pass
    # Bio.
    try:
      metadata.summary = artist['personalSignature'].strip()
      Log(metadata.summary )
    except:
      pass

    # Artwork.
    try:
      if artist['nickName'] == 'Various Artists':
          metadata.posters[VARIOUS_ARTISTS_POSTER] = Proxy.Media(HTTP.Request(VARIOUS_ARTISTS_POSTER))
      else:       
          metadata.posters['https:'+artist['cover']] = Proxy.Media(HTTP.Request('https:'+artist['cover']))
    except:
        Log('Couldn\'t add artwork for artist.')

  
class XimalayaAgent(Agent.Album):
  name = 'Ximalaya'
  languages = [Locale.Language.Chinese]
  accepts_from = ['com.plexapp.agents.localmedia','com.plexapp.agents.lyricfind']
  
  def search(self, results, media, lang, manual):

    # Handle a couple of edge cases where album search will give bad results.
    Log('????????????')
    albums = []

    if manual:
      # If this is a custom search, use the user-entered name instead of the scanner hint.
      try:
        Log('????????????: ' + media.name)
        media.title = media.name
      except:
        pass
    else:
      Log('????????????: ' + media.title)
    
    found_good_match = False

    #????????????????????????
    if media.parent_metadata.id is None:
      Log('media.parent_metadata.id is None')
      albums = self.score_by_albums(media, lang, SearchAlbums(media.name.lower(), ALBUM_MATCH_LIMIT), manual=manual) + albums
      Log(albums)
      seen = {}
      deduped = []
      for album in albums:
        if album['id'] in seen:
          continue
        seen[album['id']] = True
        deduped.append(album)
      albums = deduped

      Log('Found ' + str(len(albums)) + ' albums...')

      # Limit to 10 albums.
      albums = albums[:10]
      Log(albums)
      for i,album in enumerate(albums):
        if album['score'] > 0:
          score = album['score']
          if score >= 100:
            score = 99 - i
          Log(album['score'])
          Log(album['id'])
          Log(album['name'])
          Log(album['lang'])
          results.Append(MetadataSearchResult(id = str(album['id']), name = album['name'], lang = album['lang'], score = str(score)))
      return

    
    if media.parent_metadata.id == '[Unknown Album]':
      return #eventually, we might be able to look at tracks to match the album

    # Search for album.

    # First try matching in the list of albums by artist for single-artist albums.
    if media.parent_metadata.id != 'Various%20Artists':

      # Start with the first N albums (ideally a single API request).
      if not manual:
        albums = self.score_albums(media, lang, GetAlbumsByArtist(media.parent_metadata.id, albums=[]))
        Log('????????????')
        Log(albums)
        # Check for a good match within these reults.  If we find one, set the flag to stop looking.
        if albums and albums[0]['score'] >= ALBUM_MATCH_GOOD_SCORE:
          found_good_match = True
          Log('Good album match found (quick search) with score: ' + str(albums[0]['score']))

      # If we haven't found a good match yet, or we're running a custom search, get all albums by artist.  May be thousands
      # of albums and several API requests to complete this list, so we use it sparingly.
      if manual:
        if manual:
          Log('Custom search terms specified, fetching all albums by artist.')
        else:
          Log('No good matches found in first ' + str(len(albums)) + ' albums, fetching all albums by artist.')
        albums = self.score_albums(media, lang, GetAlbumsByArtist(media.parent_metadata.id, albums=[]), manual=manual)
        Log('????????????')
        Log(albums)
        # If we find a good match this way, set the flag to stop looking.
        if albums and albums[0]['score'] >= ALBUM_MATCH_GOOD_SCORE:
          Log('Good album match found with score: ' + str(albums[0]['score']))
          found_good_match = True
        else:
          Log('No good matches found in ' + str(len(albums)) + ' albums by artist.')

    # Either we're looking at Various Artists, or albums by artist search did not contain a good match.
    # Last.fm mysteriously omits certain (often popular) albums from albums-by-artist results, so it's
    # important to fall back even in the case of single-artist albums.

    #???????????????
    if not found_good_match or not albums:
      Log('??????????????????????????? ??????????????????')
      albums = self.score_by_albums(media, lang, SearchAlbums(media.title.lower(), ALBUM_MATCH_LIMIT), manual=manual) + albums
      
    # Dedupe albums.
    seen = {}
    deduped = []
    for album in albums:
      if album['id'] in seen:
        continue
      seen[album['id']] = True
      deduped.append(album)
    albums = deduped

    Log('Found ' + str(len(albums)) + ' albums...')

    # Limit to 10 albums.
    albums = albums[:10]
    Log(albums)
    for i,album in enumerate(albums):
        if album['score'] > 0:
          score = album['score']
          if score >= 100:
            score = 99 - i
          Log(album['score'])
          Log(album['id'])
          Log(album['name'])
          Log(album['lang'])
          results.Append(MetadataSearchResult(id = str(album['id']), name = album['name'], lang = album['lang'], score = str(score)))
    return
  def score_by_albums(self, media, lang, albums, manual=False):
    res = []
    matches = []
    for j, album in enumerate(albums):
      #try:
        name = album['title']
        Log("??????????????????" + name)
        id = str(album['albumId'])
        Log("id??????" + id)
        score = ALBUM_INITIAL_SCORE - j * 10    #92-?????????
        Log("???????????????")
        Log(score)
        res.append({'id':id, 'name':name, 'lang':lang, 'score':score})
      
      #except:
      #  Log('Error scoring album.')

    if res:
      res = sorted(res, key=lambda k: k['score'], reverse=True)
      Log(res)
      for i, result in enumerate(res):
        # Fetching albums to apply track bonus is expensive, so only do it for the top N results. ????????????5???????????????????????????
        if i < ALBUM_TRACK_BONUS_MATCH_LIMIT:
          Log("id=:"+ result['id'])
          Log("???????????????"+ result['name'])
          bonus = self.get_track_bonus(media, result['id'], lang)
          Log(bonus)
          res[i]['score'] = res[i]['score'] + bonus
          Log(res[i]['score'])
        # Append albums that meet the minimum score, skip the rest.
        if res[i]['score'] >= ALBUM_MATCH_MIN_SCORE or manual:
          Log('Album result: ' + result['name'] + ' album bonus: ' + str(bonus) + ' score: ' + str(result['score']))
          matches.append(res[i])
        else:
          Log('Skipping %d album results that don\'t meet the minimum score of %d.' % (len(res) - i, ALBUM_MATCH_MIN_SCORE))
          break

    # Sort once more to account for track bonus and return.
    if matches:
      return sorted(matches, key=lambda k: k['score'], reverse=True)
    else:
      return matches
    
  # Score a list of albums, return a fresh list of scored matches above the ALBUM_MATCH_MIN_SCORE threshold.
  def score_albums(self, media, lang, albums, manual=False):
    res = []
    matches = []
    for album in albums:
      try:
        name = album['title']
        Log("??????????????????" + name)
        
        # Sanitize artist.  Last.fm sometimes returns a string, sometimes a list.
        #if album.has_key('artist'):
        #  if not isinstance(album['artist'], basestring):
        #    artist = album['artist']['name']
        #  else:
        #    artist = album['artist']
        #else:
        #  artist = ''
        #Log("??????????????????" + artist)
        #id = media.parent_metadata.id + '/' + String.Quote(album['name'].decode('utf-8').encode('utf-8')).replace(' ','+')
        id =  str(album['id'])
        Log("??????+?????? id??????" + id)
        dist = Util.LevenshteinDistance(name.lower(),media.title.lower()) * ALBUM_NAME_DIST_COEFFICIENT  #???????????????
        Log("??????????????????")
        Log(dist)
        artist_dist = 100
        # Freeform album searches will come back with wacky artists.  If they're not close, penalize heavily, skipping them.
        #for artist in album['artists']:
        #  Log("?????????" + artist['anchorNickName'])
        if Util.LevenshteinDistance(album['anchorNickName'].lower(),String.Unquote(media.parent_metadata.title).lower()) < artist_dist :     #????????????
            artist_dist = Util.LevenshteinDistance(album['anchorNickName'].lower(),String.Unquote(media.parent_metadata.title).lower())
        Log("????????????")
        Log(artist_dist)
        if artist_dist > ALBUM_TRACK_BONUS_MAX_ARTIST_DSIT:
          artist_dist = 1000
          Log('?????????????????? ' + album['anchorNickName'])
        
        # Apply album and artist penalties and append to temp results list.
        score = ALBUM_INITIAL_SCORE - dist - artist_dist
        Log("???????????????")
        Log(score)
        res.append({'id':id, 'name':name, 'lang':lang, 'score':score})
      
      except:
        Log('Error scoring album.')

    if res:
      res = sorted(res, key=lambda k: k['score'], reverse=True)
      Log(res)
      for i, result in enumerate(res):
        # Fetching albums to apply track bonus is expensive, so only do it for the top N results. ??????????????????????????????????????????
        if i < ALBUM_TRACK_BONUS_MATCH_LIMIT:
          Log("id=:"+ result['id'])
          Log("???????????????"+ result['name'])
          bonus = self.get_track_bonus(media, result['id'], lang)
          Log(bonus)
          res[i]['score'] = res[i]['score'] + bonus
          Log(res[i]['score'])
        # Append albums that meet the minimum score, skip the rest.
        if res[i]['score'] >= ALBUM_MATCH_MIN_SCORE or manual:
          Log('Album result: ' + result['name'] + ' album bonus: ' + str(bonus) + ' score: ' + str(result['score']))
          matches.append(res[i])
        else:
          Log('Skipping %d album results that don\'t meet the minimum score of %d.' % (len(res) - i, ALBUM_MATCH_MIN_SCORE))
          break

    # Sort once more to account for track bonus and return.
    if matches:
      return sorted(matches, key=lambda k: k['score'], reverse=True)
    else:
      return matches
  
  # Get album info in order to compare track listings and apply bonus accordingly.  Return a bonus (int) of 0 - ALBUM_TRACK_MAX_BONUS.
  def get_track_bonus(self, media, album_id, lang):
    track_num,tracks = GetTracks(media.parent_metadata.id,str(album_id), lang)
    bonus = 0
    try:
      for i, t in enumerate(media.children):  #??????15?????????????????????
        media_track = t.title.lower()
        #Log("??????????????????" + media_track)
        for j, track in enumerate(tracks):

          # If the names are close enough, boost the score.
          #Log("??????????????????" + track['title'] + "????????????")
          #Log(Util.LevenshteinDistance(track['title'].lower(), media_track))
          if Util.LevenshteinDistance(track['title'].lower(), media_track) <  NAME_DISTANCE_THRESHOLD:
            bonus += ALBUM_TRACK_BONUS_INCREMENT
        if i > 15:
          break

      # If the albums have the same number of tracks, boost more.
      if abs(len(media.children) - int(track_num)) < 6:
        #Log('?????????????????????6')
        bonus += 5
      
      # Cap the bonus.
      if bonus >= ALBUM_TRACK_MAX_BONUS:
        bonus = ALBUM_TRACK_MAX_BONUS

    except:
      Log('Didn\'t find any usable tracks in search results, not applying track bonus.')

    if bonus > 0:
      Log('Applying track bonus of: ' + str(bonus))
    return bonus
 
  def update(self, metadata, media, lang):
    #media.parentTitle = '????????????'
    album = GetAlbum(metadata.id, lang)
    if not album:
      return

    # Title.
    metadata.title = album['albumTitle']
    
    # Artwork.
    try:
      valid_keys = 'http:' + album['cover']
      metadata.posters[valid_keys] = Proxy.Media(HTTP.Request(valid_keys))
      metadata.posters.validate_keys(valid_keys)
    except:
      Log('Couldn\'t add artwork for album.')

    # Release Date.
    try:
      #Log(Datetime.ParseDate(time.strftime("%Y-%m-%d", time.localtime(int(int(album['publishTime'])/1000)))))
      #metadata.originally_available_at = Datetime.ParseDate(time.strftime("%Y-%m-%d", time.localtime(int(int(album['publishTime'])/1000))))
      metadata.originally_available_at = Datetime.ParseDate(album['createDate'])
    except:
      Log('Couldn\'t add release date to album.')
      
    # ??????
    try:
      detailRichIntro = album['detailRichIntro']
      html_elem = HTML.ElementFromString(detailRichIntro)
      summary = ''
      for i in html_elem.xpath('//p'):
          summary = summary + ''.join(i.xpath('.//text()')) + '\n'
      metadata.summary = summary
      Log(metadata.summary)
      metadata.studio = '????????????'
      Log("?????????id??????")
      Log(metadata.id)
      #Log(media.id)
    except:
      Log("??????????????????")
    # Genres.
    metadata.genres.clear()
    try:
        for genre in Listify(album['tags']):
          metadata.genres.add(genre.capitalize())
    except:
        Log('Couldn\'t add genre tags to album.')


  
    for index in media.tracks:
      key = media.tracks[index].guid or int(index)
      Log("key:")
      Log(key)
      Log(index)
      Log(media.tracks[index])
      Log(metadata.tracks[key].original_title)
      metadata.tracks[key].original_title = media.parentTitle
      Log(media.tracks[index].items)
      Log(media.tracks[index].title)
      if index == '29' :
        t = metadata.tracks[key]
        t.name = '????????????'
        Log('??????')
        media.tracks[index].title = '????????????'



    # Top tracks.
    most_popular_tracks = {}
    try:
      top_tracks = GetArtistTopTracks(metadata.id.split('/')[0], lang)
      #Log(top_tracks)
      for track in top_tracks:
        most_popular_tracks[track['name']] = int(track['pop'])
      Log("???????????????")
      Log(most_popular_tracks)
    except:
      pass
    valid_keys = defaultdict(list)
    for index in media.tracks:
      key = media.tracks[index].guid or int(index)
      Log("key:")
      Log(key)
      Log(index)
      Log(media.tracks[index])
      Log(media.tracks[index].items)
      track_id = '0'
      metadata.tracks[key].original_title = media.parentTitle
      Log(media.parentTitle)
      '''
      for track in album['songs'] :
        Log(track['name'])
        Log(media.tracks[index].title)
        Log(LevenshteinRatio(track["name"], media.tracks[index].title))
        if track and LevenshteinRatio(track["name"], media.tracks[index].title) > 0.9:
          t = metadata.tracks[key]
          t.rating_count = int(track["popularity"])
          Log("t.rating_count:")
          Log(t.rating_count)
          track_id = track["id"]
          art = []
          for artist in track["artists"] :
            art.append(artist['name'])
          Log('/'.join(art))
          t.original_title = '/'.join(art)
          
      for item in media.tracks[index].items:
        for part in item.parts:
          filename = part.file
          path = os.path.dirname(filename)
          (file_root, fext) = os.path.splitext(filename)

          path_files = {}

          if len(path) > 0:
            for p in os.listdir(path):
              path_files[p.lower()] = p
          #Log(path_files)
          
          # Look for lyrics.
          lrc_exist = False
          file = (file_root + '.lrc')
          file2 = (file_root + '.txt')
          #Log("file:")
          #Log(file)
          if os.path.exists(file):
            Log('Found a lyric in %s', file)
            metadata.tracks[key].lyrics[file] = Proxy.LocalFile(file, format='lrc')
            valid_keys[key].append(file)
            lrc_exist = True 
          if not lrc_exist :
            Log(track_id)
            Log("???????????????????????? ????????????????????????:")
            if not (track_id == '0') :
              if Prefs['lyc']:
                Log(track_id)
                lyricinfo = DownlodeLyric(track_id)
                lyric = lyricinfo['lrc']['lyric']
                Log(lyric)
                #tlyric = lyricinfo['tlyric']['lyric']
                #Log(tlyric)
                if lyric is not None :
                    Log("????????????LYRIC")    
                    with open(file,'w+',encoding='utf8') as f:
                        f.write(lyric)
                        f.close()
                    metadata.tracks[key].lyrics[file] = Proxy.LocalFile(file, format='lrc')
                    valid_keys[key].append(file)
                #elif tlyric is not None :
                    #Log("????????????TXT")
                    #with open(file2,'w+',encoding='utf8') as f:
                    #    f.write(tlyric)
                    #    f.close()
                    #metadata.tracks[key].lyrics[file2] = Proxy.LocalFile(file2, format='txt')
                    #valid_keys[key].append(file2)
                else:
                      Log("??????????????????")
            else:
              Log('?????????????????????????????????????????????????????????')                
              
              
      Log(valid_keys)    
      for k in metadata.tracks:
        metadata.tracks[k].lyrics.validate_keys(valid_keys[k])    
      #for popular_track in most_popular_tracks.keys():
        #Log("popular_track:")
        #Log(popular_track)
        #Log("media.tracks[index].title :")
        #Log(media.tracks[index].title)
        #Log("????????????????????????????????????")
        #Log(LevenshteinRatio(popular_track, media.tracks[index].title))
        #if popular_track and LevenshteinRatio(popular_track, media.tracks[index].title) > 0.95:
        #  t = metadata.tracks[key]
        #  Log("t :")
        #  Log(t)
        #  if Prefs['popular']:
        #    t.rating_count = most_popular_tracks[popular_track]
        #  else:
        #    t.rating_count = 0
        #  Log("t.rating_count:")
        #  Log(t.rating_count)
    '''

def DownlodeLyric(trackid):
  url =LYRIC_URL_WANGYI + str(trackid) + '&lv=1&tv=1'
  Log(url)
  try: 
    response = GetJSON(url)
  except:
    Log('Error retrieving lrc search results.')
  return response 
  
      
def SearchArtists(artist, limit=10):
  artists = []

  if not artist:
    Log('Missing artist. Skipping match')
    return artists
  try:
    a = artist.lower().encode('utf-8')
  except:
    a = artist.lower()
  Log(a)
  url = XIMALAYA_SEARCH_ARTIST + String.Quote(a)
  Log(url)
  try: 
    response = GetJSON(url)
    num = int(response['data']['user']['total'])
  except:
    Log('Error retrieving artist search results.')
    return artists
    
  lim = min(limit,num)
  Log('???????????????????????????')
  Log(lim)
  for i in range(lim):
    try:
      artist_results = response['data']['user']
      artists = artists + Listify(artist_results['docs'])
    except:
      Log('Error retrieving artist search results.')
  # Since LFM has lots of garbage artists that match garbage inputs, we'll only consider ones that have
  # either a MusicBrainz ID or artwork.
  #
  #valid_artists = [a for a in artists if a['mbid'] or (len(a.get('image', [])) > 0 and a['image'][0].get('#text', None))]
  #if len(artists) != len(valid_artists):
  #  Log('Skipping artist results because they lacked artwork or MBID: %s' % ', '.join({a['name'] for a in artists}.difference({a['name'] for a in valid_artists})))

  #return valid_artists
  return artists


def SearchAlbums(album, limit=10, legacy=False):
  albums = []

  if not album:
    Log('Missing album. Skipping match')
    return albums

  try:
    a = album.lower().encode('utf-8')
  except:
    a = album.lower()
  Log("??????????????????" + a)
  url = XIMALAYA_SEARCH_BY_ALBUM + String.Quote(a)
  try:
    response = GetJSON(url)
    if response.has_key('error'):
      Log('??????????????????: ' + response['message'])
      return albums
    else:
      album_results = response['data']['album']['docs']
      albums = Listify(album_results)
  except:
    Log('Error retrieving album search results.')

  return albums


def GetAlbumsByArtist(artist_id, limit=ARTIST_ALBUMS_LIMIT*4,albums=[], legacy=True):
  Log("????????????id" + artist_id)
  url = XIMALAYA_ARTIST_ALBUM + artist_id
  response = GetJSON(url)
  try:
    albums.extend(Listify(response['data']['albumList']))
  except:
    # Sometimes the API will lie and say there's an Nth page of results, but the last one will return garbage.
    pass
  return albums


def GetArtist(id, lang='en'):
  url = XIMALAYA_ARTIST_URL + id
  try:
    artist_results = GetJSON(url)
    if artist_results.has_key('error'):
      Log('Error retrieving artist metadata: ' + artist_results['message'])
      return {}
    return artist_results['data']
  except:
    Log('Error retrieving artist metadata.')
    return {}


def GetAlbum(album_id, lang='en'):
  url = XIMALAYA_ALBUM_INFO + album_id
  try:
    album_results = GetJSON(url)
    if album_results.has_key('error'):
      Log('Error retrieving album metadata: ' + album_results['msg'])
      return {}
    return album_results['data']['albumPageMainInfo']
  except:
    Log('Error retrieving album metadata.')
    return {}


def GetTracks(artist_id, album_id, lang='en'):
  url = XIMALAYA_TRACK_URL + album_id + '&pageId=1&pageSize=50' #??????????????????200???
  try:
    tracks_result = GetJSON(url)
    return tracks_result['data']['totalCount'], Listify(tracks_result['data']['list'])  #?????????????????????????????????
  except:
    Log('Error retrieving tracks.')
    return '0',[]


def GetArtistTopTracks(artist_id, lang='en'):
  result = []
  url = ARTIST_URL_WANGYI + artist_id.lower()
  Log(url)
  top_tracks_result = GetJSON(url)
  total_pages = 15
  if len(top_tracks_result['hotSongs']) <= 15 :
      total_pages = len(top_tracks_result['hotSongs'])
  try:
    page = 0
    Log("??????????????????95???pop")
    #for songs in Listify(top_tracks_result['hotSongs']):
    for songs in top_tracks_result['hotSongs']:
      Log("????????????" +  songs['name'])
      Log("?????????")
      Log(songs['pop'])
      if int(songs['pop']) >= 95 :
        new_results = songs
        result.append(new_results)
      # Get out if we've exceeded the number of pages.
      #page += 1
      #if page > total_pages:
      #  break
  except:
    Log('Exception getting top tracks.')
  return result

def GetArtistSimilar(artist_id, lang='en'):
  url = ARTIST_SIMILAR_ARTISTS_URL % (artist_id.lower(), lang)
  try:
    similar_artists_result = GetJSON(url)
    if similar_artists_result.has_key('error'):
      Log('Error receiving similar artists: ' + similar_artists_result['message'])
      return []
    if isinstance(similar_artists_result['similarartists']['artist'], list) or isinstance(similar_artists_result['similarartists']['artist'], dict):
      return Listify(similar_artists_result['similarartists']['artist'])
  except:
    Log('Exception getting similar artists.')
    return []


def GetJSON(url, sleep_time=QUERY_SLEEP_TIME, cache_time=CACHE_1MONTH):
  d = None
  try:
    d = JSON.ObjectFromURL(url, sleep=sleep_time, cacheTime=cache_time, headers=headers)
    if isinstance(d, dict):
      return d
  except:
    Log('Error fetching JSON.')
    return None


def LevenshteinRatio(first, second):
  return 1 - (Util.LevenshteinDistance(first, second) / float(max(len(first), len(second))))

def NormalizeArtist(name):
  return Core.messaging.call_external_function('com.plexapp.agents.plexmusic', 'MessageKit:NormalizeArtist', kwargs = dict(artist=name))

# Utility functions for sanitizing Last.fm API responses.
def Listify(obj):
  if isinstance(obj, list):
    return obj
  else:
    return [obj]

def Dictify(obj, key=''):
  if isinstance(obj, dict):
    return obj
  else:
    return {key:obj}
