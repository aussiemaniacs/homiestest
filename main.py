#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import urllib.parse as urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import json

# Get addon info
addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
plugin_handle = int(sys.argv[1])
base_url = sys.argv[0]

def get_url(**kwargs):
    """Create a URL for calling the plugin"""
    return '{}?{}'.format(base_url, urlparse.urlencode(kwargs))

def list_categories():
    """Display main categories"""
    xbmcplugin.setPluginCategory(plugin_handle, 'MovieStream')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    categories = [
        ('Movies from TMDB', 'tmdb_movies', 'DefaultMovies.png'),
        ('GitHub Movies', 'github_movies', 'DefaultFolder.png'),
        ('Search Movies', 'search_movies', 'DefaultSearch.png'),
        ('Settings', 'settings', 'DefaultAddonProgram.png')
    ]
    
    for name, action, icon in categories:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': icon, 'icon': icon})
        url = get_url(action=action)
        is_folder = action != 'settings'
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, is_folder)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def get_tmdb_movies():
    """Get movies from TMDB API"""
    api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}'
    
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return None

def list_tmdb_movies():
    """List popular movies from TMDB"""
    xbmcplugin.setPluginCategory(plugin_handle, 'TMDB Movies')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    movies_data = get_tmdb_movies()
    if movies_data:
        for movie in movies_data.get('results', [])[:10]:  # Limit to 10 for demo
            title = movie.get('title', 'Unknown Title')
            year = movie.get('release_date', '')[:4] if movie.get('release_date') else ''
            plot = movie.get('overview', 'No description available')
            
            list_item = xbmcgui.ListItem(label=f"{title} ({year})" if year else title)
            
            # Set poster
            poster_path = movie.get('poster_path')
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                list_item.setArt({'thumb': poster_url, 'poster': poster_url})
            
            list_item.setInfo('video', {
                'title': title,
                'plot': plot,
                'year': int(year) if year.isdigit() else 0,
                'mediatype': 'movie'
            })
            list_item.setProperty('IsPlayable', 'true')
            
            url = get_url(action='play_sample')
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def get_github_movies():
    """Get movies from GitHub JSON"""
    github_url = addon.getSetting('github_repo_url') or 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
    movies_url = github_url + 'movies.json'
    
    try:
        response = requests.get(movies_url, timeout=10)
        return response.json()
    except:
        return []

def list_github_movies():
    """List movies from GitHub"""
    xbmcplugin.setPluginCategory(plugin_handle, 'GitHub Movies')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    movies = get_github_movies()
    for movie in movies:
        title = movie.get('title', 'Unknown')
        list_item = xbmcgui.ListItem(label=title)
        
        if movie.get('poster_url'):
            list_item.setArt({'thumb': movie['poster_url']})
        
        list_item.setInfo('video', {
            'title': title,
            'plot': movie.get('plot', ''),
            'year': movie.get('year', 0),
            'mediatype': 'movie'
        })
        list_item.setProperty('IsPlayable', 'true')
        
        url = get_url(action='play_github', video_url=movie.get('video_url', ''))
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def play_sample():
    """Play sample video"""
    sample_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    list_item = xbmcgui.ListItem(path=sample_url)
    xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)

def play_github(video_url):
    """Play video from GitHub database"""
    if video_url:
        list_item = xbmcgui.ListItem(path=video_url)
        xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
    else:
        xbmcgui.Dialog().notification('MovieStream', 'No video URL found', xbmcgui.NOTIFICATION_ERROR)

def search_movies():
    """Search for movies"""
    keyboard = xbmc.Keyboard('', 'Search Movies')
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if query:
            api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
            url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}'
            
            try:
                response = requests.get(url, timeout=10)
                results = response.json()
                
                xbmcplugin.setPluginCategory(plugin_handle, f'Search: {query}')
                xbmcplugin.setContent(plugin_handle, 'movies')
                
                for movie in results.get('results', [])[:10]:
                    title = movie.get('title', 'Unknown')
                    list_item = xbmcgui.ListItem(label=title)
                    
                    poster_path = movie.get('poster_path')
                    if poster_path:
                        list_item.setArt({'thumb': f"https://image.tmdb.org/t/p/w500{poster_path}"})
                    
                    list_item.setInfo('video', {
                        'title': title,
                        'plot': movie.get('overview', ''),
                        'mediatype': 'movie'
                    })
                    list_item.setProperty('IsPlayable', 'true')
                    
                    url = get_url(action='play_sample')
                    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
                
                xbmcplugin.endOfDirectory(plugin_handle)
            except:
                xbmcgui.Dialog().notification('MovieStream', 'Search failed', xbmcgui.NOTIFICATION_ERROR)

def open_settings():
    """Open addon settings"""
    addon.openSettings()

def router(paramstring):
    """Route to the appropriate function"""
    params = dict(urlparse.parse_qsl(paramstring))
    
    if params:
        action = params.get('action')
        
        if action == 'tmdb_movies':
            list_tmdb_movies()
        elif action == 'github_movies':
            list_github_movies()
        elif action == 'search_movies':
            search_movies()
        elif action == 'play_sample':
            play_sample()
        elif action == 'play_github':
            play_github(params.get('video_url'))
        elif action == 'settings':
            open_settings()
        else:
            list_categories()
    else:
        list_categories()

