#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MovieStream - FIXED VERSION (Correct setResolvedUrl spelling)
The issue was using setResolvedURL instead of setResolvedUrl!
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
    xbmcplugin.setPluginCategory(plugin_handle, 'MovieStream FIXED')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    categories = [
        ('🎬 Movies (TMDB)', 'movies', 'DefaultMovies.png'),
        ('📁 GitHub Collection', 'github_collection', 'DefaultFolder.png'),
        ('🔍 Search Movies', 'search_movies', 'DefaultSearch.png'),
        ('🎮 TEST PLAYBACK', 'test_playback', 'DefaultAddonProgram.png'),
        ('⚙️ Settings', 'settings', 'DefaultAddonProgram.png')
    ]
    
    for name, action, icon in categories:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': icon, 'icon': icon})
        list_item.setInfo('video', {'title': name, 'genre': 'Directory'})
        
        url = get_url(action=action)
        is_folder = action not in ['settings', 'test_playback']
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, is_folder)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def test_playback():
    """Test playback with correct method name"""
    xbmc.log("=== TESTING PLAYBACK WITH CORRECT METHOD ===", xbmc.LOGINFO)
    
    try:
        # Test URL that should definitely work
        test_url = "https://www.w3schools.com/html/mov_bbb.mp4"
        
        # Show notification
        xbmcgui.Dialog().notification('Testing', 'Starting playback test...', xbmcgui.NOTIFICATION_INFO, 2000)
        
        # Create ListItem
        list_item = xbmcgui.ListItem(label="Test Video", path=test_url)
        list_item.setInfo('video', {
            'title': 'Test Video',
            'plot': 'Testing Kodi playback',
            'mediatype': 'movie'
        })
        list_item.setProperty('IsPlayable', 'true')
        
        # FIXED: Use correct method name (lowercase 'l' in 'Url')
        xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
        xbmc.log("SUCCESS: setResolvedUrl called successfully!", xbmc.LOGINFO)
        
        # Show success notification
        xbmcgui.Dialog().notification('Success!', 'Test video should be playing!', xbmcgui.NOTIFICATION_INFO, 3000)
        
    except Exception as e:
        error_msg = str(e)
        xbmc.log(f"TEST ERROR: {error_msg}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Test Error', f'Error: {error_msg}')

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
            # Show only first 10 movies for easier testing
            for movie in movies.get('results', [])[:10]:
                add_movie_item(movie)
            
            # Add next page
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
    """Add a movie item - FIXED VERSION"""
    title = movie.get('title', 'Unknown Title')
    year = movie.get('release_date', '')[:4] if movie.get('release_date') else ''
    plot = movie.get('overview', 'No description available')
    
    # Create display title
    display_title = f"{title} ({year})" if year else title
    list_item = xbmcgui.ListItem(label=display_title)
    
    # Set artwork
    poster_path = movie.get('poster_path')
    if poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        list_item.setArt({'thumb': poster_url, 'poster': poster_url})
    
    backdrop_path = movie.get('backdrop_path')
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
    
    # CRITICAL: Set as playable
    list_item.setProperty('IsPlayable', 'true')
    
    # Create movie data for playback
    movie_data = {
        'title': title,
        'year': str(year),
        'tmdb_id': str(movie.get('id', '')),
        'plot': plot
    }
    
    # Create URL for playback
    url = get_url(action='play_movie', movie_data=json.dumps(movie_data))
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)

def play_movie(movie_data_str):
    """Play a movie - CORRECTED VERSION"""
    xbmc.log("=== PLAY_MOVIE CALLED (FIXED VERSION) ===", xbmc.LOGINFO)
    
    try:
        movie_data = json.loads(movie_data_str)
        title = movie_data.get('title', 'Unknown Movie')
        
        # Show loading notification
        xbmcgui.Dialog().notification('MovieStream', f'Loading {title}...', xbmcgui.NOTIFICATION_INFO, 2000)
        xbmc.log(f"Playing movie: {title}", xbmc.LOGINFO)
        
        # Multiple test URLs
        test_urls = [
            "https://www.w3schools.com/html/mov_bbb.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
        ]
        
        # Try first working URL
        for video_url in test_urls:
            try:
                xbmc.log(f"Trying URL: {video_url}", xbmc.LOGINFO)
                
                # Create ListItem
                list_item = xbmcgui.ListItem(label=title, path=video_url)
                list_item.setInfo('video', {
                    'title': title,
                    'plot': movie_data.get('plot', ''),
                    'mediatype': 'movie'
                })
                list_item.setProperty('IsPlayable', 'true')
                
                # FIXED: Use correct method name (lowercase 'l' in 'Url')
                xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
                xbmc.log("SUCCESS: Movie playback initiated!", xbmc.LOGINFO)
                
                # Show success notification
                xbmcgui.Dialog().notification('Success!', f'{title} should be playing!', xbmcgui.NOTIFICATION_INFO, 3000)
                return  # Exit on success
                
            except Exception as url_error:
                xbmc.log(f"URL {video_url} failed: {str(url_error)}", xbmc.LOGERROR)
                continue
        
        # If all URLs failed
        raise Exception("All video URLs failed")
        
    except Exception as e:
        error_msg = str(e)
        xbmc.log(f"CRITICAL ERROR in play_movie: {error_msg}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Playback Error', f'Error: {error_msg}')
        xbmcgui.Dialog().notification('MovieStream', 'Playback failed', xbmcgui.NOTIFICATION_ERROR)

def github_collection():
    """Show GitHub collection - FIXED VERSION"""
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
            
            # Use direct URL if available, otherwise use play_movie
            video_url = movie.get('video_url')
            if video_url:
                url = get_url(action='play_direct', video_url=video_url, title=title)
            else:
                url = get_url(action='play_movie', movie_data=json.dumps(movie))
            
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    except Exception as e:
        xbmc.log(f"Error loading GitHub collection: {str(e)}", xbmc.LOGERROR)
        list_item = xbmcgui.ListItem(label='❌ Error loading collection')
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def play_direct(video_url, title):
    """Play direct video URL - FIXED VERSION"""
    xbmc.log(f"Playing direct URL: {video_url}", xbmc.LOGINFO)
    
    try:
        list_item = xbmcgui.ListItem(label=title, path=video_url)
        list_item.setInfo('video', {'title': title, 'mediatype': 'movie'})
        list_item.setProperty('IsPlayable', 'true')
        
        # FIXED: Use correct method name
        xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
        xbmc.log("Direct play successful!", xbmc.LOGINFO)
        
    except Exception as e:
        xbmc.log(f"Direct play error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Direct Play Error', str(e))

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
                
                for movie in results.get('results', [])[:15]:  # Limit to 15 results
                    add_movie_item(movie)
                
                xbmcplugin.endOfDirectory(plugin_handle)
                
            except Exception as e:
                xbmc.log(f"Search error: {str(e)}", xbmc.LOGERROR)
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
        elif action == 'test_playback':
            test_playback()
        elif action == 'settings':
            open_settings()
        else:
            list_categories()
    else:
        list_categories()

if __name__ == '__main__':
    try:
        xbmc.log("=== MOVIESTREAM CORRECTED VERSION STARTING ===", xbmc.LOGINFO)
        router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
    except Exception as e:
        xbmc.log(f"CRITICAL STARTUP ERROR: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Startup Error', str(e))