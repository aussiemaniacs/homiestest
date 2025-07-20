#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MovieStream - COMPLETE FIXED VERSION
Fixed setResolvedUrl and enhanced GitHub collection error handling
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
    xbmc.log("=== TESTING PLAYBACK ===", xbmc.LOGINFO)
    
    try:
        test_url = "https://www.w3schools.com/html/mov_bbb.mp4"
        
        xbmcgui.Dialog().notification('Testing', 'Starting playback test...', xbmcgui.NOTIFICATION_INFO, 2000)
        
        list_item = xbmcgui.ListItem(label="Test Video", path=test_url)
        list_item.setInfo('video', {'title': 'Test Video', 'plot': 'Testing Kodi playback', 'mediatype': 'movie'})
        list_item.setProperty('IsPlayable', 'true')
        
        xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
        xbmc.log("SUCCESS: Test playback initiated!", xbmc.LOGINFO)
        
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
            for movie in movies.get('results', [])[:10]:
                add_movie_item(movie)
            
            if page < movies.get('total_pages', 1):
                list_item = xbmcgui.ListItem(label='➡️ Next Page >>')
                list_item.setArt({'thumb': 'DefaultFolder.png'})
                url = get_url(action='movies', page=page + 1)
                xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
        
        xbmcplugin.endOfDirectory(plugin_handle)
        
    except Exception as e:
        xbmc.log(f"Error loading movies: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Failed to load movies', xbmcgui.NOTIFICATION_ERROR)

def add_movie_item(movie):
    """Add a movie item"""
    title = movie.get('title', 'Unknown Title')
    year = movie.get('release_date', '')[:4] if movie.get('release_date') else ''
    plot = movie.get('overview', 'No description available')
    
    display_title = f"{title} ({year})" if year else title
    list_item = xbmcgui.ListItem(label=display_title)
    
    poster_path = movie.get('poster_path')
    if poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        list_item.setArt({'thumb': poster_url, 'poster': poster_url})
    
    backdrop_path = movie.get('backdrop_path')
    if backdrop_path:
        fanart_url = f"https://image.tmdb.org/t/p/w1280{backdrop_path}"
        list_item.setArt({'fanart': fanart_url})
    
    list_item.setInfo('video', {
        'title': title,
        'plot': plot,
        'year': int(year) if year.isdigit() else 0,
        'rating': float(movie.get('vote_average', 0)),
        'votes': str(movie.get('vote_count', 0)),
        'mediatype': 'movie'
    })
    
    list_item.setProperty('IsPlayable', 'true')
    
    movie_data = {
        'title': title,
        'year': str(year),
        'tmdb_id': str(movie.get('id', '')),
        'plot': plot
    }
    
    url = get_url(action='play_movie', movie_data=json.dumps(movie_data))
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)

