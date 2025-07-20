#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MovieStream Pro - Complete Cocoscrapers Integration
Version: 2.0.0 - Full Featured with Real Streaming Sources
"""

import sys
import urllib.parse as urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import json

# Import enhanced modules with error handling
try:
    from resources.lib.cocoscrapers_client import CocoScrapersClient
    from resources.lib.debrid_client import DebridClient  
    from resources.lib.tvshow_client import TVShowClient
    from resources.lib.watchlist_manager import WatchlistManager
    from resources.lib.tmdb_client import TMDBClient
    from resources.lib.github_client import GitHubClient
    from resources.lib.video_player import VideoPlayer
    from resources.lib.streaming_providers import StreamingProviders
    IMPORTS_SUCCESS = True
    xbmc.log("MovieStream Pro: All enhanced modules imported successfully", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"MovieStream Pro: Enhanced import error: {str(e)} - Using basic mode", xbmc.LOGERROR)
    IMPORTS_SUCCESS = False

# Get addon info
addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
plugin_handle = int(sys.argv[1])
base_url = sys.argv[0]

# Initialize clients with error handling
if IMPORTS_SUCCESS:
    try:
        cocoscrapers_client = CocoScrapersClient()
        debrid_client = DebridClient()
        tvshow_client = TVShowClient()
        watchlist_manager = WatchlistManager()
        tmdb_client = TMDBClient()
        github_client = GitHubClient()
        video_player = VideoPlayer()
        streaming_providers = StreamingProviders()
        CLIENTS_INITIALIZED = True
        xbmc.log("MovieStream Pro: All clients initialized successfully", xbmc.LOGINFO)
    except Exception as e:
        xbmc.log(f"MovieStream Pro: Client initialization error: {str(e)}", xbmc.LOGERROR)
        CLIENTS_INITIALIZED = False
        # Fallback to basic clients
        tmdb_client = None
        github_client = None
else:
    CLIENTS_INITIALIZED = False
    cocoscrapers_client = None
    debrid_client = None
    tmdb_client = None
    github_client = None

def get_url(**kwargs):
    """Create a URL for calling the plugin"""
    return '{}?{}'.format(base_url, urlparse.urlencode(kwargs))

def list_categories():
    """Display enhanced main categories with Pro features"""
    xbmcplugin.setPluginCategory(plugin_handle, 'MovieStream Pro 2.0')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    # Check status for display
    cocoscrapers_status = "✅" if CLIENTS_INITIALIZED and cocoscrapers_client and cocoscrapers_client.is_available() else "❌"
    debrid_status = "✅" if CLIENTS_INITIALIZED and debrid_client and debrid_client.is_available() else "❌"
    
    categories = [
        (f'🎬 Movies', 'movies_menu', 'DefaultMovies.png'),
        (f'📺 TV Shows', 'tvshows_menu', 'DefaultTVShows.png'),
        (f'🔍 Search', 'search_menu', 'DefaultSearch.png'),
        (f'📁 GitHub Collection', 'github_collection', 'DefaultFolder.png'),
        (f'⭐ My Lists', 'my_lists_menu', 'DefaultPlaylist.png'),
        (f'🎭 Streaming Providers', 'streaming_providers_menu', 'DefaultNetwork.png'),
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
    
    # Add status indicator at bottom
    status_text = f"Status: Cocoscrapers {cocoscrapers_status} | Debrid {debrid_status} | Mode: {'Pro' if CLIENTS_INITIALIZED else 'Basic'}"
    list_item = xbmcgui.ListItem(label=f"ℹ️ {status_text}")
    list_item.setArt({'thumb': 'DefaultAddonProgram.png'})
    list_item.setInfo('video', {'title': 'Addon Status', 'plot': 'Current addon capabilities and status'})
    url = get_url(action='debug_info')
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def movies_menu():
    """Enhanced movies submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '🎬 Movies')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    menu_items = [
        ('🔥 Popular Movies', 'movies', 'popular'),
        ('⭐ Top Rated Movies', 'top_rated_movies', ''),
        ('🎬 Now Playing', 'now_playing_movies', ''),
        ('🔮 Upcoming Movies', 'upcoming_movies', ''),
        ('🔍 Search Movies', 'search_movies', '')
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultMovies.png'})
        list_item.setInfo('video', {'title': name, 'genre': 'Directory'})
        
        url = get_url(action=action, param=param) if param else get_url(action=action)
        is_folder = action != 'search_movies'
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, is_folder)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def tvshows_menu():
    """Enhanced TV shows submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '📺 TV Shows')
    xbmcplugin.setContent(plugin_handle, 'tvshows')
    
    menu_items = [
        ('🔥 Popular TV Shows', 'tvshows', 'popular'),
        ('⭐ Top Rated TV Shows', 'top_rated_tvshows', ''),
        ('📺 Airing Today', 'airing_today_tvshows', ''),
        ('🔍 Search TV Shows', 'search_tv_shows', '')
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultTVShows.png'})
        list_item.setInfo('video', {'title': name, 'genre': 'Directory'})
        
        url = get_url(action=action, param=param) if param else get_url(action=action)
        is_folder = action != 'search_tv_shows'
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, is_folder)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def search_menu():
    """Search submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '🔍 Search')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    menu_items = [
        ('🎬 Search Movies', 'search_movies', 'Search for movies'),
        ('📺 Search TV Shows', 'search_tv_shows', 'Search for TV shows'),
        ('🌐 Search All Content', 'search_all', 'Search both movies and TV shows')
    ]
    
    for name, action, description in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultSearch.png'})
        list_item.setInfo('video', {'title': name, 'plot': description})
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def my_lists_menu():
    """My Lists submenu - requires enhanced clients"""
    xbmcplugin.setPluginCategory(plugin_handle, '⭐ My Lists')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    if not CLIENTS_INITIALIZED or not watchlist_manager:
        list_item = xbmcgui.ListItem(label='❌ Enhanced Features Not Available')
        list_item.setInfo('video', {
            'title': 'Feature Unavailable', 
            'plot': 'My Lists feature requires enhanced client libraries.\n\nInstall required dependencies:\n• script.module.cocoscrapers\n• Enhanced resource files'
        })
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
        xbmcplugin.endOfDirectory(plugin_handle)
        return
    
    # Get stats if available
    try:
        stats = watchlist_manager.get_stats() if hasattr(watchlist_manager, 'get_stats') else {'watchlist_count': 0, 'favorites_count': 0, 'history_count': 0}
    except:
        stats = {'watchlist_count': 0, 'favorites_count': 0, 'history_count': 0}
    
    menu_items = [
        (f"📋 Watchlist ({stats.get('watchlist_count', 0)})", 'list_watchlist', 'Movies and shows you want to watch'),
        (f"❤️ Favorites ({stats.get('favorites_count', 0)})", 'list_favorites', 'Your favorite movies and shows'),
        (f"📖 Watch History ({stats.get('history_count', 0)})", 'list_history', 'Recently watched content with resume points')
    ]
    
    for name, action, description in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultPlaylist.png'})
        list_item.setInfo('video', {'title': name, 'plot': description})
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def tools_menu():
    """Enhanced tools and diagnostics menu"""
    xbmcplugin.setPluginCategory(plugin_handle, '⚙️ Tools & Status')
    xbmcplugin.setContent(plugin_handle, 'files')
    
    # Get current status
    cocoscrapers_status = "✅ Available" if CLIENTS_INITIALIZED and cocoscrapers_client and cocoscrapers_client.is_available() else "❌ Not Available"
    debrid_status = "✅ Available" if CLIENTS_INITIALIZED and debrid_client and debrid_client.is_available() else "❌ Not Available"
    
    menu_items = [
        ('🔍 Test TMDB Connection', 'test_tmdb', 'Test connection to The Movie Database'),
        ('📁 Test GitHub Connection', 'test_github_connection', 'Test connection to GitHub repository'),
        (f'🎬 Cocoscrapers Status', 'cocoscrapers_status', f'Status: {cocoscrapers_status}'),
        (f'💎 Debrid Services Status', 'debrid_status', f'Status: {debrid_status}'),
        ('🎮 Test Movie Playback', 'test_movie_playback', 'Test sample movie playback functionality'),
        ('📺 Test TV Show Playback', 'test_episode_playback', 'Test sample TV episode playback'),
        ('ℹ️ Debug Information', 'debug_info', 'Show comprehensive addon debug information'),
        ('🗑️ Clear All Cache', 'clear_all_cache', 'Clear all cached data and reset preferences'),
        ('📊 Addon Information', 'addon_info', 'Show addon version and technical information')
    ]
    
    for name, action, description in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultAddonProgram.png'})
        list_item.setInfo('video', {'title': name, 'plot': description, 'genre': 'Tool'})
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def list_movies(page=1, category='popular'):
    """List movies from TMDB with enhanced features"""
    xbmcplugin.setPluginCategory(plugin_handle, 'Movies')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    # Use basic TMDB API if enhanced client not available
    if CLIENTS_INITIALIZED and tmdb_client:
        try:
            if category == 'popular':
                movies = tmdb_client.get_popular_movies(page)
            elif category == 'top_rated':
                movies = tmdb_client.get_top_rated_movies(page)
            elif category == 'now_playing':
                movies = tmdb_client.get_now_playing_movies(page)
            elif category == 'upcoming':
                movies = tmdb_client.get_upcoming_movies(page)
            else:
                movies = tmdb_client.get_popular_movies(page)
        except:
            movies = get_movies_basic(page, category)
    else:
        movies = get_movies_basic(page, category)
    
    if movies and movies.get('results'):
        for movie in movies.get('results', [])[:20]:  # Show 20 movies per page
            add_movie_item(movie, from_tmdb=True)
        
        # Add next page if available
        if page < min(movies.get('total_pages', 1), 10):  # Limit to 10 pages
            list_item = xbmcgui.ListItem(label=f'➡️ Next Page ({page + 1}) >>')
            list_item.setArt({'thumb': 'DefaultFolder.png'})
            url = get_url(action='movies', page=page + 1, category=category)
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def get_movies_basic(page=1, category='popular'):
    """Basic TMDB API fallback"""
    try:
        api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
        
        if category == 'top_rated':
            url = f'https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}&page={page}'
        elif category == 'now_playing':
            url = f'https://api.themoviedb.org/3/movie/now_playing?api_key={api_key}&page={page}'
        elif category == 'upcoming':
            url = f'https://api.themoviedb.org/3/movie/upcoming?api_key={api_key}&page={page}'
        else:
            url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page={page}'
        
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        xbmc.log(f"MovieStream Pro: Basic TMDB API error: {str(e)}", xbmc.LOGERROR)
        return {}

