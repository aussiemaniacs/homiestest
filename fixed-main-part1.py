#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MovieStream Pro - Complete Kodi Addon with Cocoscrapers Integration
Version: 2.0.0 - Fixed Client Initialization
"""

import sys
import urllib.parse as urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import json

# Get addon info first
addon = xbmcaddon.Addon()
plugin_handle = int(sys.argv[1])
base_url = sys.argv[0]

# Try to import modules with individual error handling
cocoscrapers_client = None
debrid_client = None
tvshow_client = None
watchlist_manager = None
tmdb_client = None
github_client = None
video_player = None
streaming_providers = None

# Basic clients (essential for core functionality)
try:
    from resources.lib.tmdb_client import TMDBClient
    tmdb_client = TMDBClient()
    TMDB_AVAILABLE = True
    xbmc.log("MovieStream: TMDB client ready", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"MovieStream: TMDB client failed: {str(e)}", xbmc.LOGERROR)
    TMDB_AVAILABLE = False

try:
    from resources.lib.github_client import GitHubClient
    github_client = GitHubClient()
    GITHUB_AVAILABLE = True
    xbmc.log("MovieStream: GitHub client ready", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"MovieStream: GitHub client failed: {str(e)}", xbmc.LOGERROR)
    GITHUB_AVAILABLE = False

try:
    from resources.lib.video_player import VideoPlayer
    video_player = VideoPlayer()
    VIDEO_PLAYER_AVAILABLE = True
    xbmc.log("MovieStream: Video player ready", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"MovieStream: Video player failed: {str(e)}", xbmc.LOGERROR)
    VIDEO_PLAYER_AVAILABLE = False

try:
    from resources.lib.streaming_providers import StreamingProviders
    streaming_providers = StreamingProviders()
    STREAMING_AVAILABLE = True
    xbmc.log("MovieStream: Streaming providers ready", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"MovieStream: Streaming providers failed: {str(e)}", xbmc.LOGERROR)
    STREAMING_AVAILABLE = False

# Enhanced clients (optional - for Cocoscrapers functionality)
try:
    from resources.lib.cocoscrapers_client import CocoScrapersClient
    cocoscrapers_client = CocoScrapersClient()
    COCOSCRAPERS_AVAILABLE = True
    xbmc.log("MovieStream: Cocoscrapers client ready", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"MovieStream: Cocoscrapers client failed: {str(e)}", xbmc.LOGERROR)
    COCOSCRAPERS_AVAILABLE = False

try:
    from resources.lib.debrid_client import DebridClient
    debrid_client = DebridClient()
    DEBRID_AVAILABLE = True
    xbmc.log("MovieStream: Debrid client ready", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"MovieStream: Debrid client failed: {str(e)}", xbmc.LOGERROR)
    DEBRID_AVAILABLE = False

try:
    from resources.lib.watchlist_manager import WatchlistManager
    watchlist_manager = WatchlistManager()
    WATCHLIST_AVAILABLE = True
    xbmc.log("MovieStream: Watchlist manager ready", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"MovieStream: Watchlist manager failed: {str(e)}", xbmc.LOGERROR)
    WATCHLIST_AVAILABLE = False

try:
    from resources.lib.tvshow_client import TVShowClient
    tvshow_client = TVShowClient()
    TVSHOW_AVAILABLE = True
    xbmc.log("MovieStream: TV show client ready", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"MovieStream: TV show client failed: {str(e)}", xbmc.LOGERROR)
    TVSHOW_AVAILABLE = False

# Determine addon capabilities
BASIC_MODE = TMDB_AVAILABLE  # At minimum, need TMDB
ENHANCED_MODE = COCOSCRAPERS_AVAILABLE and BASIC_MODE
CLIENTS_INITIALIZED = ENHANCED_MODE  # For backward compatibility

xbmc.log(f"MovieStream: Mode - Basic: {BASIC_MODE}, Enhanced: {ENHANCED_MODE}", xbmc.LOGINFO)

def get_url(**kwargs):
    """Create a URL for calling the plugin"""
    return '{}?{}'.format(base_url, urlparse.urlencode(kwargs))

def show_error_message(message):
    """Show error message to user"""
    xbmcgui.Dialog().notification('MovieStream Error', message, xbmcgui.NOTIFICATION_ERROR, 5000)
    xbmc.log(f"MovieStream Error: {message}", xbmc.LOGERROR)

def list_categories():
    """Display main categories"""
    xbmcplugin.setPluginCategory(plugin_handle, 'MovieStream Pro')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    # Check status for display
    cocoscrapers_status = "✅" if COCOSCRAPERS_AVAILABLE and cocoscrapers_client.is_available() else "❌"
    
    categories = [
        (f'🎬 Movies', 'movies_menu', 'DefaultMovies.png'),
        (f'📺 TV Shows', 'tvshows_menu', 'DefaultTVShows.png'),
        (f'🔍 Search', 'search_menu', 'DefaultSearch.png'),
        (f'📁 GitHub Collection', 'github_collection', 'DefaultFolder.png'),
        (f'⚙️ Tools & Status', 'tools_menu', 'DefaultAddonProgram.png'),
        (f'🔧 Settings', 'settings', 'DefaultAddonProgram.png')
    ]
    
    for name, action, icon in categories:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': icon, 'icon': icon})
        list_item.setInfo('video', {'title': name, 'genre': 'Directory', 'mediatype': 'video'})
        
        url = get_url(action=action)
        is_folder = action != 'settings'
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, is_folder)
    
    # Add status info at the bottom
    mode_text = 'Enhanced Mode' if ENHANCED_MODE else ('Basic Mode' if BASIC_MODE else 'Error Mode')
    status_info = f"Cocoscrapers: {cocoscrapers_status} | Status: {mode_text}"
    
    list_item = xbmcgui.ListItem(label=f"ℹ️ {status_info}")
    list_item.setArt({'thumb': 'DefaultAddonProgram.png'})
    list_item.setInfo('video', {'title': 'Addon Status', 'plot': 'Click for detailed status information'})
    url = get_url(action='debug_info')
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def movies_menu():
    """Movies submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '🎬 Movies')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    menu_items = [
        ('🔥 Popular Movies', 'movies', 'popular'),
        ('⭐ Top Rated Movies', 'movies', 'top_rated'),
        ('🎬 Now Playing', 'movies', 'now_playing'),
        ('🔮 Upcoming Movies', 'movies', 'upcoming'),
        ('🔍 Search Movies', 'search_movies', '')
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultMovies.png'})
        list_item.setInfo('video', {'title': name, 'genre': 'Directory'})
        
        if param:
            url = get_url(action=action, category=param)
        else:
            url = get_url(action=action)
        
        is_folder = action != 'search_movies'
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, is_folder)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def list_movies(page=1, category='popular'):
    """List movies from TMDB - Fixed to work without client initialization errors"""
    xbmcplugin.setPluginCategory(plugin_handle, f'Movies - {category.title()}')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    if not BASIC_MODE:
        show_error_message("TMDB functionality not available - check addon installation")
        xbmcplugin.endOfDirectory(plugin_handle)
        return
    
    try:
        # Use direct TMDB API (more reliable than client methods)
        api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
        
        # Map category to TMDB endpoint
        if category == 'top_rated':
            url = f'https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}&page={page}'
        elif category == 'now_playing':
            url = f'https://api.themoviedb.org/3/movie/now_playing?api_key={api_key}&page={page}'
        elif category == 'upcoming':
            url = f'https://api.themoviedb.org/3/movie/upcoming?api_key={api_key}&page={page}'
        else:  # popular
            url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page={page}'
        
        xbmc.log(f"MovieStream: Fetching movies from TMDB: {category}, page {page}", xbmc.LOGINFO)
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            movies = response.json()
            
            if movies.get('results'):
                for movie in movies.get('results', [])[:15]:  # Show 15 per page
                    add_movie_item(movie, from_tmdb=True)
                
                # Add next page if available
                if page < min(movies.get('total_pages', 1), 10):  # Limit to 10 pages
                    list_item = xbmcgui.ListItem(label=f'➡️ Next Page ({page + 1}) >>')
                    list_item.setArt({'thumb': 'DefaultFolder.png'})
                    url = get_url(action='movies', page=page + 1, category=category)
                    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
                
                xbmc.log(f"MovieStream: Successfully loaded {len(movies.get('results', []))} movies", xbmc.LOGINFO)
            else:
                # Show no results message
                list_item = xbmcgui.ListItem(label='No movies found')
                list_item.setInfo('video', {'title': 'No Results', 'plot': 'No movies available for this category'})
                xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
        else:
            xbmc.log(f"MovieStream: TMDB API error {response.status_code}: {response.text}", xbmc.LOGERROR)
            show_error_message(f"TMDB API error: {response.status_code}")
        
        xbmcplugin.endOfDirectory(plugin_handle)
        
    except requests.exceptions.RequestException as e:
        xbmc.log(f"MovieStream: Network error loading movies: {str(e)}", xbmc.LOGERROR)
        show_error_message(f"Network error: {str(e)}")
        xbmcplugin.endOfDirectory(plugin_handle)
    except Exception as e:
        xbmc.log(f"MovieStream: Error loading movies: {str(e)}", xbmc.LOGERROR)
        show_error_message(f"Error loading movies: {str(e)}")
        xbmcplugin.endOfDirectory(plugin_handle)