def play_movie(movie_data_str):
    """Play a movie - CORRECTED VERSION"""
    xbmc.log("=== PLAY_MOVIE CALLED ===", xbmc.LOGINFO)
    
    try:
        movie_data = json.loads(movie_data_str)
        title = movie_data.get('title', 'Unknown Movie')
        
        xbmcgui.Dialog().notification('MovieStream', f'Loading {title}...', xbmcgui.NOTIFICATION_INFO, 2000)
        xbmc.log(f"Playing movie: {title}", xbmc.LOGINFO)
        
        test_urls = [
            "https://www.w3schools.com/html/mov_bbb.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
        ]
        
        for video_url in test_urls:
            try:
                xbmc.log(f"Trying URL: {video_url}", xbmc.LOGINFO)
                
                list_item = xbmcgui.ListItem(label=title, path=video_url)
                list_item.setInfo('video', {
                    'title': title,
                    'plot': movie_data.get('plot', ''),
                    'mediatype': 'movie'
                })
                list_item.setProperty('IsPlayable', 'true')
                
                xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
                xbmc.log("SUCCESS: Movie playback initiated!", xbmc.LOGINFO)
                
                xbmcgui.Dialog().notification('Success!', f'{title} should be playing!', xbmcgui.NOTIFICATION_INFO, 3000)
                return
                
            except Exception as url_error:
                xbmc.log(f"URL {video_url} failed: {str(url_error)}", xbmc.LOGERROR)
                continue
        
        raise Exception("All video URLs failed")
        
    except Exception as e:
        error_msg = str(e)
        xbmc.log(f"CRITICAL ERROR in play_movie: {error_msg}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Playback Error', f'Error: {error_msg}')
        xbmcgui.Dialog().notification('MovieStream', 'Playback failed', xbmcgui.NOTIFICATION_ERROR)

def github_collection():
    """Show GitHub collection - ENHANCED ERROR HANDLING"""
    xbmcplugin.setPluginCategory(plugin_handle, 'GitHub Collection')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    try:
        # Get GitHub URL from settings
        github_url = addon.getSetting('github_repo_url')
        xbmc.log(f"GitHub URL from settings: {github_url}", xbmc.LOGINFO)
        
        # Use default if not set
        if not github_url or github_url.strip() == '':
            github_url = 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
            xbmc.log(f"Using default GitHub URL: {github_url}", xbmc.LOGINFO)
        
        # Ensure URL ends with slash
        if not github_url.endswith('/'):
            github_url += '/'
        
        # Construct movies.json URL
        movies_url = github_url + 'movies.json'
        xbmc.log(f"Fetching movies from: {movies_url}", xbmc.LOGINFO)
        
        # Show loading notification
        xbmcgui.Dialog().notification('GitHub Collection', 'Loading movies...', xbmcgui.NOTIFICATION_INFO, 2000)
        
        # Try to fetch the JSON
        response = requests.get(movies_url, timeout=15)
        xbmc.log(f"HTTP Response Code: {response.status_code}", xbmc.LOGINFO)
        
        if response.status_code != 200:
            raise Exception(f"HTTP Error {response.status_code}: {response.reason}")
        
        # Try to parse JSON
        try:
            movies = response.json()
            xbmc.log(f"Successfully parsed JSON. Found {len(movies)} movies", xbmc.LOGINFO)
        except json.JSONDecodeError as json_error:
            raise Exception(f"Invalid JSON format: {str(json_error)}")
        
        # Check if movies is a list
        if not isinstance(movies, list):
            raise Exception(f"Expected list of movies, got {type(movies)}")
        
        if len(movies) == 0:
            # Show empty collection message
            list_item = xbmcgui.ListItem(label='📭 No movies found in collection')
            list_item.setInfo('video', {
                'title': 'Empty Collection',
                'plot': f'No movies found at {movies_url}\n\nCheck your GitHub repository or add movies.json file.'
            })
            xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
        else:
            # Add movies to the list
            for i, movie in enumerate(movies):
                try:
                    xbmc.log(f"Processing movie {i+1}: {movie.get('title', 'No title')}", xbmc.LOGINFO)
                    add_github_movie_item(movie, i+1)
                except Exception as movie_error:
                    xbmc.log(f"Error processing movie {i+1}: {str(movie_error)}", xbmc.LOGERROR)
                    continue
            
            # Show success notification
            xbmcgui.Dialog().notification('GitHub Collection', f'Loaded {len(movies)} movies successfully!', xbmcgui.NOTIFICATION_INFO, 3000)
    
    except requests.exceptions.ConnectionError:
        error_msg = f"Connection failed to {movies_url}\n\nCheck your internet connection or GitHub URL."
        show_github_error("Connection Error", error_msg)
        
    except requests.exceptions.Timeout:
        error_msg = f"Request timed out to {movies_url}\n\nTry again later or check GitHub URL."
        show_github_error("Timeout Error", error_msg)
        
    except Exception as e:
        error_msg = f"Error: {str(e)}\n\nURL: {movies_url}\n\nTips:\n• Check GitHub repository URL in settings\n• Ensure movies.json exists\n• Verify JSON format"
        show_github_error("GitHub Collection Error", error_msg)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def add_github_movie_item(movie, index):
    """Add a GitHub movie item with better error handling"""
    title = movie.get('title', f'Movie {index}')
    
    list_item = xbmcgui.ListItem(label=title)
    
    # Set artwork if available
    poster_url = movie.get('poster_url')
    if poster_url and poster_url.strip():
        try:
            list_item.setArt({'thumb': poster_url, 'poster': poster_url})
        except Exception as art_error:
            xbmc.log(f"Error setting artwork for {title}: {str(art_error)}", xbmc.LOGWARNING)
    
    # Set video info
    list_item.setInfo('video', {
        'title': title,
        'plot': movie.get('plot', movie.get('description', 'No description available')),
        'year': int(movie.get('year', 0)) if str(movie.get('year', '')).isdigit() else 0,
        'genre': movie.get('genre', ''),
        'rating': float(movie.get('rating', 0)) if movie.get('rating') else 0,
        'mediatype': 'movie'
    })
    
    list_item.setProperty('IsPlayable', 'true')
    
    # Determine playback URL
    video_url = movie.get('video_url')
    m3u8_url = movie.get('m3u8_url')
    
    if video_url and video_url.strip():
        # Direct video URL
        url = get_url(action='play_direct', video_url=video_url, title=title)
        xbmc.log(f"GitHub movie '{title}' has direct video URL", xbmc.LOGINFO)
    elif m3u8_url and m3u8_url.strip():
        # M3U8 streaming URL
        url = get_url(action='play_direct', video_url=m3u8_url, title=title)
        xbmc.log(f"GitHub movie '{title}' has M3U8 URL", xbmc.LOGINFO)
    else:
        # No direct URL - use movie data (will play sample video)
        url = get_url(action='play_movie', movie_data=json.dumps(movie))
        xbmc.log(f"GitHub movie '{title}' has no direct URL - will use sample", xbmc.LOGINFO)
    
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)

