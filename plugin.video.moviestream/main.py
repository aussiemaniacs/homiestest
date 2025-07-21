#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MovieStream Pro - Complete Kodi Addon with Cocoscrapers Integration
Features: TMDB, GitHub, Cocoscrapers, Debrid Services, TV Shows, Watchlist, Favorites
Version: 2.0.0 - FIXED CLIENT INITIALIZATION
"""

import sys
import urllib.parse as urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import requests
import json

# Import our enhanced modules
try:
    from resources.lib.cocoscrapers_client import CocoScrapersClient
    from resources.lib.debrid_client import DebridClient
    from resources.lib.tvshow_client import TVShowClient
    from resources.lib.watchlist_manager import WatchlistManager
    from resources.lib.tmdb_client import TMDBClient
    from resources.lib.github_client import GitHubClient
    from resources.lib.video_player import VideoPlayer
    from resources.lib.torrent_client import TorrentClient
    from resources.lib.subtitle_client import SubtitleClient
    from resources.lib.streaming_providers import StreamingProviders
    IMPORTS_SUCCESS = True
except Exception as e:
    xbmc.log(f"MovieStream: Import error: {str(e)}", xbmc.LOGERROR)
    IMPORTS_SUCCESS = False

# Get addon info
addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_path = addon.getAddonInfo('path')
addon_profile = addon.getAddonInfo('profile')

# Plugin handle and base URL
plugin_handle = int(sys.argv[1])
base_url = sys.argv[0]

# Initialize clients with robust error handling
cocoscrapers_client = None
debrid_client = None
tvshow_client = None
watchlist_manager = None
tmdb_client = None
github_client = None
video_player = None
streaming_providers = None

# Try to initialize basic clients first
try:
    if 'TMDBClient' in globals():
        tmdb_client = TMDBClient()
        xbmc.log("MovieStream: TMDB client initialized", xbmc.LOGINFO)
    else:
        xbmc.log("MovieStream: TMDBClient not available", xbmc.LOGWARNING)
except Exception as e:
    xbmc.log(f"MovieStream: TMDB client init error: {str(e)}", xbmc.LOGERROR)

try:
    if 'GitHubClient' in globals():
        github_client = GitHubClient()
        xbmc.log("MovieStream: GitHub client initialized", xbmc.LOGINFO)
    else:
        xbmc.log("MovieStream: GitHubClient not available", xbmc.LOGWARNING)
except Exception as e:
    xbmc.log(f"MovieStream: GitHub client init error: {str(e)}", xbmc.LOGERROR)

try:
    if 'VideoPlayer' in globals():
        video_player = VideoPlayer()
        xbmc.log("MovieStream: Video player initialized", xbmc.LOGINFO)
    else:
        xbmc.log("MovieStream: VideoPlayer not available", xbmc.LOGWARNING)
except Exception as e:
    xbmc.log(f"MovieStream: Video player init error: {str(e)}", xbmc.LOGERROR)

try:
    if 'StreamingProviders' in globals():
        streaming_providers = StreamingProviders()
        xbmc.log("MovieStream: Streaming providers initialized", xbmc.LOGINFO)
    else:
        xbmc.log("MovieStream: StreamingProviders not available", xbmc.LOGWARNING)
except Exception as e:
    xbmc.log(f"MovieStream: Streaming providers init error: {str(e)}", xbmc.LOGERROR)

# Check if basic functionality is available
BASIC_CLIENTS_READY = bool(tmdb_client and github_client)

# Try to initialize enhanced clients if imports were successful
if IMPORTS_SUCCESS:
    try:
        cocoscrapers_client = CocoScrapersClient()
        debrid_client = DebridClient()
        tvshow_client = TVShowClient()
        watchlist_manager = WatchlistManager()
        CLIENTS_INITIALIZED = True
        xbmc.log("MovieStream: Enhanced clients initialized successfully", xbmc.LOGINFO)
    except Exception as e:
        xbmc.log(f"MovieStream: Enhanced client initialization error: {str(e)}", xbmc.LOGERROR)
        CLIENTS_INITIALIZED = False
        xbmc.log("MovieStream: Running in basic mode only", xbmc.LOGINFO)
else:
    CLIENTS_INITIALIZED = False
    xbmc.log("MovieStream: Enhanced imports failed - running in basic mode", xbmc.LOGINFO)

def get_url(**kwargs):
    """Create a URL for calling the plugin"""
    return '{}?{}'.format(base_url, urlparse.urlencode(kwargs))

def list_categories():
    """Display main categories"""
    xbmcplugin.setPluginCategory(plugin_handle, 'MovieStream Pro')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    # Check Cocoscrapers status for display
    cocoscrapers_status = "✅" if CLIENTS_INITIALIZED and cocoscrapers_client and cocoscrapers_client.is_available() else "❌"
    
    categories = [
        (f'🎬 Movies', 'movies_menu', 'DefaultMovies.png'),
        (f'📺 TV Shows', 'tvshows_menu', 'DefaultTVShows.png'),
        (f'🔍 Search', 'search_menu', 'DefaultSearch.png'),
        (f'📁 GitHub Collection', 'github_collection', 'DefaultFolder.png'),
        (f'⭐ My Lists', 'my_lists_menu', 'DefaultPlaylist.png'),
        (f'🎭 Streaming Providers', 'streaming_providers', 'DefaultNetwork.png'),
        (f'🎞️ Subtitle Manager', 'subtitle_manager', 'DefaultSubtitles.png'),
        (f'⚙️ Tools', 'tools_menu', 'DefaultAddonProgram.png'),
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
    if BASIC_CLIENTS_READY:
        status_mode = 'Pro Mode' if CLIENTS_INITIALIZED else 'Basic Mode'
        status_info = f"Cocoscrapers: {cocoscrapers_status} | Status: {status_mode} ✅"
    else:
        status_info = f"Status: Error - Check Settings ❌"
    
    list_item = xbmcgui.ListItem(label=f"ℹ️ {status_info}")
    list_item.setArt({'thumb': 'DefaultAddonProgram.png'})
    list_item.setInfo('video', {'title': status_info, 'plot': 'Addon status information'})
    url = get_url(action='debug_info')
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def show_error_message(message):
    """Show error message to user"""
    xbmcgui.Dialog().notification('MovieStream Error', message, xbmcgui.NOTIFICATION_ERROR)

def list_movies(page=1, category='popular'):
    """List movies from TMDB - Fixed to work without client initialization errors"""
    xbmcplugin.setPluginCategory(plugin_handle, f'Movies - {category.title()}')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    try:
        # Use direct TMDB API (more reliable than depending on client initialization)
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

def get_movies_basic_api(page=1, category='popular'):
    """Basic TMDB API fallback - works without enhanced clients"""
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
        
        xbmc.log(f"MovieStream: Using basic TMDB API: {url}", xbmc.LOGINFO)
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            xbmc.log(f"MovieStream: TMDB API error {response.status_code}", xbmc.LOGERROR)
            return {}
            
    except Exception as e:
        xbmc.log(f"MovieStream: Basic TMDB API error: {str(e)}", xbmc.LOGERROR)
        return {}

def list_tv_shows(page=1):
    """List popular TV shows from TMDB"""
    xbmcplugin.setPluginCategory(plugin_handle, 'TV Shows')
    xbmcplugin.setContent(plugin_handle, 'tvshows')
    
    if not CLIENTS_INITIALIZED:
        show_error_message("Client initialization failed")
        return
    
    try:
        # Get popular TV shows from TMDB
        api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
        url = f'https://api.themoviedb.org/3/tv/popular?api_key={api_key}&page={page}'
        
        response = requests.get(url, timeout=10)
        shows = response.json()
        
        if shows:
            for show in shows.get('results', []):
                add_tv_show_item(show)
            
            # Add next page if available
            if page < shows.get('total_pages', 1):
                list_item = xbmcgui.ListItem(label='➡️ Next Page >>')
                list_item.setArt({'thumb': 'DefaultFolder.png'})
                url = get_url(action='tvshows', page=page + 1)
                xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
        
        xbmcplugin.endOfDirectory(plugin_handle)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error loading TV shows: {str(e)}", xbmc.LOGERROR)
        show_error_message("Failed to load TV shows")

def show_seasons(show_id):
    """Show seasons for a TV show"""
    if not CLIENTS_INITIALIZED:
        show_error_message("Client initialization failed")
        return
    
    try:
        # Get show details from TMDB
        api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
        url = f'https://api.themoviedb.org/3/tv/{show_id}?api_key={api_key}'
        
        response = requests.get(url, timeout=10)
        show_details = response.json()
        
        if show_details:
            xbmcplugin.setPluginCategory(plugin_handle, show_details.get('name', 'TV Show'))
            xbmcplugin.setContent(plugin_handle, 'seasons')
            
            for season in show_details.get('seasons', []):
                season_number = season.get('season_number')
                season_name = season.get('name', f'Season {season_number}')
                
                list_item = xbmcgui.ListItem(label=season_name)
                
                poster_path = season.get('poster_path')
                if poster_path:
                    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                    list_item.setArt({'thumb': poster_url, 'poster': poster_url})
                
                list_item.setInfo('video', {
                    'title': season_name,
                    'plot': season.get('overview', ''),
                    'season': season_number,
                    'mediatype': 'season'
                })
                
                url = get_url(action='show_episodes', show_id=show_id, season_number=season_number)
                xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
            
            xbmcplugin.endOfDirectory(plugin_handle)
    
    except Exception as e:
        xbmc.log(f"MovieStream: Error loading seasons: {str(e)}", xbmc.LOGERROR)
        show_error_message("Failed to load seasons")

def add_movie_item(movie, from_tmdb=False):
    """Add a movie item to the directory with Cocoscrapers support"""
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
        
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ''
        fanart_url = f"https://image.tmdb.org/t/p/w1280{backdrop_path}" if backdrop_path else ''
        
        if poster_url:
            list_item.setArt({'thumb': poster_url, 'poster': poster_url})
        if fanart_url:
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
    
    # Set as playable - CRITICAL for Kodi to recognize as playable item
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
    
    # Add context menu items if watchlist is available
    if CLIENTS_INITIALIZED and hasattr(watchlist_manager, 'get_context_menu_items'):
        try:
            context_items = watchlist_manager.get_context_menu_items(movie_data)
            
            # Add source selection context menu
            if cocoscrapers_client.is_available():
                context_items.append((
                    'Select Source',
                    f'RunPlugin({get_url(action="select_movie_source", movie_data=json.dumps(movie_data))})'
                ))
            
            list_item.addContextMenuItems(context_items)
        except Exception as e:
            xbmc.log(f"MovieStream: Context menu error: {str(e)}", xbmc.LOGWARNING)
    
    # Set playback URL - This is crucial for triggering play_movie action
    url = get_url(action='play_movie', movie_data=json.dumps(movie_data))
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)

def add_tv_show_item(show):
    """Add a TV show item to the directory"""
    title = show.get('name', 'Unknown Title')
    year = show.get('first_air_date', '')[:4] if show.get('first_air_date') else ''
    plot = show.get('overview', 'No description available')
    
    # Build artwork URLs
    poster_path = show.get('poster_path')
    backdrop_path = show.get('backdrop_path')
    
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ''
    fanart_url = f"https://image.tmdb.org/t/p/w1280{backdrop_path}" if backdrop_path else ''
    
    list_item = xbmcgui.ListItem(label=f"{title} ({year})" if year else title)
    
    # Set artwork
    list_item.setArt({
        'thumb': poster_url,
        'poster': poster_url,
        'fanart': fanart_url,
        'landscape': fanart_url
    })
    
    # Set video info
    list_item.setInfo('video', {
        'title': title,
        'year': int(year) if year.isdigit() else 0,
        'plot': plot,
        'rating': show.get('vote_average', 0),
        'votes': str(show.get('vote_count', 0)),
        'mediatype': 'tvshow'
    })
    
    url = get_url(action='show_seasons', show_id=show.get('id'))
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)

def search_movies():
    """Search for movies - Works with basic or enhanced clients"""
    keyboard = xbmc.Keyboard('', 'Search Movies')
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if query:
            xbmcplugin.setPluginCategory(plugin_handle, f'Search: {query}')
            xbmcplugin.setContent(plugin_handle, 'movies')
            
            try:
                # Try enhanced client first, fallback to basic API
                if CLIENTS_INITIALIZED and tmdb_client and hasattr(tmdb_client, 'search_movies'):
                    results = tmdb_client.search_movies(query)
                else:
                    # Use basic TMDB search API
                    results = search_movies_basic_api(query)
                
                if results and results.get('results'):
                    for movie in results.get('results', [])[:20]:  # Limit to 20 results
                        add_movie_item(movie, from_tmdb=True)
                else:
                    # Show no results message
                    list_item = xbmcgui.ListItem(label=f'No results found for "{query}"')
                    list_item.setInfo('video', {'title': 'No Results', 'plot': f'No movies found matching "{query}"'})
                    xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
                
                xbmcplugin.endOfDirectory(plugin_handle)
                
            except Exception as e:
                xbmc.log(f"MovieStream: Movie search error: {str(e)}", xbmc.LOGERROR)
                show_error_message(f"Search failed: {str(e)}")

def search_movies_basic_api(query):
    """Basic movie search using TMDB API"""
    try:
        api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
        url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}'
        
        xbmc.log(f"MovieStream: Searching movies with basic API: {query}", xbmc.LOGINFO)
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            xbmc.log(f"MovieStream: Search API error {response.status_code}", xbmc.LOGERROR)
            return {}
            
    except Exception as e:
        xbmc.log(f"MovieStream: Basic search error: {str(e)}", xbmc.LOGERROR)
        return {}

def search_tv_shows():
    """Search for TV shows"""
    keyboard = xbmc.Keyboard('', 'Search TV Shows')
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if query:
            xbmcplugin.setPluginCategory(plugin_handle, f'Search: {query}')
            xbmcplugin.setContent(plugin_handle, 'tvshows')
            
            tmdb = TMDBClient()
            results = tmdb.search_tv_shows(query)
            
            if results:
                for show in results.get('results', []):
                    add_tv_show_item(show)
            
            xbmcplugin.endOfDirectory(plugin_handle)

def show_seasons(show_id):
    """Show seasons for a TV show"""
    tmdb = TMDBClient()
    show_details = tmdb.get_tv_show_details(show_id)
    
    if show_details:
        xbmcplugin.setPluginCategory(plugin_handle, show_details.get('name', 'TV Show'))
        xbmcplugin.setContent(plugin_handle, 'seasons')
        
        for season in show_details.get('seasons', []):
            season_number = season.get('season_number')
            season_name = season.get('name', f'Season {season_number}')
            
            list_item = xbmcgui.ListItem(label=season_name)
            
            poster_path = season.get('poster_path')
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                list_item.setArt({'thumb': poster_url, 'poster': poster_url})
            
            list_item.setInfo('video', {
                'title': season_name,
                'plot': season.get('overview', ''),
                'mediatype': 'season'
            })
            
            url = get_url(action='show_episodes', show_id=show_id, season_number=season_number)
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
        
        xbmcplugin.endOfDirectory(plugin_handle)

def show_episodes(show_id, season_number):
    """Show episodes for a season"""
    if not CLIENTS_INITIALIZED:
        show_error_message("Client initialization failed")
        return
    
    try:
        # Get season details from TMDB
        api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
        url = f'https://api.themoviedb.org/3/tv/{show_id}/season/{season_number}?api_key={api_key}'
        
        response = requests.get(url, timeout=10)
        season_details = response.json()
        
        if season_details:
            xbmcplugin.setPluginCategory(plugin_handle, f"Season {season_number}")
            xbmcplugin.setContent(plugin_handle, 'episodes')
            
            show_name = season_details.get('name', 'Unknown Show')
            
            for episode in season_details.get('episodes', []):
                episode_number = episode.get('episode_number')
                episode_name = episode.get('name', f'Episode {episode_number}')
                
                list_item = xbmcgui.ListItem(label=f"{episode_number}. {episode_name}")
                
                still_path = episode.get('still_path')
                if still_path:
                    thumb_url = f"https://image.tmdb.org/t/p/w500{still_path}"
                    list_item.setArt({'thumb': thumb_url})
                
                list_item.setInfo('video', {
                    'title': episode_name,
                    'plot': episode.get('overview', ''),
                    'episode': episode_number,
                    'season': int(season_number),
                    'rating': float(episode.get('vote_average', 0)),
                    'mediatype': 'episode'
                })
                
                list_item.setProperty('IsPlayable', 'true')
                
                # Create episode data for playback
                episode_data = {
                    'title': episode_name,
                    'show_title': show_name,
                    'year': episode.get('air_date', '')[:4] if episode.get('air_date') else '',
                    'season': int(season_number),
                    'episode': episode_number,
                    'show_tmdb_id': show_id,
                    'type': 'episode',
                    'plot': episode.get('overview', '')
                }
                
                url = get_url(action='play_episode', episode_data=json.dumps(episode_data))
                xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
            
            xbmcplugin.endOfDirectory(plugin_handle)
    
    except Exception as e:
        xbmc.log(f"MovieStream: Error loading episodes: {str(e)}", xbmc.LOGERROR)
        show_error_message("Failed to load episodes")

def movies_menu():
    """Movies submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '🎬 Movies')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    menu_items = [
        ('Popular Movies', 'movies', 'popular'),
        ('Top Rated Movies', 'top_rated_movies', ''),
        ('Now Playing', 'now_playing_movies', ''),
        ('Upcoming Movies', 'upcoming_movies', ''),
        ('Search Movies', 'search_movies', '')
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultMovies.png'})
        list_item.setInfo('video', {'title': name, 'genre': 'Directory'})
        
        url = get_url(action=action, param=param)
        is_folder = action != 'search_movies'
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, is_folder)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def search_menu():
    """Search submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '🔍 Search')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    menu_items = [
        ('Search Movies', 'search_movies', ''),
        ('Search TV Shows', 'search_tv_shows', '')
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultSearch.png'})
        list_item.setInfo('video', {'title': name, 'genre': 'Directory'})
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def my_lists_menu():
    """My Lists submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '⭐ My Lists')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    if not CLIENTS_INITIALIZED:
        list_item = xbmcgui.ListItem(label='Feature not available')
        list_item.setInfo('video', {'title': 'Error', 'plot': 'Enhanced features require proper initialization'})
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
        xbmcplugin.endOfDirectory(plugin_handle)
        return
    
    try:
        stats = watchlist_manager.get_stats() if hasattr(watchlist_manager, 'get_stats') else {'watchlist_count': 0, 'favorites_count': 0, 'history_count': 0}
    except:
        stats = {'watchlist_count': 0, 'favorites_count': 0, 'history_count': 0}
    
    menu_items = [
        (f"📋 Watchlist ({stats.get('watchlist_count', 0)})", 'list_watchlist', ''),
        (f"❤️ Favorites ({stats.get('favorites_count', 0)})", 'list_favorites', ''),
        (f"📖 Watch History ({stats.get('history_count', 0)})", 'list_history', '')
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultPlaylist.png'})
        list_item.setInfo('video', {'title': name, 'genre': 'Directory'})
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def tools_menu():
    """Enhanced Tools submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '⚙️ Tools')
    xbmcplugin.setContent(plugin_handle, 'files')
    
    # Check addon status
    cocoscrapers_status = "✅ Available" if CLIENTS_INITIALIZED and cocoscrapers_client.is_available() else "❌ Not Available"
    debrid_status = "✅ Available" if CLIENTS_INITIALIZED and debrid_client.is_available() else "❌ Not Available"
    
    menu_items = [
        ('🔍 Test TMDB Connection', 'test_tmdb', 'Test connection to TMDB API'),
        ('📁 Test GitHub Connection', 'test_github', 'Test connection to GitHub repository'),
        (f'🎬 Cocoscrapers Status', 'cocoscrapers_status', f'Status: {cocoscrapers_status}'),
        (f'💎 Debrid Account Status', 'debrid_status', f'Status: {debrid_status}'),
        ('🎮 Test Movie Playback', 'test_movie_playback', 'Test sample movie playback'),
        ('ℹ️ Debug Information', 'debug_info', 'Show addon debug information'),
        ('🗑️ Clear All Cache', 'clear_all_cache', 'Clear all cached data'),
        ('📊 Addon Information', 'addon_info', 'Show addon version and info')
    ]
    
    for name, action, description in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultAddonProgram.png'})
        list_item.setInfo('video', {
            'title': name,
            'plot': description,
            'genre': 'Tool'
        })
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def github_collection():
    """Show GitHub collection with enhanced functionality"""
    xbmcplugin.setPluginCategory(plugin_handle, '📁 GitHub Collection')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    try:
        # Check if GitHub client is available
        if not github_client:
            show_error_message("GitHub client not available")
            return
        
        # Try to get collection - works with both basic and enhanced clients
        if hasattr(github_client, 'get_movie_collection'):
            collection = github_client.get_movie_collection()
        else:
            # Fallback to basic GitHub API
            collection = get_github_collection_basic()
        
        if collection:
            for movie in collection:
                add_movie_item(movie, from_tmdb=False)
        else:
            # Show no content message
            list_item = xbmcgui.ListItem(label='📭 No movies found in collection')
            list_item.setInfo('video', {
                'title': 'Empty Collection', 
                'plot': 'No movies found.\n\nPossible causes:\n• GitHub repository URL not set\n• movies.json file missing\n• Network connection issue\n\nCheck Settings > GitHub Repository URL'
            })
            xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    except Exception as e:
        xbmc.log(f"MovieStream: Error loading GitHub collection: {str(e)}", xbmc.LOGERROR)
        
        # Show error message with troubleshooting info
        list_item = xbmcgui.ListItem(label='❌ Error loading GitHub collection')
        list_item.setInfo('video', {
            'title': 'GitHub Collection Error', 
            'plot': f'Error: {str(e)}\n\nTroubleshooting:\n• Check GitHub repository URL in Settings\n• Verify movies.json file exists\n• Test connection: Tools > Test GitHub Connection\n• Check Kodi log for details'
        })
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def get_github_collection_basic():
    """Basic GitHub collection loading without enhanced client"""
    try:
        github_url = addon.getSetting('github_repo_url')
        if not github_url:
            github_url = 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
        
        if not github_url.endswith('/'):
            github_url += '/'
        
        movies_url = github_url + 'movies.json'
        xbmc.log(f"MovieStream: Loading GitHub collection from: {movies_url}", xbmc.LOGINFO)
        
        response = requests.get(movies_url, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            xbmc.log(f"MovieStream: GitHub API error {response.status_code}", xbmc.LOGERROR)
            return []
            
    except Exception as e:
        xbmc.log(f"MovieStream: Basic GitHub collection error: {str(e)}", xbmc.LOGERROR)
        return []

def play_movie(movie_data_str):
    """Play a movie with Cocoscrapers integration - PRIORITY 1"""
    xbmc.log("MovieStream: PLAY_MOVIE CALLED", xbmc.LOGINFO)
    
    try:
        movie_data = json.loads(movie_data_str)
        xbmc.log(f"MovieStream: Movie data received: {movie_data.get('title', 'Unknown')}", xbmc.LOGINFO)
        
        # Show immediate feedback to user
        xbmcgui.Dialog().notification('MovieStream', f'Loading {movie_data.get("title", "movie")}...', xbmcgui.NOTIFICATION_INFO, 2000)
        
        # PRIORITY 1: Try Cocoscrapers (if enabled and available)
        if (CLIENTS_INITIALIZED and 
            addon.getSettingBool('enable_cocoscrapers') and 
            cocoscrapers_client.is_available()):
            
            xbmc.log("MovieStream: Using Cocoscrapers (PRIORITY 1)", xbmc.LOGINFO)
            
            try:
                # Get IMDB ID for better scraping results
                imdb_id = movie_data.get('imdb_id', '')
                if not imdb_id and movie_data.get('tmdb_id'):
                    # Try to get IMDB ID from TMDB
                    try:
                        movie_details = tmdb_client.get_movie_details(movie_data['tmdb_id'])
                        if movie_details and movie_details.get('imdb_id'):
                            imdb_id = movie_details['imdb_id']
                            xbmc.log(f"MovieStream: Retrieved IMDB ID: {imdb_id}", xbmc.LOGINFO)
                    except Exception as e:
                        xbmc.log(f"MovieStream: Error getting IMDB ID: {str(e)}", xbmc.LOGWARNING)
                
                # Scrape sources with Cocoscrapers
                sources = cocoscrapers_client.scrape_movie_sources(
                    title=movie_data['title'],
                    year=movie_data['year'],
                    tmdb_id=movie_data.get('tmdb_id'),
                    imdb_id=imdb_id
                )
                
                if sources:
                    xbmc.log(f"MovieStream: Found {len(sources)} sources via Cocoscrapers", xbmc.LOGINFO)
                    
                    # Filter with debrid services if available
                    if CLIENTS_INITIALIZED and debrid_client.is_available():
                        sources = debrid_client.filter_debrid_sources(sources)
                        xbmc.log(f"MovieStream: After debrid filtering: {len(sources)} sources", xbmc.LOGINFO)
                    
                    if sources:
                        # Auto-play best source or show selection
                        if addon.getSettingBool('auto_play_best_source') and sources:
                            selected_source = sources[0]  # Best source is first
                            xbmc.log("MovieStream: Auto-playing best source", xbmc.LOGINFO)
                        else:
                            selected_source = cocoscrapers_client.show_source_selection(sources, movie_data['title'])
                        
                        if selected_source:
                            # Resolve source
                            resolved_url = cocoscrapers_client.resolve_source(selected_source)
                            
                            if resolved_url:
                                xbmc.log(f"MovieStream: Successfully resolved URL via Cocoscrapers", xbmc.LOGINFO)
                                play_resolved_url(resolved_url, movie_data)
                                return
                            else:
                                xbmc.log("MovieStream: Failed to resolve Cocoscrapers source", xbmc.LOGWARNING)
                        else:
                            xbmc.log("MovieStream: No source selected by user", xbmc.LOGINFO)
                else:
                    xbmc.log("MovieStream: No sources found via Cocoscrapers", xbmc.LOGWARNING)
                    
            except Exception as e:
                xbmc.log(f"MovieStream: Cocoscrapers error: {str(e)}", xbmc.LOGERROR)
        
        # PRIORITY 2: Try M3U8 URL (for GitHub collection with streaming URLs)
        if movie_data.get('m3u8_url'):
            xbmc.log("MovieStream: Using M3U8 URL (PRIORITY 2)", xbmc.LOGINFO)
            try:
                play_resolved_url(movie_data['m3u8_url'], movie_data)
                return
            except Exception as e:
                xbmc.log(f"MovieStream: M3U8 playback error: {str(e)}", xbmc.LOGERROR)
        
        # PRIORITY 3: Try direct video URL (for GitHub collection)
        if movie_data.get('video_url'):
            xbmc.log("MovieStream: Using direct video URL (PRIORITY 3)", xbmc.LOGINFO)
            try:
                play_resolved_url(movie_data['video_url'], movie_data)
                return
            except Exception as e:
                xbmc.log(f"MovieStream: Direct URL playback error: {str(e)}", xbmc.LOGERROR)
        
        # FALLBACK: Use sample video
        xbmc.log("MovieStream: All methods failed, using sample video", xbmc.LOGWARNING)
        xbmcgui.Dialog().notification('MovieStream', 'No sources found - playing sample', xbmcgui.NOTIFICATION_WARNING)
        play_sample_video()
        
    except Exception as e:
        xbmc.log(f"MovieStream: Critical error in play_movie: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Playback failed', xbmcgui.NOTIFICATION_ERROR)
        play_sample_video()

def play_resolved_url(url, item_data):
    """Play a resolved URL with metadata"""
    try:
        xbmc.log(f"MovieStream: Playing resolved URL: {url[:50]}...", xbmc.LOGINFO)
        
        list_item = xbmcgui.ListItem(label=item_data.get('title', 'Unknown'), path=url)
        
        # Set info
        list_item.setInfo('video', {
            'title': item_data.get('title', 'Unknown'),
            'plot': item_data.get('plot', ''),
            'year': int(item_data.get('year', 0)) if str(item_data.get('year', '')).isdigit() else 0,
            'mediatype': item_data.get('type', 'video')
        })
        
        # Set artwork
        if item_data.get('poster_url'):
            list_item.setArt({'thumb': item_data['poster_url']})
        
        # Add to history if available
        if CLIENTS_INITIALIZED and hasattr(watchlist_manager, 'add_to_history'):
            try:
                watchlist_manager.add_to_history(item_data)
            except Exception as e:
                xbmc.log(f"MovieStream: History add error: {str(e)}", xbmc.LOGWARNING)
        
        # Set resolved URL for Kodi
        xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
        xbmc.log("MovieStream: Successfully set resolved URL", xbmc.LOGINFO)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing resolved URL: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'URL resolution failed', xbmcgui.NOTIFICATION_ERROR)

def play_sample_video():
    """Play sample video as fallback"""
    sample_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    list_item = xbmcgui.ListItem(label="Sample Video", path=sample_url)
    list_item.setInfo('video', {'title': 'Sample Video', 'plot': 'Sample video for testing'})
    xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
    xbmc.log("MovieStream: Playing sample video", xbmc.LOGINFO)

def play_episode(episode_data_str=None, show_id=None, season_number=None, episode_number=None):
    """Play a TV episode with Cocoscrapers support"""
    xbmc.log("MovieStream: PLAY_EPISODE CALLED", xbmc.LOGINFO)
    
    try:
        # Handle both old and new parameter formats
        if episode_data_str:
            episode_data = json.loads(episode_data_str)
        else:
            # Legacy format - create episode data from individual parameters
            episode_data = {
                'show_title': f'Show {show_id}',
                'season': int(season_number) if season_number else 1,
                'episode': int(episode_number) if episode_number else 1,
                'show_tmdb_id': show_id,
                'type': 'episode',
                'title': f'Episode {episode_number}',
                'year': '',
                'plot': ''
            }
        
        xbmc.log(f"MovieStream: Episode data: {episode_data.get('show_title', 'Unknown')} S{episode_data.get('season', 1)}E{episode_data.get('episode', 1)}", xbmc.LOGINFO)
        
        # Show immediate feedback
        show_title = f"{episode_data.get('show_title', 'Unknown Show')} S{episode_data.get('season', 1)}E{episode_data.get('episode', 1)}"
        xbmcgui.Dialog().notification('MovieStream', f'Loading {show_title}...', xbmcgui.NOTIFICATION_INFO, 2000)
        
        # PRIORITY 1: Try Cocoscrapers (if enabled and available)
        if (CLIENTS_INITIALIZED and 
            addon.getSettingBool('enable_cocoscrapers') and 
            cocoscrapers_client.is_available()):
            
            xbmc.log("MovieStream: Using Cocoscrapers for episode (PRIORITY 1)", xbmc.LOGINFO)
            
            try:
                # Scrape episode sources with Cocoscrapers
                sources = cocoscrapers_client.scrape_episode_sources(
                    show_title=episode_data['show_title'],
                    year=episode_data.get('year', ''),
                    season=episode_data['season'],
                    episode=episode_data['episode'],
                    show_id=episode_data.get('show_tmdb_id')
                )
                
                if sources:
                    xbmc.log(f"MovieStream: Found {len(sources)} episode sources via Cocoscrapers", xbmc.LOGINFO)
                    
                    # Filter with debrid services if available
                    if CLIENTS_INITIALIZED and debrid_client.is_available():
                        sources = debrid_client.filter_debrid_sources(sources)
                        xbmc.log(f"MovieStream: After debrid filtering: {len(sources)} sources", xbmc.LOGINFO)
                    
                    if sources:
                        # Auto-play best source or show selection
                        if addon.getSettingBool('auto_play_best_source') and sources:
                            selected_source = sources[0]  # Best source is first
                            xbmc.log("MovieStream: Auto-playing best episode source", xbmc.LOGINFO)
                        else:
                            selected_source = cocoscrapers_client.show_source_selection(sources, show_title)
                        
                        if selected_source:
                            # Resolve source
                            resolved_url = cocoscrapers_client.resolve_source(selected_source)
                            
                            if resolved_url:
                                xbmc.log(f"MovieStream: Successfully resolved episode URL via Cocoscrapers", xbmc.LOGINFO)
                                play_resolved_url(resolved_url, episode_data)
                                return
                            else:
                                xbmc.log("MovieStream: Failed to resolve Cocoscrapers episode source", xbmc.LOGWARNING)
                        else:
                            xbmc.log("MovieStream: No episode source selected by user", xbmc.LOGINFO)
                else:
                    xbmc.log("MovieStream: No episode sources found via Cocoscrapers", xbmc.LOGWARNING)
                    
            except Exception as e:
                xbmc.log(f"MovieStream: Cocoscrapers episode error: {str(e)}", xbmc.LOGERROR)
        
        # FALLBACK: Use sample video
        xbmc.log("MovieStream: All episode methods failed, using sample video", xbmc.LOGWARNING)
        xbmcgui.Dialog().notification('MovieStream', 'No episode sources found - playing sample', xbmcgui.NOTIFICATION_WARNING)
        play_sample_video()
        
    except Exception as e:
        xbmc.log(f"MovieStream: Critical error in play_episode: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Episode playback failed', xbmcgui.NOTIFICATION_ERROR)
        play_sample_video()

def test_movie_playback():
    """Test movie playback with sample movie"""
    try:
        # Create test movie data
        test_movie = {
            'title': 'Big Buck Bunny',
            'year': '2008',
            'tmdb_id': '10378',
            'imdb_id': 'tt1254207',
            'type': 'movie',
            'plot': 'Test movie for MovieStream playback functionality'
        }
        
        xbmcgui.Dialog().notification('MovieStream', 'Testing movie playback...', xbmcgui.NOTIFICATION_INFO)
        play_movie(json.dumps(test_movie))
        
    except Exception as e:
        xbmc.log(f"MovieStream: Test playback error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Test Error', f'Test failed: {str(e)}')

def debug_info():
    """Show comprehensive debug information"""
    try:
        # Collect debug information
        info = []
        info.append(f"=== MovieStream Pro Debug Info ===")
        info.append(f"Addon: {addon.getAddonInfo('name')} v{addon.getAddonInfo('version')}")
        info.append(f"")
        info.append(f"=== Initialization Status ===")
        info.append(f"Enhanced Imports Success: {'Yes' if IMPORTS_SUCCESS else 'No'}")
        info.append(f"Basic Clients Ready: {'Yes' if BASIC_CLIENTS_READY else 'No'}")
        info.append(f"Enhanced Clients Ready: {'Yes' if CLIENTS_INITIALIZED else 'No'}")
        info.append(f"")
        info.append(f"=== Client Status ===")
        info.append(f"TMDB Client: {'✅ Ready' if tmdb_client else '❌ Failed'}")
        info.append(f"GitHub Client: {'✅ Ready' if github_client else '❌ Failed'}")
        info.append(f"Video Player: {'✅ Ready' if video_player else '❌ Failed'}")
        info.append(f"Streaming Providers: {'✅ Ready' if streaming_providers else '❌ Failed'}")
        info.append(f"")
        
        if CLIENTS_INITIALIZED:
            info.append(f"=== Enhanced Clients ===")
            info.append(f"Cocoscrapers: {'✅ Available' if cocoscrapers_client and cocoscrapers_client.is_available() else '❌ Not Available'}")
            info.append(f"Debrid Services: {'✅ Available' if debrid_client and debrid_client.is_available() else '❌ Not Available'}")
            info.append(f"TV Show Client: {'✅ Ready' if tvshow_client else '❌ Failed'}")
            info.append(f"Watchlist Manager: {'✅ Ready' if watchlist_manager else '❌ Failed'}")
            info.append(f"")
            
            # Cocoscrapers detailed info
            if cocoscrapers_client and cocoscrapers_client.is_available():
                try:
                    stats = cocoscrapers_client.get_scraper_stats()
                    info.append(f"=== Cocoscrapers Details ===")
                    info.append(f"Total Scrapers: {stats.get('total_scrapers', 'Unknown')}")
                    info.append(f"Enabled Scrapers: {stats.get('enabled_scrapers', 'Unknown')}")
                    info.append(f"")
                except:
                    info.append(f"Cocoscrapers: Stats unavailable")
                    info.append(f"")
        
        info.append(f"=== Settings ===")
        info.append(f"Enable Cocoscrapers: {addon.getSettingBool('enable_cocoscrapers')}")
        info.append(f"Auto Play Best: {addon.getSettingBool('auto_play_best_source')}")
        info.append(f"Scraper Timeout: {addon.getSetting('scraper_timeout')}s")
        info.append(f"TMDB API Key: {'✅ Set' if addon.getSetting('tmdb_api_key') else '❌ Not Set'}")
        github_url = addon.getSetting('github_repo_url')
        info.append(f"GitHub URL: {'✅ Set' if github_url else '❌ Not Set'}")
        if github_url:
            info.append(f"  {github_url[:60]}...")
        
        debug_message = '\n'.join(info)
        xbmcgui.Dialog().textviewer('MovieStream Pro - Debug Information', debug_message)
        
    except Exception as e:
        xbmcgui.Dialog().ok('Debug Error', f'Error collecting debug info: {str(e)}')

def cocoscrapers_status():
    """Show detailed Cocoscrapers status"""
    try:
        if not CLIENTS_INITIALIZED:
            message = "❌ Clients Not Initialized\n\n"
            message += "The addon failed to initialize properly.\n"
            message += "Check the Kodi log for import errors."
        elif cocoscrapers_client.is_available():
            stats = cocoscrapers_client.get_scraper_stats()
            message = f"✅ Cocoscrapers Available\n\n"
            message += f"Total Scrapers: {stats.get('total_scrapers', 'Unknown')}\n"
            message += f"Enabled Scrapers: {stats.get('enabled_scrapers', 'Unknown')}\n"
            message += f"Timeout Setting: {addon.getSetting('scraper_timeout')}s\n"
            message += f"Max Sources: {addon.getSetting('max_sources')}\n\n"
            message += "Cocoscrapers is ready to find streaming sources."
        else:
            message = "❌ Cocoscrapers Not Available\n\n"
            message += "To use Cocoscrapers:\n"
            message += "1. Install 'script.module.cocoscrapers' addon\n"
            message += "2. Install 'script.module.resolveurl' addon (optional)\n"
            message += "3. Restart MovieStream addon\n\n"
            message += "Without Cocoscrapers, only GitHub collection videos will play."
        
        xbmcgui.Dialog().ok('Cocoscrapers Status', message)
        
    except Exception as e:
        xbmcgui.Dialog().ok('Status Error', f'Error checking Cocoscrapers: {str(e)}')

def debrid_status():
    """Show debrid services status"""
    try:
        if not CLIENTS_INITIALIZED or not debrid_client.is_available():
            message = "❌ No Debrid Services Configured\n\n"
            message += "Available services:\n"
            message += "• Real-Debrid\n"
            message += "• Premiumize\n"
            message += "• All-Debrid\n\n"
            message += "Configure API keys in Settings to enable premium links."
        else:
            status = debrid_client.check_account_status()
            message = "💎 Debrid Services Status\n\n"
            
            for service, info in status.items():
                if info:
                    message += f"{info.get('service', service)}: ✅ Active\n"
                    message += f"User: {info.get('username', 'N/A')}\n"
                    message += f"Premium: {'Yes' if info.get('premium', False) else 'No'}\n\n"
                else:
                    message += f"{service}: ❌ Error or Not Configured\n\n"
        
        xbmcgui.Dialog().ok('Debrid Status', message)
        
    except Exception as e:
        xbmcgui.Dialog().ok('Status Error', f'Error checking debrid services: {str(e)}')

def get_video_url_for_movie(movie_details):
    """Get video URL for a movie using multiple providers"""
    
    # Initialize streaming providers
    providers = StreamingProviders()
    
    # Try to get video URL from providers
    video_url = providers.get_video_url(movie_details)
    
    if video_url:
        return video_url
    
    # Fallback to sample URLs for demo
    title = movie_details.get('title', '').replace(' ', '+')
    year = movie_details.get('release_date', '')[:4] if movie_details.get('release_date') else ''
    
    # Sample URLs for demonstration
    sample_urls = [
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"
    ]
    
    import random
    return random.choice(sample_urls)

def get_video_url_for_episode(episode_details, show_id, season_number, episode_number):
    """Get video URL for a TV episode (placeholder implementation)"""
    # Similar to movie implementation but for episodes
    sample_urls = [
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"
    ]
    
    import random
    return random.choice(sample_urls)

def open_settings():
    """Open addon settings"""
    addon.openSettings()

def streaming_providers():
    """Show available streaming providers"""
    xbmcplugin.setPluginCategory(plugin_handle, 'Streaming Providers')
    xbmcplugin.setContent(plugin_handle, 'files')
    
    providers = StreamingProviders()
    available_providers = providers.get_available_providers()
    
    for provider_name in available_providers:
        provider_info = providers.get_provider_info(provider_name)
        
        list_item = xbmcgui.ListItem(label=provider_info['name'])
        list_item.setArt({'thumb': 'DefaultNetwork.png'})
        list_item.setInfo('video', {
            'title': provider_info['name'],
            'plot': provider_info['description']
        })
        
        url = get_url(action='provider_info', provider=provider_name)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def subtitle_manager():
    """Show subtitle management options"""
    xbmcplugin.setPluginCategory(plugin_handle, 'Subtitle Manager')
    xbmcplugin.setContent(plugin_handle, 'files')
    
    subtitle_client = SubtitleClient()
    
    options = [
        ('Supported Languages', 'subtitle_languages', 'View supported subtitle languages'),
        ('Clear Cache', 'clear_subtitle_cache', 'Clear downloaded subtitle cache'),
        ('Download Settings', 'subtitle_settings', 'Configure subtitle preferences')
    ]
    
    for name, action, description in options:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultSubtitles.png'})
        list_item.setInfo('video', {
            'title': name,
            'plot': description
        })
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def tools():
    """Show addon tools and utilities"""
    xbmcplugin.setPluginCategory(plugin_handle, 'Tools')
    xbmcplugin.setContent(plugin_handle, 'files')
    
    tools_list = [
        ('Test TMDB Connection', 'test_tmdb', 'Test connection to TMDB API'),
        ('Test GitHub Connection', 'test_github', 'Test connection to GitHub repository'),
        ('Clear All Cache', 'clear_all_cache', 'Clear all cached data'),
        ('Addon Information', 'addon_info', 'Show addon version and info'),
        ('Generate Sample Database', 'generate_sample_db', 'Generate sample JSON files')
    ]
    
    for name, action, description in tools_list:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultAddonProgram.png'})
        list_item.setInfo('video', {
            'title': name,
            'plot': description
        })
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def test_tmdb():
    """Test TMDB API connection"""
    tmdb = TMDBClient()
    
    try:
        # Test popular movies endpoint
        result = tmdb.get_popular_movies(1)
        
        if result and 'results' in result:
            message = f"✅ TMDB Connection Successful!\n\nFound {len(result['results'])} popular movies.\nTotal pages: {result.get('total_pages', 0)}\nTotal results: {result.get('total_results', 0)}"
            xbmcgui.Dialog().ok('TMDB Test', message)
        else:
            xbmcgui.Dialog().ok('TMDB Test', '❌ TMDB Connection Failed!\n\nNo results returned from API.')
    
    except Exception as e:
        xbmcgui.Dialog().ok('TMDB Test', f'❌ TMDB Connection Error!\n\n{str(e)}')

def test_github():
    """Test GitHub repository connection"""
    github = GitHubClient()
    
    try:
        # Test movie collection endpoint
        result = github.get_movie_collection()
        
        if result:
            message = f"✅ GitHub Connection Successful!\n\nFound {len(result)} movies in collection."
            xbmcgui.Dialog().ok('GitHub Test', message)
        else:
            message = "⚠️ GitHub Connection Warning!\n\nConnected but no movies found.\nCheck your repository URL and JSON files."
            xbmcgui.Dialog().ok('GitHub Test', message)
    
    except Exception as e:
        xbmcgui.Dialog().ok('GitHub Test', f'❌ GitHub Connection Error!\n\n{str(e)}')

def clear_all_cache():
    """Clear all cached data"""
    try:
        # Clear subtitle cache
        subtitle_client = SubtitleClient()
        subtitle_client.clean_subtitle_cache()
        
        # Clear metadata cache (if implemented)
        # ... additional cache clearing logic
        
        xbmcgui.Dialog().notification('MovieStream', 'Cache cleared successfully', xbmcgui.NOTIFICATION_INFO)
    
    except Exception as e:
        xbmcgui.Dialog().notification('MovieStream', f'Cache clear error: {str(e)}', xbmcgui.NOTIFICATION_ERROR)

def addon_info():
    """Show addon information"""
    addon_version = addon.getAddonInfo('version')
    addon_name = addon.getAddonInfo('name')
    addon_author = addon.getAddonInfo('author')
    
    message = f"{addon_name} v{addon_version}\n\nDeveloped by: {addon_author}\n\nFeatures:\n• TMDB Integration\n• GitHub Database\n• Multiple Video Sources\n• Subtitle Support\n• Search Functionality"
    
    xbmcgui.Dialog().ok('Addon Information', message)

def generate_sample_db():
    """Generate sample database files"""
    github = GitHubClient()
    
    try:
        sample_files = github.create_sample_json_files()
        
        # Show generated files info
        files_list = '\n'.join(sample_files.keys())
        message = f"Sample database files generated:\n\n{files_list}\n\nThese files can be uploaded to your GitHub repository."
        
        xbmcgui.Dialog().ok('Sample Database Generated', message)
    
    except Exception as e:
        xbmcgui.Dialog().ok('Generation Error', f'Error generating sample database:\n\n{str(e)}')

def open_settings():
    """Open addon settings"""
    addon.openSettings()

def router(paramstring):
    """Route to the appropriate function based on the provided paramstring"""
    # Parse parameters
    params = dict(urlparse.parse_qsl(paramstring))
    
    # Route to appropriate function
    if params:
        action = params.get('action')
        
        # Main menu actions
        if action == 'movies_menu':
            movies_menu()
        elif action == 'tvshows_menu':
            tvshows_menu()
        elif action == 'search_menu':
            search_menu()
        elif action == 'my_lists_menu':
            my_lists_menu()
        elif action == 'tools_menu':
            tools_menu()
        
        # Movie actions
        elif action == 'movies':
            category = params.get('category', 'popular')
            list_movies(int(params.get('page', 1)), category)
        elif action == 'top_rated_movies':
            list_movies(int(params.get('page', 1)), 'top_rated')
        elif action == 'now_playing_movies':
            list_movies(int(params.get('page', 1)), 'now_playing')
        elif action == 'upcoming_movies':
            list_movies(int(params.get('page', 1)), 'upcoming')
        elif action == 'play_movie':
            play_movie(params.get('movie_data', '{}'))
        elif action == 'search_movies':
            search_movies()
            
        # TV Show actions
        elif action == 'tvshows':
            list_tv_shows(int(params.get('page', 1)))
        elif action == 'search_tv':
            search_tv_shows()
        elif action == 'show_seasons':
            show_seasons(params.get('show_id'))
        elif action == 'show_episodes':
            show_episodes(params.get('show_id'), params.get('season_number'))
        elif action == 'play_episode':
            # Handle both new and legacy episode playback formats
            if params.get('episode_data'):
                play_episode(episode_data_str=params.get('episode_data'))
            else:
                play_episode(show_id=params.get('show_id'), 
                           season_number=params.get('season_number'), 
                           episode_number=params.get('episode_number'))
        
        # Collection actions
        elif action == 'github_collection':
            github_collection()
            
        # Tool actions
        elif action == 'test_tmdb':
            test_tmdb()
        elif action == 'test_github':
            test_github()
        elif action == 'test_movie_playback':
            test_movie_playback()
        elif action == 'debug_info':
            debug_info()
        elif action == 'cocoscrapers_status':
            cocoscrapers_status()
        elif action == 'debrid_status':
            debrid_status()
        elif action == 'clear_all_cache':
            clear_all_cache()
        elif action == 'addon_info':
            addon_info()
            
        # Other actions
        elif action == 'streaming_providers':
            streaming_providers()
        elif action == 'subtitle_manager':
            subtitle_manager()
        elif action == 'generate_sample_db':
            generate_sample_db()
        elif action == 'settings':
            open_settings()
        else:
            # Default to main menu
            list_categories()
    else:
        # No parameters, show main menu
        list_categories()

# Additional missing functions that need to be implemented
def search_tv_shows():
    """Search for TV shows"""
    keyboard = xbmc.Keyboard('', 'Search TV Shows')
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if query:
            xbmcplugin.setPluginCategory(plugin_handle, f'Search: {query}')
            xbmcplugin.setContent(plugin_handle, 'tvshows')
            
            if not CLIENTS_INITIALIZED:
                show_error_message("Search unavailable - client initialization failed")
                return
            
            try:
                # Use TMDB search for TV shows
                api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
                url = f'https://api.themoviedb.org/3/search/tv?api_key={api_key}&query={query}'
                
                response = requests.get(url, timeout=10)
                results = response.json()
                
                for show in results.get('results', [])[:20]:
                    add_tv_show_item(show)
                
                xbmcplugin.endOfDirectory(plugin_handle)
                
            except Exception as e:
                xbmc.log(f"MovieStream: TV search error: {str(e)}", xbmc.LOGERROR)
                show_error_message('TV show search failed')

def tvshows_menu():
    """TV shows submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '📺 TV Shows')
    xbmcplugin.setContent(plugin_handle, 'tvshows')
    
    menu_items = [
        ('Popular TV Shows', 'tvshows', 'popular'),
        ('Top Rated TV Shows', 'top_rated_tvshows', ''),
        ('Airing Today', 'airing_today_tvshows', ''),
        ('Search TV Shows', 'search_tv', '')
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultTVShows.png'})
        list_item.setInfo('video', {'title': name, 'genre': 'Directory'})
        
        url = get_url(action=action, param=param)
        is_folder = action != 'search_tv'
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, is_folder)
    
    xbmcplugin.endOfDirectory(plugin_handle)

if __name__ == '__main__':
    try:
        # Log startup
        xbmc.log("MovieStream: Starting addon", xbmc.LOGINFO)
        xbmc.log(f"MovieStream: Imports successful: {IMPORTS_SUCCESS}", xbmc.LOGINFO)
        xbmc.log(f"MovieStream: Clients initialized: {CLIENTS_INITIALIZED}", xbmc.LOGINFO)
        
        # Route to appropriate function
        router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
        
    except Exception as e:
        xbmc.log(f"MovieStream: Critical startup error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Critical error - check log', xbmcgui.NOTIFICATION_ERROR)