def add_movie_item(movie, from_tmdb=False):
    """Add enhanced movie item with Cocoscrapers support"""
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
        'director': movie.get('director', ''),
        'mediatype': 'movie'
    }
    list_item.setInfo('video', info_dict)
    
    # CRITICAL: Set as playable
    list_item.setProperty('IsPlayable', 'true')
    
    # Create comprehensive movie data
    movie_data = {
        'title': title,
        'year': str(year),
        'tmdb_id': str(movie.get('id', movie.get('tmdb_id', ''))),
        'imdb_id': movie.get('imdb_id', ''),
        'type': 'movie',
        'poster_url': movie.get('poster_url', ''),
        'plot': plot,
        'video_url': movie.get('video_url', ''),  # For GitHub collection
        'm3u8_url': movie.get('m3u8_url', '')     # For streaming URLs
    }
    
    # Add context menu for enhanced features
    if CLIENTS_INITIALIZED and watchlist_manager:
        try:
            context_items = []
            
            # Watchlist context menu
            context_items.append((
                'Add to Watchlist',
                f'RunPlugin({get_url(action="add_to_watchlist", movie_data=json.dumps(movie_data))})'
            ))
            
            # Favorites context menu
            context_items.append((
                'Add to Favorites', 
                f'RunPlugin({get_url(action="add_to_favorites", movie_data=json.dumps(movie_data))})'
            ))
            
            # Source selection if Cocoscrapers available
            if cocoscrapers_client and cocoscrapers_client.is_available():
                context_items.append((
                    'Select Source',
                    f'RunPlugin({get_url(action="select_movie_source", movie_data=json.dumps(movie_data))})'
                ))
            
            list_item.addContextMenuItems(context_items)
        except Exception as e:
            xbmc.log(f"MovieStream Pro: Context menu error: {str(e)}", xbmc.LOGWARNING)
    
    # Set playback URL
    url = get_url(action='play_movie', movie_data=json.dumps(movie_data))
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)