def show_github_error(title, message):
    """Show GitHub error in both notification and list item"""
    # Show notification
    xbmcgui.Dialog().notification('GitHub Error', 'Check collection settings', xbmcgui.NOTIFICATION_ERROR, 5000)
    
    # Add error item to list
    list_item = xbmcgui.ListItem(label='❌ GitHub Collection Error')
    list_item.setInfo('video', {
        'title': title,
        'plot': message
    })
    
    # Add settings action
    url = get_url(action='settings')
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    # Add test URL item
    list_item2 = xbmcgui.ListItem(label='🔧 Test GitHub Connection')
    list_item2.setInfo('video', {
        'title': 'Test Connection', 
        'plot': 'Click to test your GitHub repository connection'
    })
    url2 = get_url(action='test_github_connection')
    xbmcplugin.addDirectoryItem(plugin_handle, url2, list_item2, False)

def test_github_connection():
    """Test GitHub connection and show detailed results"""
    try:
        # Get URL from settings
        github_url = addon.getSetting('github_repo_url') or 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
        if not github_url.endswith('/'):
            github_url += '/'
        
        movies_url = github_url + 'movies.json'
        
        # Show testing notification
        xbmcgui.Dialog().notification('Testing', 'Checking GitHub connection...', xbmcgui.NOTIFICATION_INFO, 3000)
        
        # Test connection
        response = requests.get(movies_url, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    success_msg = f"✅ Connection Successful!\n\nURL: {movies_url}\nStatus: {response.status_code}\nMovies found: {len(data)}\n\nFirst movie: {data[0].get('title', 'No title') if data else 'None'}"
                else:
                    success_msg = f"⚠️ Connected but JSON is not a list\n\nURL: {movies_url}\nType: {type(data)}\nContent: {str(data)[:100]}..."
            except json.JSONDecodeError as json_err:
                success_msg = f"⚠️ Connected but invalid JSON\n\nURL: {movies_url}\nJSON Error: {str(json_err)}\nContent preview: {response.text[:200]}..."
            
            xbmcgui.Dialog().ok('GitHub Test Results', success_msg)
        else:
            error_msg = f"❌ Connection Failed\n\nURL: {movies_url}\nHTTP Status: {response.status_code}\nError: {response.reason}\n\nCheck if the file exists and URL is correct."
            xbmcgui.Dialog().ok('GitHub Test Results', error_msg)
    
    except requests.exceptions.ConnectionError:
        error_msg = f"❌ No Internet Connection\n\nCannot reach: {movies_url}\n\nCheck your internet connection."
        xbmcgui.Dialog().ok('Connection Error', error_msg)
    
    except Exception as e:
        error_msg = f"❌ Test Failed\n\nError: {str(e)}\nURL: {movies_url}"
        xbmcgui.Dialog().ok('Test Error', error_msg)

def play_direct(video_url, title):
    """Play direct video URL - FIXED VERSION"""
    xbmc.log(f"Playing direct URL: {video_url}", xbmc.LOGINFO)
    
    try:
        list_item = xbmcgui.ListItem(label=title, path=video_url)
        list_item.setInfo('video', {'title': title, 'mediatype': 'movie'})
        list_item.setProperty('IsPlayable', 'true')
        
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
                
                for movie in results.get('results', [])[:15]:
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
        elif action == 'test_github_connection':
            test_github_connection()
        elif action == 'settings':
            open_settings()
        else:
            list_categories()
    else:
        list_categories()

if __name__ == '__main__':
    try:
        xbmc.log("=== MOVIESTREAM COMPLETE FIXED VERSION STARTING ===", xbmc.LOGINFO)
        router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
    except Exception as e:
        xbmc.log(f"CRITICAL STARTUP ERROR: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Startup Error', str(e))