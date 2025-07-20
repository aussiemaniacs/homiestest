#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MovieStream Pro - Complete Kodi Addon with Cocoscrapers Integration
Features: TMDB, GitHub, Cocoscrapers, Debrid Services, TV Shows, Watchlist, Favorites
Version: 2.0.0
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
        xbmc.log("MovieStream: All clients initialized successfully", xbmc.LOGINFO)
    except Exception as e:
        xbmc.log(f"MovieStream: Client initialization error: {str(e)}", xbmc.LOGERROR)
        CLIENTS_INITIALIZED = False
        # Initialize basic clients only
        tmdb_client = TMDBClient()
        github_client = GitHubClient()
        video_player = VideoPlayer()
        streaming_providers = StreamingProviders()
else:
    CLIENTS_INITIALIZED = False

def get_url(**kwargs):
    """Create a URL for calling the plugin"""
    return '{}?{}'.format(base_url, urlparse.urlencode(kwargs))

def list_categories():
    """Display main categories"""
    xbmcplugin.setPluginCategory(plugin_handle, 'MovieStream Pro')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    # Check Cocoscrapers status for display
    cocoscrapers_status = "✅" if CLIENTS_INITIALIZED and cocoscrapers_client.is_available() else "❌"
    
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
    status_info = f"Cocoscrapers: {cocoscrapers_status} | Status: {'Ready' if CLIENTS_INITIALIZED else 'Limited Mode'}"
    list_item = xbmcgui.ListItem(label=f"ℹ️ {status_info}")
    list_item.setArt({'thumb': 'DefaultAddonProgram.png'})
    list_item.setInfo('video', {'title': status_info, 'plot': 'Addon status information'})
    url = get_url(action='debug_info')
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def show_error_message(message):
    """Show error message to user"""
    xbmcgui.Dialog().notification('MovieStream Error', message, xbmcgui.NOTIFICATION_ERROR)

def list_movies(page=1):
    """List popular movies from TMDB"""
    xbmcplugin.setPluginCategory(plugin_handle, 'Movies')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    if not CLIENTS_INITIALIZED:
        show_error_message("Client initialization failed")
        return
    
    movies = tmdb_client.get_popular_movies(page)
    
    if movies:
        for movie in movies.get('results', []):
            add_movie_item(movie, from_tmdb=True)
        
        # Add next page if available
        if page < movies.get('total_pages', 1):
            list_item = xbmcgui.ListItem(label='➡️ Next Page >>')
            list_item.setArt({'thumb': 'DefaultFolder.png'})
            url = get_url(action='movies', page=page + 1)
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def list_tv_shows(page=1):
    """List popular TV shows from TMDB"""
    xbmcplugin.setPluginCategory(plugin_handle, 'TV Shows')
    xbmcplugin.setContent(plugin_handle, 'tvshows')
    
    tmdb = TMDBClient()
    shows = tmdb.get_popular_tv_shows(page)
    
    if shows:
        for show in shows.get('results', []):
            add_tv_show_item(show)
        
        # Add next page if available
        if page < shows.get('total_pages', 1):
            list_item = xbmcgui.ListItem(label='Next Page >>')
            list_item.setArt({'thumb': 'DefaultFolder.png'})
            url = get_url(action='tvshows', page=page + 1)
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
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
    """Search for movies"""
    keyboard = xbmc.Keyboard('', 'Search Movies')
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if query:
            xbmcplugin.setPluginCategory(plugin_handle, f'Search: {query}')
            xbmcplugin.setContent(plugin_handle, 'movies')
            
            tmdb = TMDBClient()
            results = tmdb.search_movies(query)
            
            if results:
                for movie in results.get('results', []):
                    add_movie_item(movie)
            
            xbmcplugin.endOfDirectory(plugin_handle)

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
    tmdb = TMDBClient()
    season_details = tmdb.get_season_details(show_id, season_number)
    
    if season_details:
        xbmcplugin.setPluginCategory(plugin_handle, f"Season {season_number}")
        xbmcplugin.setContent(plugin_handle, 'episodes')
        
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
                'episode': episode_number,
                'season': season_number,
                'plot': episode.get('overview', ''),
                'rating': episode.get('vote_average', 0),
                'mediatype': 'episode'
            })
            
            list_item.setProperty('IsPlayable', 'true')
            
            url = get_url(action='play_episode', show_id=show_id, season_number=season_number, episode_number=episode_number)
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
        
        xbmcplugin.endOfDirectory(plugin_handle)

