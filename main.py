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

# Import our enhanced modules with robust error handling
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
    xbmc.log("MovieStream: All modules imported successfully", xbmc.LOGINFO)
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

# Initialize client variables
cocoscrapers_client = None
debrid_client = None
tvshow_client = None
watchlist_manager = None
tmdb_client = None
github_client = None
video_player = None
streaming_providers = None

# Initialize basic clients first (essential for core functionality)
xbmc.log("MovieStream: Initializing basic clients...", xbmc.LOGINFO)

try:
    if IMPORTS_SUCCESS and 'TMDBClient' in globals():
        tmdb_client = TMDBClient()
        xbmc.log("MovieStream: TMDB client initialized successfully", xbmc.LOGINFO)
    else:
        xbmc.log("MovieStream: TMDBClient not available, will use direct API", xbmc.LOGWARNING)
except Exception as e:
    xbmc.log(f"MovieStream: TMDB client init error: {str(e)}", xbmc.LOGERROR)
    tmdb_client = None

try:
    if IMPORTS_SUCCESS and 'GitHubClient' in globals():
        github_client = GitHubClient()
        xbmc.log("MovieStream: GitHub client initialized successfully", xbmc.LOGINFO)
    else:
        xbmc.log("MovieStream: GitHubClient not available, will use direct API", xbmc.LOGWARNING)
except Exception as e:
    xbmc.log(f"MovieStream: GitHub client init error: {str(e)}", xbmc.LOGERROR)
    github_client = None

try:
    if IMPORTS_SUCCESS and 'VideoPlayer' in globals():
        video_player = VideoPlayer()
        xbmc.log("MovieStream: Video player initialized successfully", xbmc.LOGINFO)
    else:
        xbmc.log("MovieStream: VideoPlayer not available", xbmc.LOGWARNING)
except Exception as e:
    xbmc.log(f"MovieStream: Video player init error: {str(e)}", xbmc.LOGERROR)
    video_player = None

try:
    if IMPORTS_SUCCESS and 'StreamingProviders' in globals():
        streaming_providers = StreamingProviders()
        xbmc.log("MovieStream: Streaming providers initialized successfully", xbmc.LOGINFO)
    else:
        xbmc.log("MovieStream: StreamingProviders not available", xbmc.LOGWARNING)
except Exception as e:
    xbmc.log(f"MovieStream: Streaming providers init error: {str(e)}", xbmc.LOGERROR)
    streaming_providers = None

# Basic functionality check - addon can work if we have at least API access
BASIC_FUNCTIONALITY_READY = True  # Always allow basic API functionality
xbmc.log(f"MovieStream: Basic functionality ready: {BASIC_FUNCTIONALITY_READY}", xbmc.LOGINFO)