def add_movie_item(movie, from_tmdb=False):
    """Add a movie item to the directory with robust error handling"""
    try:
        title = movie.get('title', 'Unknown Title')
        year = movie.get('release_date', '')[:4] if movie.get('release_date') else movie.get('year', '')
        plot = movie.get('overview', movie.get('plot', 'No description available'))
        
        # Create display title
        display_title = f"{title} ({year})" if year else title
        list_item = xbmcgui.ListItem(label=display_title)
        
        # Set artwork
        if from_tmdb:
            poster_path = movie.get('poster_path')
            backdrop_path = movie.get('backdrop_path')
            
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                list_item.setArt({'thumb': poster_url, 'poster': poster_url})
            
            if backdrop_path:
                fanart_url = f"https://image.tmdb.org/t/p/w1280{backdrop_path}"
                list_item.setArt({'fanart': fanart_url, 'landscape': fanart_url})
        else:
            # GitHub/custom sources
            if movie.get('poster_url'):
                list_item.setArt({'thumb': movie['poster_url'], 'poster': movie['poster_url']})
            if movie.get('backdrop_url'):
                list_item.setArt({'fanart': movie['backdrop_url']})
        
        # Set video info
        info_dict = {
            'title': title,
            'plot': plot,
            'year': int(year) if str(year).isdigit() else 0,
            'genre': movie.get('genre', ''),
            'rating': float(movie.get('vote_average', movie.get('rating', 0))),
            'votes': str(movie.get('vote_count', 0)),
            'mediatype': 'movie'
        }
        list_item.setInfo('video', info_dict)
        
        # CRITICAL: Set as playable
        list_item.setProperty('IsPlayable', 'true')
        
        # Create movie data for playback
        movie_data = {
            'title': title,
            'year': str(year),
            'tmdb_id': str(movie.get('id', movie.get('tmdb_id', ''))),
            'imdb_id': movie.get('imdb_id', ''),
            'type': 'movie',
            'poster_url': movie.get('poster_url', ''),
            'plot': plot,
            'video_url': movie.get('video_url', ''),  # For GitHub collection
            'm3u8_url': movie.get('m3u8_url', '')     # For M3U8 streams
        }
        
        # Set playback URL
        url = get_url(action='play_movie', movie_data=json.dumps(movie_data))
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error adding movie item: {str(e)}", xbmc.LOGERROR)

# Continue with the rest of the functions...
# (I'll provide the remaining functions in the next parts)