def github_collection():
    """Show GitHub collection"""
    xbmcplugin.setPluginCategory(plugin_handle, 'GitHub Collection')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    github = GitHubClient()
    collection = github.get_movie_collection()
    
    if collection:
        for movie in collection:
            list_item = xbmcgui.ListItem(label=movie.get('title', 'Unknown'))
            
            # Set artwork if available
            if movie.get('poster_url'):
                list_item.setArt({'thumb': movie['poster_url'], 'poster': movie['poster_url']})
            
            list_item.setInfo('video', {
                'title': movie.get('title', ''),
                'year': movie.get('year', 0),
                'plot': movie.get('plot', ''),
                'genre': movie.get('genre', ''),
                'rating': movie.get('rating', 0),
                'mediatype': 'movie'
            })
            
            list_item.setProperty('IsPlayable', 'true')
            
            url = get_url(action='play_github_movie', movie_data=json.dumps(movie))
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

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
        xbmcplugin.setResolvedURL(plugin_handle, True, list_item)
        xbmc.log("MovieStream: Successfully set resolved URL", xbmc.LOGINFO)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing resolved URL: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'URL resolution failed', xbmcgui.NOTIFICATION_ERROR)

def play_sample_video():
    """Play sample video as fallback"""
    sample_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    list_item = xbmcgui.ListItem(label="Sample Video", path=sample_url)
    list_item.setInfo('video', {'title': 'Sample Video', 'plot': 'Sample video for testing'})
    xbmcplugin.setResolvedURL(plugin_handle, True, list_item)
    xbmc.log("MovieStream: Playing sample video", xbmc.LOGINFO)

def play_episode(show_id, season_number, episode_number):
    """Play a TV episode"""
    # Get episode details from TMDB
    tmdb = TMDBClient()
    episode_details = tmdb.get_episode_details(show_id, season_number, episode_number)
    
    if episode_details:
        video_url = get_video_url_for_episode(episode_details, show_id, season_number, episode_number)
        
        if video_url:
            player = VideoPlayer()
            player.play_video(video_url, episode_details)
        else:
            xbmcgui.Dialog().notification('MovieStream', 'No video source found', xbmcgui.NOTIFICATION_WARNING)

def play_github_movie(movie_data):
    """Play a movie from GitHub collection"""
    try:
        movie = json.loads(movie_data)
        video_url = movie.get('video_url')
        
        if video_url:
            player = VideoPlayer()
            player.play_video(video_url, movie)
        else:
            xbmcgui.Dialog().notification('MovieStream', 'No video URL found', xbmcgui.NOTIFICATION_WARNING)
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing GitHub movie: {str(e)}", xbmc.LOGERROR)

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
        
        if action == 'movies':
            list_movies(int(params.get('page', 1)))
        elif action == 'tvshows':
            list_tv_shows(int(params.get('page', 1)))
        elif action == 'search_movies':
            search_movies()
        elif action == 'search_tv':
            search_tv_shows()
        elif action == 'show_seasons':
            show_seasons(params.get('show_id'))
        elif action == 'show_episodes':
            show_episodes(params.get('show_id'), params.get('season_number'))
        elif action == 'play_movie':
            play_movie(params.get('movie_id'))
        elif action == 'play_episode':
            play_episode(params.get('show_id'), params.get('season_number'), params.get('episode_number'))
        elif action == 'github_collection':
            github_collection()
        elif action == 'play_github_movie':
            play_github_movie(params.get('movie_data'))
        elif action == 'streaming_providers':
            streaming_providers()
        elif action == 'subtitle_manager':
            subtitle_manager()
        elif action == 'tools':
            tools()
        elif action == 'test_tmdb':
            test_tmdb()
        elif action == 'test_github':
            test_github()
        elif action == 'clear_all_cache':
            clear_all_cache()
        elif action == 'addon_info':
            addon_info()
        elif action == 'generate_sample_db':
            generate_sample_db()
        elif action == 'settings':
            open_settings()
        else:
            list_categories()
    else:
        list_categories()

if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else '')