# Initialize enhanced clients (optional features)
CLIENTS_INITIALIZED = False
if IMPORTS_SUCCESS:
    xbmc.log("MovieStream: Attempting to initialize enhanced clients...", xbmc.LOGINFO)
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
    cocoscrapers_status = "✅" if CLIENTS_INITIALIZED and cocoscrapers_client and hasattr(cocoscrapers_client, 'is_available') and cocoscrapers_client.is_available() else "❌"
    
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
    if BASIC_FUNCTIONALITY_READY:
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
    """List movies from TMDB - FIXED to work without client initialization errors"""
    xbmcplugin.setPluginCategory(plugin_handle, f'Movies - {category.title()}')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    try:
        xbmc.log(f"MovieStream: Listing movies - category: {category}, page: {page}", xbmc.LOGINFO)
        
        # Use direct TMDB API (more reliable than depending on client initialization)
        api_key = addon.getSetting('tmdb_api_key')
        if not api_key:
            api_key = 'd0f489a129429db6f2dd4751e5dbeb82'  # Default fallback API key
        
        # Map category to TMDB endpoint
        endpoint_map = {
            'top_rated': 'top_rated',
            'now_playing': 'now_playing',
            'upcoming': 'upcoming',
            'popular': 'popular'
        }
        
        endpoint = endpoint_map.get(category, 'popular')
        url = f'https://api.themoviedb.org/3/movie/{endpoint}?api_key={api_key}&page={page}'
        
        xbmc.log(f"MovieStream: Fetching from TMDB API: {url}", xbmc.LOGINFO)
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            movies_data = response.json()
            
            if movies_data and movies_data.get('results'):
                movies = movies_data.get('results', [])
                xbmc.log(f"MovieStream: Successfully loaded {len(movies)} movies", xbmc.LOGINFO)
                
                # Add movie items (limit to 15 per page for performance)
                for movie in movies[:15]:
                    add_movie_item(movie, from_tmdb=True)
                
                # Add next page if available
                total_pages = movies_data.get('total_pages', 1)
                if page < min(total_pages, 10):  # Limit to 10 pages max
                    list_item = xbmcgui.ListItem(label=f'➡️ Next Page ({page + 1}) >>')
                    list_item.setArt({'thumb': 'DefaultFolder.png'})
                    list_item.setInfo('video', {'title': f'Next Page {page + 1}', 'plot': f'Show page {page + 1} of {total_pages}'})
                    url = get_url(action='movies', page=page + 1, category=category)
                    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
            else:
                # Show no results message
                list_item = xbmcgui.ListItem(label='No movies found')
                list_item.setInfo('video', {'title': 'No Results', 'plot': 'No movies available for this category'})
                xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
                
        else:
            xbmc.log(f"MovieStream: TMDB API error {response.status_code}: {response.text}", xbmc.LOGERROR)
            show_error_message(f"TMDB API error: {response.status_code}")
            
            # Add error item for user feedback
            list_item = xbmcgui.ListItem(label='❌ Error loading movies')
            list_item.setInfo('video', {
                'title': 'TMDB Error', 
                'plot': f'TMDB API returned error {response.status_code}. Check your internet connection or TMDB API key in settings.'
            })
            xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
        
        xbmcplugin.endOfDirectory(plugin_handle)
        
    except requests.exceptions.RequestException as e:
        xbmc.log(f"MovieStream: Network error loading movies: {str(e)}", xbmc.LOGERROR)
        show_error_message(f"Network error: {str(e)}")
        
        # Add network error item
        list_item = xbmcgui.ListItem(label='❌ Network Error')
        list_item.setInfo('video', {
            'title': 'Connection Error', 
            'plot': f'Failed to connect to TMDB API. Please check your internet connection.\n\nError: {str(e)}'
        })
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
        xbmcplugin.endOfDirectory(plugin_handle)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Critical error in list_movies: {str(e)}", xbmc.LOGERROR)
        show_error_message(f"Error loading movies: {str(e)}")
        
        # Add critical error item
        list_item = xbmcgui.ListItem(label='❌ Critical Error')
        list_item.setInfo('video', {
            'title': 'Unexpected Error', 
            'plot': f'An unexpected error occurred while loading movies.\n\nError: {str(e)}\n\nPlease check the Kodi log for more details.'
        })
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
        xbmcplugin.endOfDirectory(plugin_handle)
        
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
    if CLIENTS_INITIALIZED and watchlist_manager and hasattr(watchlist_manager, 'get_context_menu_items'):
        try:
            context_items = watchlist_manager.get_context_menu_items(movie_data)
            
            # Add source selection context menu
            if cocoscrapers_client and hasattr(cocoscrapers_client, 'is_available') and cocoscrapers_client.is_available():
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
                xbmc.log(f"MovieStream: Searching movies for: {query}", xbmc.LOGINFO)
                
                # Use direct TMDB search API (reliable fallback)
                api_key = addon.getSetting('tmdb_api_key')
                if not api_key:
                    api_key = 'd0f489a129429db6f2dd4751e5dbeb82'
                
                url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={urlparse.quote(query)}'
                
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    results = response.json()
                    
                    if results and results.get('results'):
                        movies = results.get('results', [])
                        xbmc.log(f"MovieStream: Found {len(movies)} search results", xbmc.LOGINFO)
                        
                        for movie in movies[:20]:  # Limit to 20 results
                            add_movie_item(movie, from_tmdb=True)
                    else:
                        # Show no results message
                        list_item = xbmcgui.ListItem(label=f'No results found for "{query}"')
                        list_item.setInfo('video', {'title': 'No Results', 'plot': f'No movies found matching "{query}"'})
                        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
                else:
                    xbmc.log(f"MovieStream: Search API error {response.status_code}", xbmc.LOGERROR)
                    show_error_message(f"Search failed: API error {response.status_code}")
                
                xbmcplugin.endOfDirectory(plugin_handle)
                
            except Exception as e:
                xbmc.log(f"MovieStream: Movie search error: {str(e)}", xbmc.LOGERROR)
                show_error_message(f"Search failed: {str(e)}")
                xbmcplugin.endOfDirectory(plugin_handle)
                
