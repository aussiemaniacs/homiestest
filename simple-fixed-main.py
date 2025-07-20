#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MovieStream - Quick Fixed Version
This version fixes the main playback issue while keeping it simple
"""

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
        ('🎬 Movies (TMDB)', 'movies', 'DefaultMovies.png'),
        ('📁 GitHub Collection', 'github_collection', 'DefaultFolder.png'),
        ('🔍 Search Movies', 'search_movies', 'DefaultSearch.png'),
        ('⚙️ Settings', 'settings', 'DefaultAddonProgram.png')
    ]
    
    for name, action, icon in categories:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': icon, 'icon': icon})
        list_item.setInfo('video', {'title': name, 'genre': 'Directory'})
        
        url = get_url(action=action)
        is_folder = action != 'settings'
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, is_folder)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def list_movies(page=1):
    """List popular movies from TMDB"""
    xbmcplugin.setPluginCategory(plugin_handle, 'Movies')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page={page}'
    
    try:
        response = requests.get(url, timeout=10)
        movies = response.json()
        
        if movies:
            for movie in movies.get('results', []):
                add_movie_item(movie)
            
            # Add next page if available
            if page < movies.get('total_pages', 1):
                list_item = xbmcgui.ListItem(label='➡️ Next Page >>')
                list_item.setArt({'thumb': 'DefaultFolder.png'})
                url = get_url(action='movies', page=page + 1)
                xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
        
        xbmcplugin.endOfDirectory(plugin_handle)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error loading movies: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Failed to load movies', xbmcgui.NOTIFICATION_ERROR)

def add_movie_item(movie):
    """Add a movie item to the directory - FIXED VERSION"""
    title = movie.get('title', 'Unknown Title')
    year = movie.get('release_date', '')[:4] if movie.get('release_date') else ''
    plot = movie.get('overview', 'No description available')
    
    # Create display title
    display_title = f"{title} ({year})" if year else title
    list_item = xbmcgui.ListItem(label=display_title)
    
    # Set artwork
    poster_path = movie.get('poster_path')
    backdrop_path = movie.get('backdrop_path')
    
    if poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        list_item.setArt({'thumb': poster_url, 'poster': poster_url})
    
    if backdrop_path:
        fanart_url = f"https://image.tmdb.org/t/p/w1280{backdrop_path}"
        list_item.setArt({'fanart': fanart_url})
    
    # Set video info
    list_item.setInfo('video', {
        'title': title,
        'plot': plot,
        'year': int(year) if year.isdigit() else 0,
        'rating': float(movie.get('vote_average', 0)),
        'votes': str(movie.get('vote_count', 0)),
        'mediatype': 'movie'
    })
    
    # CRITICAL FIX: Set as playable - THIS WAS MISSING!
    list_item.setProperty('IsPlayable', 'true')
    
    # Create movie data for playback
    movie_data = {
        'title': title,
        'year': str(year),
        'tmdb_id': str(movie.get('id', '')),
        'plot': plot
    }
    
    # CRITICAL FIX: Use proper URL parameters
    url = get_url(action='play_movie', movie_data=json.dumps(movie_data))
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)

def play_movie(movie_data_str):
    """Play a movie - FIXED VERSION"""
    xbmc.log("MovieStream: PLAY_MOVIE CALLED - THIS IS THE FIX!", xbmc.LOGINFO)
    
    try:
        movie_data = json.loads(movie_data_str)
        title = movie_data.get('title', 'Unknown Movie')
        
        # Show immediate feedback to user
        xbmcgui.Dialog().notification('MovieStream', f'Loading {title}...', xbmcgui.NOTIFICATION_INFO, 2000)
        xbmc.log(f"MovieStream: Playing movie: {title}", xbmc.LOGINFO)
        
        # For now, play a sample video (you can add Cocoscrapers later)
        sample_urls = [
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"
        ]
        
        # Use first sample for now
        video_url = sample_urls[0]
        
        # CRITICAL: Create ListItem and set resolved URL
        list_item = xbmcgui.ListItem(label=title, path=video_url)
        list_item.setInfo('video', {
            'title': title,
            'plot': movie_data.get('plot', ''),
            'mediatype': 'movie'
        })
        
        # Set resolved URL - THIS MAKES IT PLAY!
        xbmcplugin.setResolvedURL(plugin_handle, True, list_item)
        xbmc.log("MovieStream: Successfully set resolved URL", xbmc.LOGINFO)
        
        # Show success message
        xbmcgui.Dialog().notification('MovieStream', 'Playing sample video!', xbmcgui.NOTIFICATION_INFO)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Critical error in play_movie: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Playback failed', xbmcgui.NOTIFICATION_ERROR)

def github_collection():
    """Show GitHub collection"""
    xbmcplugin.setPluginCategory(plugin_handle, 'GitHub Collection')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    try:
        github_url = addon.getSetting('github_repo_url') or 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
        movies_url = github_url + 'movies.json'
        
        response = requests.get(movies_url, timeout=10)
        movies = response.json()
        
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
            
            # For GitHub movies, play directly if URL exists
            video_url = movie.get('video_url')
            if video_url:
                url = get_url(action='play_direct', video_url=video_url, title=title)
            else:
                url = get_url(action='play_movie', movie_data=json.dumps(movie))
            
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    except Exception as e:
        xbmc.log(f"MovieStream: Error loading GitHub collection: {str(e)}", xbmc.LOGERROR)
        list_item = xbmcgui.ListItem(label='❌ Error loading GitHub collection')
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def play_direct(video_url, title):
    """Play direct video URL"""
    try:
        list_item = xbmcgui.ListItem(label=title, path=video_url)
        list_item.setInfo('video', {'title': title, 'mediatype': 'movie'})
        xbmcplugin.setResolvedURL(plugin_handle, True, list_item)
        xbmc.log(f"MovieStream: Playing direct URL: {video_url}", xbmc.LOGINFO)
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing direct URL: {str(e)}", xbmc.LOGERROR)

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
                
                for movie in results.get('results', [])[:20]:
                    add_movie_item(movie)
                
                xbmcplugin.endOfDirectory(plugin_handle)
                
            except Exception as e:
                xbmc.log(f"MovieStream: Search error: {str(e)}", xbmc.LOGERROR)
                xbmcgui.Dialog().notification('MovieStream', 'Search failed', xbmcgui.NOTIFICATION_ERROR)

def open_settings():
    """Open addon settings"""
    addon.openSettings()

def router(paramstring):
    """Route to the appropriate function"""
    params = dict(urlparse.parse_qsl(paramstring))
    
    if params:
        action = params.get('action')
        
        if action == 'movies':
            list_movies(int(params.get('page', 1)))
        elif action == 'play_movie':
            play_movie(params.get('movie_data', '{}'))
        elif action == 'play_direct':
            play_direct(params.get('video_url', ''), params.get('title', 'Video'))
        elif action == 'search_movies':
            search_movies()
        elif action == 'github_collection':
            github_collection()
        elif action == 'settings':
            open_settings()
        else:
            list_categories()
    else:
        list_categories()

if __name__ == '__main__':
    try:
        xbmc.log("MovieStream: Starting FIXED addon", xbmc.LOGINFO)
        router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
    except Exception as e:
        xbmc.log(f"MovieStream: Critical startup error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Critical error - check log', xbmcgui.NOTIFICATION_ERROR)