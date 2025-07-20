#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MovieStream - Enhanced Debugging Version
This version has extensive logging to find the exact issue
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
    xbmcplugin.setPluginCategory(plugin_handle, 'MovieStream DEBUG')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    categories = [
        ('🎬 Movies (TMDB)', 'movies', 'DefaultMovies.png'),
        ('📁 GitHub Collection', 'github_collection', 'DefaultFolder.png'),
        ('🔍 Search Movies', 'search_movies', 'DefaultSearch.png'),
        ('🎮 TEST DIRECT PLAY', 'test_direct_play', 'DefaultAddonProgram.png'),
        ('⚙️ Settings', 'settings', 'DefaultAddonProgram.png')
    ]
    
    for name, action, icon in categories:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': icon, 'icon': icon})
        list_item.setInfo('video', {'title': name, 'genre': 'Directory'})
        
        url = get_url(action=action)
        is_folder = action != 'settings' and action != 'test_direct_play'
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, is_folder)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def test_direct_play():
    """Test direct playback - ULTIMATE DEBUG"""
    xbmc.log("=== DIRECT PLAY TEST STARTED ===", xbmc.LOGINFO)
    
    try:
        # Test with multiple different approaches
        test_urls = [
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
            "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4"
        ]
        
        for i, test_url in enumerate(test_urls):
            xbmc.log(f"Testing URL {i+1}: {test_url}", xbmc.LOGINFO)
            
            # Show notification
            xbmcgui.Dialog().notification('Debug Test', f'Testing URL {i+1}/3', xbmcgui.NOTIFICATION_INFO, 3000)
            
            # Create ListItem
            list_item = xbmcgui.ListItem(label=f"Test Video {i+1}", path=test_url)
            list_item.setInfo('video', {
                'title': f'Test Video {i+1}',
                'plot': 'Direct playback test',
                'mediatype': 'movie'
            })
            list_item.setProperty('IsPlayable', 'true')
            
            # Try to play
            xbmcplugin.setResolvedURL(plugin_handle, True, list_item)
            xbmc.log(f"setResolvedURL called for URL {i+1}", xbmc.LOGINFO)
            
            # Only test first one for now
            break
            
    except Exception as e:
        error_msg = str(e)
        xbmc.log(f"DIRECT TEST ERROR: {error_msg}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Test Error', f'Direct test failed: {error_msg}')

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
            # Add only first 5 movies for testing
            for movie in movies.get('results', [])[:5]:
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
    """Add a movie item to the directory - ENHANCED DEBUG VERSION"""
    title = movie.get('title', 'Unknown Title')
    year = movie.get('release_date', '')[:4] if movie.get('release_date') else ''
    plot = movie.get('overview', 'No description available')
    
    xbmc.log(f"Adding movie: {title} ({year})", xbmc.LOGINFO)
    
    # Create display title
    display_title = f"{title} ({year})" if year else title
    list_item = xbmcgui.ListItem(label=display_title)
    
    # Set artwork
    poster_path = movie.get('poster_path')
    if poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        list_item.setArt({'thumb': poster_url, 'poster': poster_url})
        xbmc.log(f"Set poster: {poster_url}", xbmc.LOGINFO)
    
    # Set video info
    list_item.setInfo('video', {
        'title': title,
        'plot': plot,
        'year': int(year) if year.isdigit() else 0,
        'rating': float(movie.get('vote_average', 0)),
        'mediatype': 'movie'
    })
    
    # CRITICAL: Set as playable
    list_item.setProperty('IsPlayable', 'true')
    xbmc.log(f"Set IsPlayable=true for {title}", xbmc.LOGINFO)
    
    # Create movie data for playback
    movie_data = {
        'title': title,
        'year': str(year),
        'tmdb_id': str(movie.get('id', '')),
        'plot': plot
    }
    
    # Create URL
    url = get_url(action='play_movie', movie_data=json.dumps(movie_data))
    xbmc.log(f"Created play URL: {url[:100]}...", xbmc.LOGINFO)
    
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    xbmc.log(f"Added directory item for {title}", xbmc.LOGINFO)

def play_movie(movie_data_str):
    """Play a movie - ULTRA DEBUG VERSION"""
    xbmc.log("=== PLAY_MOVIE FUNCTION CALLED ===", xbmc.LOGINFO)
    xbmc.log(f"Raw movie_data parameter: {movie_data_str[:200]}...", xbmc.LOGINFO)
    
    try:
        # Parse movie data
        movie_data = json.loads(movie_data_str)
        title = movie_data.get('title', 'Unknown Movie')
        xbmc.log(f"Parsed movie data - Title: {title}", xbmc.LOGINFO)
        
        # Show loading notification
        xbmcgui.Dialog().notification('MovieStream DEBUG', f'Loading {title}...', xbmcgui.NOTIFICATION_INFO, 3000)
        xbmc.log(f"Showed loading notification for: {title}", xbmc.LOGINFO)
        
        # Test multiple video URLs
        test_urls = [
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
            "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4"
        ]
        
        # Try each URL until one works
        for i, video_url in enumerate(test_urls):
            xbmc.log(f"Trying video URL {i+1}: {video_url}", xbmc.LOGINFO)
            
            try:
                # Create ListItem
                xbmc.log("Creating ListItem...", xbmc.LOGINFO)
                list_item = xbmcgui.ListItem(label=title, path=video_url)
                
                # Set info
                xbmc.log("Setting video info...", xbmc.LOGINFO)
                list_item.setInfo('video', {
                    'title': title,
                    'plot': movie_data.get('plot', ''),
                    'mediatype': 'movie'
                })
                
                # Set properties
                xbmc.log("Setting properties...", xbmc.LOGINFO)
                list_item.setProperty('IsPlayable', 'true')
                
                # Test URL accessibility first
                xbmc.log(f"Testing URL accessibility: {video_url}", xbmc.LOGINFO)
                try:
                    response = requests.head(video_url, timeout=5)
                    xbmc.log(f"URL test response: {response.status_code}", xbmc.LOGINFO)
                except Exception as url_test_error:
                    xbmc.log(f"URL test failed: {str(url_test_error)}", xbmc.LOGWARNING)
                    continue  # Try next URL
                
                # Try to resolve URL
                xbmc.log("Calling setResolvedURL...", xbmc.LOGINFO)
                result = xbmcplugin.setResolvedURL(plugin_handle, True, list_item)
                xbmc.log(f"setResolvedURL result: {result}", xbmc.LOGINFO)
                
                # Show success message
                xbmcgui.Dialog().notification('MovieStream DEBUG', f'Attempting playback: {title}', xbmcgui.NOTIFICATION_INFO, 3000)
                xbmc.log("SUCCESS: setResolvedURL completed", xbmc.LOGINFO)
                
                return  # Exit function on success
                
            except Exception as url_error:
                xbmc.log(f"Error with URL {i+1}: {str(url_error)}", xbmc.LOGERROR)
                continue
        
        # If we get here, all URLs failed
        xbmc.log("ALL URLS FAILED", xbmc.LOGERROR)
        raise Exception("No working video URLs found")
        
    except json.JSONDecodeError as json_error:
        error_msg = f"JSON decode error: {str(json_error)}"
        xbmc.log(f"CRITICAL: {error_msg}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('JSON Error', error_msg)
        
    except Exception as e:
        error_msg = str(e)
        xbmc.log(f"CRITICAL ERROR in play_movie: {error_msg}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Playback Error', f'Detailed error: {error_msg}')
        xbmcgui.Dialog().notification('MovieStream', 'Playback failed - check log', xbmcgui.NOTIFICATION_ERROR)

def github_collection():
    """Show GitHub collection"""
    xbmcplugin.setPluginCategory(plugin_handle, 'GitHub Collection')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    try:
        github_url = addon.getSetting('github_repo_url') or 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
        movies_url = github_url + 'movies.json'
        
        xbmc.log(f"Fetching GitHub movies from: {movies_url}", xbmc.LOGINFO)
        
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
                xbmc.log(f"GitHub movie with direct URL: {title} -> {video_url}", xbmc.LOGINFO)
            else:
                url = get_url(action='play_movie', movie_data=json.dumps(movie))
                xbmc.log(f"GitHub movie without URL: {title}", xbmc.LOGINFO)
            
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    except Exception as e:
        xbmc.log(f"MovieStream: Error loading GitHub collection: {str(e)}", xbmc.LOGERROR)
        list_item = xbmcgui.ListItem(label='❌ Error loading GitHub collection')
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def play_direct(video_url, title):
    """Play direct video URL with debug info"""
    xbmc.log(f"=== PLAY_DIRECT CALLED ===", xbmc.LOGINFO)
    xbmc.log(f"URL: {video_url}", xbmc.LOGINFO)
    xbmc.log(f"Title: {title}", xbmc.LOGINFO)
    
    try:
        list_item = xbmcgui.ListItem(label=title, path=video_url)
        list_item.setInfo('video', {'title': title, 'mediatype': 'movie'})
        list_item.setProperty('IsPlayable', 'true')
        
        xbmc.log("Calling setResolvedURL for direct play...", xbmc.LOGINFO)
        xbmcplugin.setResolvedURL(plugin_handle, True, list_item)
        xbmc.log("setResolvedURL completed for direct play", xbmc.LOGINFO)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing direct URL: {str(e)}", xbmc.LOGERROR)
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
                
                for movie in results.get('results', [])[:10]:  # Limit to 10 for testing
                    add_movie_item(movie)
                
                xbmcplugin.endOfDirectory(plugin_handle)
                
            except Exception as e:
                xbmc.log(f"MovieStream: Search error: {str(e)}", xbmc.LOGERROR)
                xbmcgui.Dialog().notification('MovieStream', 'Search failed', xbmcgui.NOTIFICATION_ERROR)

def open_settings():
    """Open addon settings"""
    addon.openSettings()

def router(paramstring):
    """Route to the appropriate function with enhanced logging"""
    xbmc.log(f"=== ROUTER CALLED ===", xbmc.LOGINFO)
    xbmc.log(f"Raw paramstring: {paramstring}", xbmc.LOGINFO)
    
    # Parse parameters
    params = dict(urlparse.parse_qsl(paramstring))
    xbmc.log(f"Parsed params: {params}", xbmc.LOGINFO)
    
    if params:
        action = params.get('action')
        xbmc.log(f"Action: {action}", xbmc.LOGINFO)
        
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
        elif action == 'test_direct_play':
            test_direct_play()
        elif action == 'settings':
            open_settings()
        else:
            xbmc.log(f"Unknown action: {action}, showing main menu", xbmc.LOGINFO)
            list_categories()
    else:
        xbmc.log("No params, showing main menu", xbmc.LOGINFO)
        list_categories()

if __name__ == '__main__':
    try:
        xbmc.log("=== MOVIESTREAM DEBUG VERSION STARTING ===", xbmc.LOGINFO)
        xbmc.log(f"sys.argv: {sys.argv}", xbmc.LOGINFO)
        xbmc.log(f"plugin_handle: {plugin_handle}", xbmc.LOGINFO)
        xbmc.log(f"base_url: {base_url}", xbmc.LOGINFO)
        
        router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
        
    except Exception as e:
        error_msg = str(e)
        xbmc.log(f"CRITICAL STARTUP ERROR: {error_msg}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Startup Error', error_msg)
        xbmcgui.Dialog().notification('MovieStream', 'Critical error - check log', xbmc.NOTIFICATION_ERROR)