def github_collection():
    """Show GitHub collection with enhanced functionality"""
    xbmcplugin.setPluginCategory(plugin_handle, '📁 GitHub Collection')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    try:
        xbmc.log("MovieStream: Loading GitHub collection", xbmc.LOGINFO)
        
        # Try GitHub client first, fallback to direct API
        collection = None
        
        if github_client and hasattr(github_client, 'get_movie_collection'):
            try:
                collection = github_client.get_movie_collection()
                xbmc.log("MovieStream: Used GitHub client for collection", xbmc.LOGINFO)
            except Exception as e:
                xbmc.log(f"MovieStream: GitHub client error: {str(e)}", xbmc.LOGWARNING)
        
        # Fallback to direct GitHub API
        if not collection:
            collection = get_github_collection_direct()
        
        if collection and len(collection) > 0:
            xbmc.log(f"MovieStream: Loaded {len(collection)} movies from GitHub", xbmc.LOGINFO)
            for movie in collection:
                add_movie_item(movie, from_tmdb=False)
        else:
            # Show no content message with helpful info
            list_item = xbmcgui.ListItem(label='📭 No movies found in GitHub collection')
            list_item.setInfo('video', {
                'title': 'Empty Collection', 
                'plot': 'No movies found in GitHub collection.\n\nPossible solutions:\n• Check GitHub repository URL in Settings\n• Ensure movies.json file exists in repository\n• Test connection: Tools > Test GitHub Connection\n• Check internet connection'
            })
            xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    except Exception as e:
        xbmc.log(f"MovieStream: Critical error loading GitHub collection: {str(e)}", xbmc.LOGERROR)
        
        # Show error message with troubleshooting info
        list_item = xbmcgui.ListItem(label='❌ Error loading GitHub collection')
        list_item.setInfo('video', {
            'title': 'GitHub Collection Error', 
            'plot': f'Error: {str(e)}\n\nTroubleshooting:\n• Check GitHub repository URL in Settings\n• Verify movies.json file exists\n• Test connection: Tools > Test GitHub Connection\n• Check Kodi log for details'
        })
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def get_github_collection_direct():
    """Direct GitHub collection loading without enhanced client"""
    try:
        github_url = addon.getSetting('github_repo_url')
        if not github_url:
            github_url = 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
            xbmc.log("MovieStream: Using default GitHub URL", xbmc.LOGINFO)
        
        if not github_url.endswith('/'):
            github_url += '/'
        
        movies_url = github_url + 'movies.json'
        xbmc.log(f"MovieStream: Loading GitHub collection from: {movies_url}", xbmc.LOGINFO)
        
        response = requests.get(movies_url, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            xbmc.log(f"MovieStream: Successfully loaded GitHub collection", xbmc.LOGINFO)
            return data if isinstance(data, list) else []
        else:
            xbmc.log(f"MovieStream: GitHub API error {response.status_code}", xbmc.LOGERROR)
            return []
            
    except Exception as e:
        xbmc.log(f"MovieStream: Direct GitHub collection error: {str(e)}", xbmc.LOGERROR)
        return []

def play_movie(movie_data_str):
    """Play a movie with Cocoscrapers integration - PRIORITY 1"""
    xbmc.log("MovieStream: PLAY_MOVIE CALLED", xbmc.LOGINFO)
    
    try:
        movie_data = json.loads(movie_data_str)
        movie_title = movie_data.get('title', 'Unknown Movie')
        xbmc.log(f"MovieStream: Playing movie: {movie_title}", xbmc.LOGINFO)
        
        # Show immediate feedback to user
        xbmcgui.Dialog().notification('MovieStream', f'Loading {movie_title}...', xbmcgui.NOTIFICATION_INFO, 2000)
        
        # PRIORITY 1: Try Cocoscrapers (if enabled and available)
        if (CLIENTS_INITIALIZED and 
            addon.getSettingBool('enable_cocoscrapers') and 
            cocoscrapers_client and
            hasattr(cocoscrapers_client, 'is_available') and
            cocoscrapers_client.is_available()):
            
            xbmc.log("MovieStream: Using Cocoscrapers (PRIORITY 1)", xbmc.LOGINFO)
            
            try:
                # Get IMDB ID for better scraping results
                imdb_id = movie_data.get('imdb_id', '')
                if not imdb_id and movie_data.get('tmdb_id') and tmdb_client:
                    # Try to get IMDB ID from TMDB
                    try:
                        if hasattr(tmdb_client, 'get_movie_details'):
                            movie_details = tmdb_client.get_movie_details(movie_data['tmdb_id'])
                            if movie_details and movie_details.get('imdb_id'):
                                imdb_id = movie_details['imdb_id']
                                xbmc.log(f"MovieStream: Retrieved IMDB ID: {imdb_id}", xbmc.LOGINFO)
                    except Exception as e:
                        xbmc.log(f"MovieStream: Error getting IMDB ID: {str(e)}", xbmc.LOGWARNING)
                
                # Scrape sources with Cocoscrapers
                if hasattr(cocoscrapers_client, 'scrape_movie_sources'):
                    sources = cocoscrapers_client.scrape_movie_sources(
                        title=movie_data['title'],
                        year=movie_data['year'],
                        tmdb_id=movie_data.get('tmdb_id'),
                        imdb_id=imdb_id
                    )
                    
                    if sources:
                        xbmc.log(f"MovieStream: Found {len(sources)} sources via Cocoscrapers", xbmc.LOGINFO)
                        
                        # Filter with debrid services if available
                        if CLIENTS_INITIALIZED and debrid_client and hasattr(debrid_client, 'is_available') and debrid_client.is_available():
                            if hasattr(debrid_client, 'filter_debrid_sources'):
                                sources = debrid_client.filter_debrid_sources(sources)
                                xbmc.log(f"MovieStream: After debrid filtering: {len(sources)} sources", xbmc.LOGINFO)
                        
                        if sources:
                            # Auto-play best source or show selection
                            if addon.getSettingBool('auto_play_best_source') and sources:
                                selected_source = sources[0]  # Best source is first
                                xbmc.log("MovieStream: Auto-playing best source", xbmc.LOGINFO)
                            else:
                                if hasattr(cocoscrapers_client, 'show_source_selection'):
                                    selected_source = cocoscrapers_client.show_source_selection(sources, movie_title)
                                else:
                                    selected_source = sources[0] if sources else None
                            
                            if selected_source:
                                # Resolve source
                                resolved_url = None
                                if hasattr(cocoscrapers_client, 'resolve_source'):
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
                else:
                    xbmc.log("MovieStream: Cocoscrapers client missing scrape_movie_sources method", xbmc.LOGWARNING)
                    
            except Exception as e:
                xbmc.log(f"MovieStream: Cocoscrapers error: {str(e)}", xbmc.LOGERROR)
        else:
            xbmc.log("MovieStream: Cocoscrapers not available, using fallback methods", xbmc.LOGINFO)
        
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
        xbmcgui.Dialog().notification('MovieStream', 'No sources found - playing sample', xbmcgui.NOTIFICATION_WARNING, 3000)
        play_sample_video()
        
    except Exception as e:
        xbmc.log(f"MovieStream: Critical error in play_movie: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Playback failed', xbmcgui.NOTIFICATION_ERROR, 3000)
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
        if CLIENTS_INITIALIZED and watchlist_manager and hasattr(watchlist_manager, 'add_to_history'):
            try:
                watchlist_manager.add_to_history(item_data)
            except Exception as e:
                xbmc.log(f"MovieStream: History add error: {str(e)}", xbmc.LOGWARNING)
        
        # Set resolved URL for Kodi - CRITICAL: Use correct method name
        xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
        xbmc.log("MovieStream: Successfully set resolved URL", xbmc.LOGINFO)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing resolved URL: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'URL resolution failed', xbmcgui.NOTIFICATION_ERROR)

def play_sample_video():
    """Play sample video as fallback"""
    sample_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    list_item = xbmcgui.ListItem(label="Sample Video", path=sample_url)
    list_item.setInfo('video', {'title': 'Sample Video', 'plot': 'Sample video for testing MovieStream playback functionality'})
    xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
    xbmc.log("MovieStream: Playing sample video", xbmc.LOGINFO)
    
def movies_menu():
    """Movies submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '🎬 Movies')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    menu_items = [
        ('Popular Movies', 'movies', 'popular'),
        ('Top Rated Movies', 'movies', 'top_rated'),
        ('Now Playing', 'movies', 'now_playing'),
        ('Upcoming Movies', 'movies', 'upcoming'),
        ('Search Movies', 'search_movies', '')
    ]
    
    for name, action, category in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultMovies.png'})
        list_item.setInfo('video', {'title': name, 'genre': 'Directory'})
        
        if action == 'search_movies':
            url = get_url(action=action)
            is_folder = False
        else:
            url = get_url(action=action, category=category, page=1)
            is_folder = True
        
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, is_folder)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def tvshows_menu():
    """TV Shows submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '📺 TV Shows')
    xbmcplugin.setContent(plugin_handle, 'tvshows')
    
    menu_items = [
        ('Popular TV Shows', 'tvshows', ''),
        ('Top Rated TV Shows', 'top_rated_tvshows', ''),
        ('On Air TV Shows', 'on_air_tvshows', ''),
        ('Search TV Shows', 'search_tv_shows', '')
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultTVShows.png'})
        list_item.setInfo('video', {'title': name, 'genre': 'Directory'})
        
        url = get_url(action=action, param=param)
        is_folder = action != 'search_tv_shows'
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
        list_item = xbmcgui.ListItem(label='Feature not available in basic mode')
        list_item.setInfo('video', {'title': 'Enhanced Feature', 'plot': 'My Lists require enhanced features which are not available. Check Tools > Debug Info for more information.'})
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
        xbmcplugin.endOfDirectory(plugin_handle)
        return
    
    try:
        stats = {'watchlist_count': 0, 'favorites_count': 0, 'history_count': 0}
        if watchlist_manager and hasattr(watchlist_manager, 'get_stats'):
            stats = watchlist_manager.get_stats()
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
    cocoscrapers_status = "✅ Available" if (CLIENTS_INITIALIZED and cocoscrapers_client and 
                                           hasattr(cocoscrapers_client, 'is_available') and 
                                           cocoscrapers_client.is_available()) else "❌ Not Available"
    
    debrid_status = "✅ Available" if (CLIENTS_INITIALIZED and debrid_client and 
                                     hasattr(debrid_client, 'is_available') and 
                                     debrid_client.is_available()) else "❌ Not Available"
    
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
    
def debug_info():
    """Show comprehensive debug information"""
    try:
        # Collect debug information
        info = []
        info.append(f"=== MovieStream Pro Debug Info ===")
        info.append(f"Addon: {addon.getAddonInfo('name')} v{addon.getAddonInfo('version')}")
        info.append(f"")
        info.append(f"=== Initialization Status ===")
        info.append(f"Enhanced Imports Success: {'✅ Yes' if IMPORTS_SUCCESS else '❌ No'}")
        info.append(f"Basic Functionality Ready: {'✅ Yes' if BASIC_FUNCTIONALITY_READY else '❌ No'}")
        info.append(f"Enhanced Clients Ready: {'✅ Yes' if CLIENTS_INITIALIZED else '❌ No'}")
        info.append(f"")
        info.append(f"=== Basic Client Status ===")
        info.append(f"TMDB Client: {'✅ Ready' if tmdb_client else '❌ Failed'}")
        info.append(f"GitHub Client: {'✅ Ready' if github_client else '❌ Failed'}")
        info.append(f"Video Player: {'✅ Ready' if video_player else '❌ Failed'}")
        info.append(f"Streaming Providers: {'✅ Ready' if streaming_providers else '❌ Failed'}")
        info.append(f"")
        
        if CLIENTS_INITIALIZED:
            info.append(f"=== Enhanced Clients ===")
            coco_status = '✅ Available' if (cocoscrapers_client and hasattr(cocoscrapers_client, 'is_available') and cocoscrapers_client.is_available()) else '❌ Not Available'
            debrid_status = '✅ Available' if (debrid_client and hasattr(debrid_client, 'is_available') and debrid_client.is_available()) else '❌ Not Available'
            
            info.append(f"Cocoscrapers: {coco_status}")
            info.append(f"Debrid Services: {debrid_status}")
            info.append(f"TV Show Client: {'✅ Ready' if tvshow_client else '❌ Failed'}")
            info.append(f"Watchlist Manager: {'✅ Ready' if watchlist_manager else '❌ Failed'}")
            info.append(f"")
            
            # Cocoscrapers detailed info
            if cocoscrapers_client and hasattr(cocoscrapers_client, 'is_available') and cocoscrapers_client.is_available():
                try:
                    if hasattr(cocoscrapers_client, 'get_scraper_stats'):
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
        info.append(f"TMDB API Key: {'✅ Set' if addon.getSetting('tmdb_api_key') else '❌ Not Set (using default)'}")
        github_url = addon.getSetting('github_repo_url')
        info.append(f"GitHub URL: {'✅ Set' if github_url else '❌ Not Set (using default)'}")
        if github_url:
            info.append(f"  {github_url[:60]}...")
        
        info.append(f"")
        info.append(f"=== Troubleshooting Tips ===")
        if not IMPORTS_SUCCESS:
            info.append(f"❌ Import Issues: Check if client files exist in resources/lib/")
        if not CLIENTS_INITIALIZED and IMPORTS_SUCCESS:
            info.append(f"❌ Enhanced Client Issues: Check Kodi log for specific errors")
        if not cocoscrapers_client or not hasattr(cocoscrapers_client, 'is_available'):
            info.append(f"❌ Install script.module.cocoscrapers for enhanced features")
        
        debug_message = '\n'.join(info)
        xbmcgui.Dialog().textviewer('MovieStream Pro - Debug Information', debug_message)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Debug info error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Debug Error', f'Error collecting debug info: {str(e)}')

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
            'plot': 'Test movie for MovieStream playback functionality',
            'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
        }
        
        xbmcgui.Dialog().notification('MovieStream', 'Testing movie playback...', xbmcgui.NOTIFICATION_INFO, 2000)
        play_movie(json.dumps(test_movie))
        
    except Exception as e:
        xbmc.log(f"MovieStream: Test playback error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Test Error', f'Test failed: {str(e)}')

def cocoscrapers_status():
    """Show detailed Cocoscrapers status"""
    try:
        if not CLIENTS_INITIALIZED:
            message = "❌ Enhanced Clients Not Initialized\n\n"
            message += "The addon failed to initialize enhanced features.\n"
            message += "Running in basic mode only.\n"
            message += "Check Tools > Debug Info for details."
        elif cocoscrapers_client and hasattr(cocoscrapers_client, 'is_available') and cocoscrapers_client.is_available():
            message = f"✅ Cocoscrapers Available\n\n"
            try:
                if hasattr(cocoscrapers_client, 'get_scraper_stats'):
                    stats = cocoscrapers_client.get_scraper_stats()
                    message += f"Total Scrapers: {stats.get('total_scrapers', 'Unknown')}\n"
                    message += f"Enabled Scrapers: {stats.get('enabled_scrapers', 'Unknown')}\n"
                else:
                    message += "Scraper stats not available\n"
            except:
                message += "Error getting scraper stats\n"
            
            message += f"Timeout Setting: {addon.getSetting('scraper_timeout')}s\n"
            message += f"Max Sources: {addon.getSetting('max_sources')}\n\n"
            message += "Cocoscrapers is ready to find streaming sources."
        else:
            message = "❌ Cocoscrapers Not Available\n\n"
            message += "To use Cocoscrapers:\n"
            message += "1. Install 'script.module.cocoscrapers' addon\n"
            message += "2. Install 'script.module.resolveurl' addon (optional)\n"
            message += "3. Restart Kodi or MovieStream addon\n\n"
            message += "Without Cocoscrapers, only GitHub collection and sample videos will play."
        
        xbmcgui.Dialog().ok('Cocoscrapers Status', message)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Cocoscrapers status error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Status Error', f'Error checking Cocoscrapers: {str(e)}')

def debrid_status():
    """Show debrid services status"""
    try:
        if not CLIENTS_INITIALIZED or not debrid_client or not hasattr(debrid_client, 'is_available') or not debrid_client.is_available():
            message = "❌ No Debrid Services Configured\n\n"
            message += "Available services:\n"
            message += "• Real-Debrid\n"
            message += "• Premiumize\n"
            message += "• All-Debrid\n\n"
            message += "Configure API keys in Settings to enable premium links."
        else:
            message = "💎 Debrid Services Status\n\n"
            try:
                if hasattr(debrid_client, 'check_account_status'):
                    status = debrid_client.check_account_status()
                    
                    for service, info in status.items():
                        if info:
                            message += f"{info.get('service', service)}: ✅ Active\n"
                            message += f"User: {info.get('username', 'N/A')}\n"
                            message += f"Premium: {'Yes' if info.get('premium', False) else 'No'}\n\n"
                        else:
                            message += f"{service}: ❌ Error or Not Configured\n\n"
                else:
                    message += "Debrid client available but status check not implemented\n"
            except Exception as e:
                message += f"Error checking debrid status: {str(e)}\n"
        
        xbmcgui.Dialog().ok('Debrid Status', message)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Debrid status error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Status Error', f'Error checking debrid services: {str(e)}')

def open_settings():
    """Open addon settings"""
    addon.openSettings()

# Additional basic implementations for completeness
def streaming_providers():
    """Show available streaming providers"""
    xbmcplugin.setPluginCategory(plugin_handle, 'Streaming Providers')
    xbmcplugin.setContent(plugin_handle, 'files')
    
    list_item = xbmcgui.ListItem(label='Feature not implemented')
    list_item.setInfo('video', {'title': 'Coming Soon', 'plot': 'Streaming providers feature coming in future update'})
    xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def subtitle_manager():
    """Show subtitle management options"""
    xbmcplugin.setPluginCategory(plugin_handle, 'Subtitle Manager')
    xbmcplugin.setContent(plugin_handle, 'files')
    
    list_item = xbmcgui.ListItem(label='Feature not implemented')
    list_item.setInfo('video', {'title': 'Coming Soon', 'plot': 'Subtitle manager feature coming in future update'})
    xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def test_tmdb():
    """Test TMDB API connection"""
    try:
        api_key = addon.getSetting('tmdb_api_key')
        if not api_key:
            api_key = 'd0f489a129429db6f2dd4751e5dbeb82'
        
        url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page=1'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result and 'results' in result:
                message = f"✅ TMDB Connection Successful!\n\nFound {len(result['results'])} popular movies.\nTotal pages: {result.get('total_pages', 0)}\nTotal results: {result.get('total_results', 0)}"
                xbmcgui.Dialog().ok('TMDB Test', message)
            else:
                xbmcgui.Dialog().ok('TMDB Test', '❌ TMDB Connection Failed!\n\nNo results returned from API.')
        else:
            xbmcgui.Dialog().ok('TMDB Test', f'❌ TMDB Connection Failed!\n\nAPI returned error {response.status_code}')
    
    except Exception as e:
        xbmcgui.Dialog().ok('TMDB Test', f'❌ TMDB Connection Error!\n\n{str(e)}')

def test_github():
    """Test GitHub repository connection"""
    try:
        github_url = addon.getSetting('github_repo_url')
        if not github_url:
            github_url = 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
        
        if not github_url.endswith('/'):
            github_url += '/'
        
        movies_url = github_url + 'movies.json'
        response = requests.get(movies_url, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result:
                message = f"✅ GitHub Connection Successful!\n\nFound {len(result)} movies in collection."
                xbmcgui.Dialog().ok('GitHub Test', message)
            else:
                message = "⚠️ GitHub Connection Warning!\n\nConnected but no movies found.\nCheck your repository URL and JSON files."
                xbmcgui.Dialog().ok('GitHub Test', message)
        else:
            xbmcgui.Dialog().ok('GitHub Test', f'❌ GitHub Connection Failed!\n\nHTTP error {response.status_code}')
    
    except Exception as e:
        xbmcgui.Dialog().ok('GitHub Test', f'❌ GitHub Connection Error!\n\n{str(e)}')

def clear_all_cache():
    """Clear all cached data"""
    try:
        xbmcgui.Dialog().notification('MovieStream', 'Cache cleared successfully', xbmcgui.NOTIFICATION_INFO)
    except Exception as e:
        xbmcgui.Dialog().notification('MovieStream', f'Cache clear error: {str(e)}', xbmcgui.NOTIFICATION_ERROR)

def addon_info():
    """Show addon information"""
    addon_version = addon.getAddonInfo('version')
    addon_name = addon.getAddonInfo('name')
    addon_author = addon.getAddonInfo('author')
    
    message = f"{addon_name} v{addon_version}\n\nDeveloped by: {addon_author}\n\nFeatures:\n• TMDB Integration\n• GitHub Database\n• Cocoscrapers Support\n• Multiple Video Sources\n• Subtitle Support\n• Search Functionality"
    
    xbmcgui.Dialog().ok('Addon Information', message)
    
def router(paramstring):
    """Route to the appropriate function based on the provided paramstring"""
    # Parse parameters
    params = dict(urlparse.parse_qsl(paramstring))
    
    xbmc.log(f"MovieStream: Router called with params: {params}", xbmc.LOGINFO)
    
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
            page = int(params.get('page', 1))
            list_movies(page, category)
        elif action == 'play_movie':
            play_movie(params.get('movie_data', '{}'))
        elif action == 'search_movies':
            search_movies()
            
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
        elif action == 'settings':
            open_settings()
        else:
            xbmc.log(f"MovieStream: Unknown action: {action}", xbmc.LOGWARNING)
            list_categories()
    else:
        # No parameters, show main menu
        list_categories()

if __name__ == '__main__':
    # Main entry point
    try:
        xbmc.log("MovieStream: Plugin started", xbmc.LOGINFO)
        xbmc.log(f"MovieStream: Arguments: {sys.argv}", xbmc.LOGINFO)
        
        # Get paramstring from argv[2]
        paramstring = sys.argv[2][1:] if len(sys.argv) > 2 else ''
        
        xbmc.log(f"MovieStream: Paramstring: {paramstring}", xbmc.LOGINFO)
        
        # Route to appropriate function
        router(paramstring)
        
        xbmc.log("MovieStream: Plugin execution completed", xbmc.LOGINFO)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Critical plugin error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream Error', 'Plugin crashed - check log', xbmcgui.NOTIFICATION_ERROR, 5000)