if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
File 3: movies.json (Root)
Click "Add file" → "Create new file"
Type filename: movies.json
Copy this content:
[
  {
    "id": "movie_001",
    "title": "Big Buck Bunny",
    "year": 2008,
    "genre": "Animation, Comedy, Short",
    "rating": 8.2,
    "plot": "A large and lovable rabbit deals with three tiny bullies, led by a flying squirrel, who are determined to squelch his happiness.",
    "director": "Sacha Goedegebure",
    "cast": ["Frank Dorrestein", "Maurits Delchot", "Jan Morgenstern"],
    "runtime": 10,
    "poster_url": "https://peach.blender.org/wp-content/uploads/bbb-splash.png",
    "backdrop_url": "https://peach.blender.org/wp-content/uploads/bbb-splash.png",
    "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    "trailer_url": "https://www.youtube.com/watch?v=YE7VzlLtp-4",
    "subtitles": [
      {
        "language": "en",
        "url": "https://gist.githubusercontent.com/samdutton/ca37f3adaf4e23679957b8083e061177/raw/e19399fbccbc069a2af4266e5120ae6bad62699a/sample.vtt"
      }
    ],
    "quality": "720p",
    "file_size": "158MB",
    "added_date": "2024-01-15",
    "tmdb_id": 10378
  },
  {
    "id": "movie_002", 
    "title": "Elephant's Dream",
    "year": 2006,
    "genre": "Animation, Science Fiction, Short",
    "rating": 7.3,
    "plot": "Emo and Proog are two men exploring a strange industrial world. The older and apparently more experienced Proog acts as a guide for Emo, leading him through dangerous, shifting mechanical environments.",
    "director": "Bassam Kurdali",
    "cast": ["Tygo Gernandt", "Cas Jansen"],
    "runtime": 11,
    "poster_url": "https://orange.blender.org/wp-content/themes/orange/images/media/gallery/s5_proog.jpg",
    "backdrop_url": "https://orange.blender.org/wp-content/themes/orange/images/media/gallery/s5_proog.jpg", 
    "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    "trailer_url": "https://www.youtube.com/watch?v=TLkA0RELQ1g",
    "subtitles": [
      {
        "language": "en",
        "url": "https://gist.githubusercontent.com/samdutton/ca37f3adaf4e23679957b8083e061177/raw/e19399fbccbc069a2af4266e5120ae6bad62699a/sample.vtt"
      }
    ],
    "quality": "480p",
    "file_size": "53MB", 
    "added_date": "2024-01-16",
    "tmdb_id": 2062
  },
  {
    "id": "movie_003",
    "title": "Sintel",
    "year": 2010,
    "genre": "Animation, Adventure, Fantasy, Short",
    "rating": 8.0,
    "plot": "A lonely young woman, Sintel, helps and befriends a dragon, whom she calls Scales. But when he is kidnapped by an adult dragon, Sintel decides to embark on a dangerous quest to find her lost friend Scales.",
    "director": "Colin Levy",
    "cast": ["Halina Reijn", "Thom Hoffman"],
    "runtime": 15,
    "poster_url": "https://durian.blender.org/wp-content/uploads/2010/05/sintel_trailer_400p.png",
    "backdrop_url": "https://durian.blender.org/wp-content/uploads/2010/05/sintel_trailer_400p.png",
    "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4", 
    "trailer_url": "https://www.youtube.com/watch?v=eRsGyueVLvQ",
    "subtitles": [
      {
        "language": "en",
        "url": "https://gist.githubusercontent.com/samdutton/ca37f3adaf4e23679957b8083e061177/raw/e19399fbccbc069a2af4266e5120ae6bad62699a/sample.vtt"
      }
    ],
    "quality": "1080p",
    "file_size": "347MB",
    "added_date": "2024-01-17", 
    "tmdb_id": 45745
  }
]
STEP 2: Create Folder Structure
Create resources/ Folder
Click "Create new file"
Type: resources/settings.xml (This creates the folder)
Copy this content:
<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<settings>
    <category label="32001">
        <setting id="tmdb_api_key" type="text" label="32002" default="d0f489a129429db6f2dd4751e5dbeb82" option="hidden" />
        <setting id="github_repo_url" type="text" label="32003" default="https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/" />
        <setting id="enable_github_sync" type="bool" label="32004" default="true" />
        <setting id="auto_update_metadata" type="bool" label="32005" default="true" />
    </category>
    <category label="32010">
        <setting id="video_quality" type="select" label="32011" default="720p" values="480p|720p|1080p|4K" />
        <setting id="subtitle_language" type="select" label="32012" default="en" values="en|es|fr|de|it|pt" />
        <setting id="enable_subtitles" type="bool" label="32013" default="true" />
        <setting id="buffer_size" type="slider" label="32014" default="5" range="1,1,20" option="int" />
    </category>
    <category label="32020">
        <setting id="cache_metadata" type="bool" label="32021" default="true" />
        <setting id="cache_duration" type="slider" label="32022" default="24" range="1,1,168" option="int" />
        <setting id="clear_cache" type="action" label="32023" action="RunPlugin(plugin://plugin.video.moviestream/?action=clear_cache)" />
    </category>
</settings>
