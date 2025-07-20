#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MovieStream Pro - Complete Kodi Addon
Version: 2.0.0 - Fixed Cocoscrapers Integration
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
addon_id = addon.getAddonInfo('id')
plugin_handle = int(sys.argv[1])
base_url = sys.argv[0]

xbmc.log("MovieStream: Addon starting up", xbmc.LOGINFO)

# Initialize clients with error handling
cocoscrapers_client = None
debrid_client = None
tvshow_client = None
watchlist_manager = None

try:
    from resources.lib.cocoscrapers_client import CocoScrapersClient
    cocoscrapers_client = CocoScrapersClient()
    xbmc.log("MovieStream: CocoScrapersClient loaded successfully", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"MovieStream: CocoScrapersClient error: {str(e)}", xbmc.LOGWARNING)

try:
    from resources.lib.debrid_client import DebridClient
    debrid_client = DebridClient()
    xbmc.log("MovieStream: DebridClient loaded successfully", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"MovieStream: DebridClient error: {str(e)}", xbmc.LOGWARNING)

try:
    from resources.lib.tvshow_client import TVShowClient
    tvshow_client = TVShowClient()
    xbmc.log("MovieStream: TVShowClient loaded successfully", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"MovieStream: TVShowClient error: {str(e)}", xbmc.LOGWARNING)

try:
    from resources.lib.watchlist_manager import WatchlistManager
    watchlist_manager = WatchlistManager()
    xbmc.log("MovieStream: WatchlistManager loaded successfully", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"MovieStream: WatchlistManager error: {str(e)}", xbmc.LOGWARNING)

def get_url(**kwargs):
    """Create a URL for calling the plugin"""
    return '{}?{}'.format(base_url, urlparse.urlencode(kwargs))

def list_categories():
    """Display main categories"""
    xbmc.log("MovieStream: Displaying main categories", xbmc.LOGDEBUG)
    xbmcplugin.setPluginCategory(plugin_handle, 'MovieStream Pro')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    categories = [
        ('🎬 Movies', 'movies_menu', 'DefaultMovies.png'),
        ('📺 TV Shows', 'tvshows_menu', 'DefaultTVShows.png'),
        ('🔍 Search', 'search_menu', 'DefaultSearch.png'),
        ('📁 GitHub Collection', 'github_collection', 'DefaultFolder.png'),
        ('⚙️ Tools', 'tools_menu', 'DefaultAddonProgram.png'),
        ('🔧 Settings', 'settings', 'DefaultAddonProgram.png')
    ]
    
    for name, action, icon in categories:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': icon, 'icon': icon})
        
        list_item.setInfo('video', {
            'title': name,
            'genre': 'Directory',
            'mediatype': 'video'
        })
        
        url = get_url(action=action)
        is_folder = action != 'settings'
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, is_folder)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def movies_menu():
    """Movies submenu"""
    xbmc.log("MovieStream: Displaying movies menu", xbmc.LOGDEBUG)
    xbmcplugin.setPluginCategory(plugin_handle, '🎬 Movies')
    
    menu_items = [
        ('Popular Movies', 'tmdb_movies', 'popular'),
        ('Top Rated Movies', 'tmdb_movies', 'top_rated'),
        ('Now Playing', 'tmdb_movies', 'now_playing'),
        ('Upcoming Movies', 'tmdb_movies', 'upcoming'),
        ('Search Movies', 'search_movies', '')
    ]
    
    for name, action, category in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultMovies.png'})
        
        url = get_url(action=action, category=category)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def get_tmdb_movies(category='popular', page=1):
    """Get movies from TMDB API"""
    api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
    
    endpoints = {
        'popular': f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page={page}',
        'top_rated': f'https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}&page={page}',
        'now_playing': f'https://api.themoviedb.org/3/movie/now_playing?api_key={api_key}&page={page}',
        'upcoming': f'https://api.themoviedb.org/3/movie/upcoming?api_key={api_key}&page={page}'
    }
    
    try:
        url = endpoints.get(category, endpoints['popular'])
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        xbmc.log(f"MovieStream: Error getting TMDB movies: {str(e)}", xbmc.LOGERROR)
        return None

def list_tmdb_movies(category='popular', page=1):
    """List movies from TMDB"""
    xbmc.log(f"MovieStream: Listing TMDB movies - category: {category}, page: {page}", xbmc.LOGDEBUG)
    
    category_names = {
        'popular': 'Popular Movies',
        'top_rated': 'Top Rated Movies',
        'now_playing': 'Now Playing',
        'upcoming': 'Upcoming Movies'
    }
    
    xbmcplugin.setPluginCategory(plugin_handle, category_names.get(category, 'Movies'))
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    movies_data = get_tmdb_movies(category, page)
    if movies_data and 'results' in movies_data:
        results = movies_data.get('results', [])
        if results:
            for movie in results:
                add_movie_item(movie, from_tmdb=True)
            
            # Add next page if available
            if page < movies_data.get('total_pages', 1):
                list_item = xbmcgui.ListItem(label='➡️ Next Page >>')
                list_item.setArt({'thumb': 'DefaultFolder.png'})
                url = get_url(action='tmdb_movies', category=category, page=page + 1)
                xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
        else:
            # No results found
            list_item = xbmcgui.ListItem(label='No movies found')
            xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    else:
        # TMDB API error
        list_item = xbmcgui.ListItem(label='❌ TMDB API Error')
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def add_movie_item(movie, from_tmdb=False):
    """Add a movie item to the directory with proper click handling"""
    try:
        title = movie.get('title', 'Unknown Title')
        year = ''
        
        if from_tmdb:
            year = movie.get('release_date', '')[:4] if movie.get('release_date') else ''
        else:
            year = str(movie.get('year', ''))
        
        plot = movie.get('overview', movie.get('plot', 'No description available'))
        
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
                list_item.setArt({'fanart': fanart_url})
        else:
            if movie.get('poster_url'):
                list_item.setArt({'thumb': movie['poster_url'], 'poster': movie['poster_url']})
            if movie.get('backdrop_url'):
                list_item.setArt({'fanart': movie['backdrop_url']})
        
        # Set video info
        list_item.setInfo('video', {
            'title': title,
            'plot': plot,
            'year': int(year) if year.isdigit() else 0,
            'genre': movie.get('genre', ''),
            'rating': float(movie.get('vote_average', movie.get('rating', 0))),
            'votes': str(movie.get('vote_count', 0)),
            'mediatype': 'movie'
        })
        
        # CRITICAL: Set as playable
        list_item.setProperty('IsPlayable', 'true')
        
        # Create movie data for playback
        movie_data = {
            'title': title,
            'year': str(year),
            'tmdb_id': str(movie.get('id', movie.get('tmdb_id', ''))),
            'imdb_id': movie.get('imdb_id', ''),
            'type': 'movie',
            'plot': plot,
            'video_url': movie.get('video_url', ''),
            'm3u8_url': movie.get('m3u8_url', ''),
            'poster_url': movie.get('poster_url', '')
        }
        
        # CRITICAL: Create proper play URL
        url = get_url(action='play_movie', movie_data=json.dumps(movie_data))
        
        # Add directory item with isFolder=False for playable items
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
        
        xbmc.log(f"MovieStream: Added movie item: {title} with URL: {url[:100]}...", xbmc.LOGDEBUG)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error adding movie item: {str(e)}", xbmc.LOGERROR)

def play_movie(movie_data_str):
    """Play a movie - MAIN PLAYBACK FUNCTION"""
    xbmc.log(f"MovieStream: *** PLAY_MOVIE CALLED ***", xbmc.LOGINFO)
    xbmc.log(f"MovieStream: Movie data received: {movie_data_str[:200]}...", xbmc.LOGDEBUG)
    
    try:
        # Parse movie data
        movie_data = json.loads(movie_data_str)
        title = movie_data.get('title', 'Unknown')
        
        xbmc.log(f"MovieStream: Starting playback for: {title}", xbmc.LOGINFO)
        
        # Show notification that we're starting
        xbmcgui.Dialog().notification('MovieStream', f'Loading {title}...', xbmcgui.NOTIFICATION_INFO, 2000)
        
        # Force Cocoscrapers scraping
        if cocoscrapers_client and cocoscrapers_client.is_available():
            xbmc.log(f"MovieStream: Cocoscrapers available - starting scraping for {title}", xbmc.LOGINFO)
            
            # Get movie details
            tmdb_id = movie_data.get('tmdb_id', '')
            imdb_id = movie_data.get('imdb_id', '')
            year = movie_data.get('year', '')
            
            xbmc.log(f"MovieStream: Movie details - TMDB: {tmdb_id}, IMDB: {imdb_id}, Year: {year}", xbmc.LOGDEBUG)
            
            # Try to get IMDB ID if missing
            if tmdb_id and not imdb_id:
                try:
                    enhanced_data = get_enhanced_tmdb_details(tmdb_id, 'movie')
                    if enhanced_data.get('imdb_id'):
                        imdb_id = enhanced_data['imdb_id']
                        xbmc.log(f"MovieStream: Retrieved IMDB ID: {imdb_id}", xbmc.LOGINFO)
                except Exception as e:
                    xbmc.log(f"MovieStream: Error getting IMDB ID: {str(e)}", xbmc.LOGWARNING)
            
            # Start scraping
            xbmc.log(f"MovieStream: Calling scrape_movie_sources for {title}", xbmc.LOGINFO)
            sources = cocoscrapers_client.scrape_movie_sources(
                title=title,
                year=year,
                tmdb_id=tmdb_id,
                imdb_id=imdb_id
            )
            
            xbmc.log(f"MovieStream: Scraping returned {len(sources) if sources else 0} sources", xbmc.LOGINFO)
            
            if sources:
                # Apply debrid filtering if available
                if debrid_client and debrid_client.is_available():
                    sources = debrid_client.filter_debrid_sources(sources)
                    xbmc.log(f"MovieStream: After debrid filtering: {len(sources)} sources", xbmc.LOGDEBUG)
                
                # Handle source selection
                selected_source = None
                if addon.getSettingBool('auto_play_best_source'):
                    selected_source = sources[0]
                    xbmc.log(f"MovieStream: Auto-selected best source: {selected_source.get('provider', 'Unknown')}", xbmc.LOGINFO)
                else:
                    selected_source = cocoscrapers_client.show_source_selection(sources, title)
                
                if selected_source:
                    xbmc.log(f"MovieStream: Selected source: {selected_source.get('provider', 'Unknown')}", xbmc.LOGINFO)
                    
                    # Resolve the source
                    resolved_url = cocoscrapers_client.resolve_source(selected_source)
                    
                    if resolved_url:
                        xbmc.log(f"MovieStream: Source resolved, starting playback", xbmc.LOGINFO)
                        play_resolved_url(resolved_url, movie_data, None)
                        return
                    else:
                        xbmc.log(f"MovieStream: Failed to resolve source", xbmc.LOGERROR)
                        xbmcgui.Dialog().notification('MovieStream', 'Failed to resolve source', xbmcgui.NOTIFICATION_ERROR)
                else:
                    xbmc.log(f"MovieStream: User cancelled source selection", xbmc.LOGINFO)
                    return
            else:
                xbmc.log(f"MovieStream: No sources found via Cocoscrapers", xbmc.LOGWARNING)
        else:
            xbmc.log(f"MovieStream: Cocoscrapers not available", xbmc.LOGWARNING)
        
        # Try fallback sources
        video_url = movie_data.get('video_url', '').strip()
        m3u8_url = movie_data.get('m3u8_url', '').strip()
        
        if m3u8_url:
            xbmc.log(f"MovieStream: Using fallback M3U8 URL", xbmc.LOGINFO)
            play_resolved_url(m3u8_url, movie_data, None)
            return
        elif video_url:
            xbmc.log(f"MovieStream: Using fallback video URL", xbmc.LOGINFO)
            play_resolved_url(video_url, movie_data, None)
            return
        
        # No sources found anywhere
        xbmc.log(f"MovieStream: No playable sources found for {title}", xbmc.LOGWARNING)
        
        error_msg = f'No sources found for {title}'
        if not cocoscrapers_client or not cocoscrapers_client.is_available():
            error_msg += '\n\nCocoscrapers not available.\nInstall script.module.cocoscrapers'
        
        xbmcgui.Dialog().ok('MovieStream - No Sources', error_msg)
        
    except json.JSONDecodeError as e:
        xbmc.log(f"MovieStream: JSON decode error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Data parsing error', xbmcgui.NOTIFICATION_ERROR)
    except Exception as e:
        xbmc.log(f"MovieStream: Playback error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', f'Playback error: {str(e)}', xbmcgui.NOTIFICATION_ERROR)

def play_resolved_url(url, item_data, resume_point=None):
    """Play a resolved URL"""
    try:
        if not url:
            raise ValueError("No URL provided")
        
        title = item_data.get('title', 'Unknown')
        xbmc.log(f"MovieStream: Playing URL for {title}: {str(url)[:100]}...", xbmc.LOGINFO)
        
        list_item = xbmcgui.ListItem(label=title, path=url)
        
        # Set info
        list_item.setInfo('video', {
            'title': title,
            'plot': item_data.get('plot', ''),
            'year': int(item_data.get('year', 0)) if str(item_data.get('year', '')).isdigit() else 0,
            'mediatype': item_data.get('type', 'video')
        })
        
        # Set artwork
        if item_data.get('poster_url'):
            list_item.setArt({'thumb': item_data['poster_url']})
        
        # Handle M3U8/HLS streams
        if any(indicator in url.lower() for indicator in ['.m3u8', 'manifest.m3u8', '/playlist.m3u8']):
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            list_item.setMimeType('application/vnd.apple.mpegurl')
            xbmc.log(f"MovieStream: Set HLS properties for {title}", xbmc.LOGINFO)
        
        # Resolve the URL
        xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
        
        xbmc.log(f"MovieStream: Successfully resolved URL for {title}", xbmc.LOGINFO)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing resolved URL: {str(e)}", xbmc.LOGERROR)
        xbmcplugin.setResolvedUrl(plugin_handle, False, xbmcgui.ListItem())
        xbmcgui.Dialog().notification('MovieStream', f'Playback failed: {str(e)}', xbmcgui.NOTIFICATION_ERROR)

def get_enhanced_tmdb_details(tmdb_id, media_type):
    """Get enhanced TMDB details including external IDs"""
    try:
        api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
        
        if media_type == 'movie':
            url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}&append_to_response=external_ids'
        else:
            url = f'https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={api_key}&append_to_response=external_ids'
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        enhanced_data = {}
        if 'external_ids' in data:
            enhanced_data['imdb_id'] = data['external_ids'].get('imdb_id')
            enhanced_data['tvdb_id'] = data['external_ids'].get('tvdb_id')
        
        return enhanced_data
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error getting enhanced TMDB details: {str(e)}", xbmc.LOGERROR)
        return {}

def github_collection():
    """Show GitHub collection"""
    xbmc.log("MovieStream: Loading GitHub collection", xbmc.LOGDEBUG)
    xbmcplugin.setPluginCategory(plugin_handle, '📁 GitHub Collection')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    try:
        github_url = addon.getSetting('github_repo_url') or 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
        if not github_url.endswith('/'):
            github_url += '/'
        movies_url = github_url + 'movies.json'
        
        response = requests.get(movies_url, timeout=10)
        response.raise_for_status()
        movies = response.json()
        
        if movies:
            for movie in movies:
                add_movie_item(movie, from_tmdb=False)
        else:
            list_item = xbmcgui.ListItem(label='No movies in GitHub collection')
            xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    except Exception as e:
        xbmc.log(f"MovieStream: GitHub error: {str(e)}", xbmc.LOGERROR)
        list_item = xbmcgui.ListItem(label='❌ GitHub Connection Error')
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def search_movies():
    """Search for movies"""
    keyboard = xbmc.Keyboard('', 'Search Movies')
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if query:
            try:
                api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
                url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}'
                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                results = response.json()
                
                xbmcplugin.setPluginCategory(plugin_handle, f'Search: {query}')
                xbmcplugin.setContent(plugin_handle, 'movies')
                
                movies = results.get('results', [])[:20]
                if movies:
                    for movie in movies:
                        add_movie_item(movie, from_tmdb=True)
                else:
                    list_item = xbmcgui.ListItem(label='No results found')
                    xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
                
                xbmcplugin.endOfDirectory(plugin_handle)
                
            except Exception as e:
                xbmc.log(f"MovieStream: Search error: {str(e)}", xbmc.LOGERROR)
                xbmcgui.Dialog().notification('MovieStream', 'Search failed', xbmcgui.NOTIFICATION_ERROR)

def search_menu():
    """Search submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '🔍 Search')
    
    menu_items = [
        ('Search Movies', 'search_movies', ''),
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultSearch.png'})
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def tools_menu():
    """Tools submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '⚙️ Tools')
    
    menu_items = [
        ('🔍 Test TMDB Connection', 'test_tmdb', ''),
        ('📁 Test GitHub Connection', 'test_github', ''),
        ('🎬 Cocoscrapers Status', 'cocoscrapers_status', ''),
        ('🧪 Test Movie Playback', 'test_movie_playback', ''),
        ('📊 Debug Information', 'debug_info', ''),
        ('ℹ️ Addon Information', 'addon_info', '')
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultAddonProgram.png'})
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def test_movie_playback():
    """Test movie playback with a sample movie"""
    try:
        # Create test movie data
        test_movie = {
            'title': 'Big Buck Bunny',
            'year': '2008',
            'tmdb_id': '10378',
            'imdb_id': 'tt1254207',
            'type': 'movie',
            'plot': 'Test movie for playback debugging',
            'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
            'm3u8_url': '',
            'poster_url': ''
        }
        
        xbmc.log("MovieStream: Starting test movie playback", xbmc.LOGINFO)
        play_movie(json.dumps(test_movie))
        
    except Exception as e:
        xbmc.log(f"MovieStream: Test playback error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Test Playback Error', f'Error: {str(e)}')

def cocoscrapers_status():
    """Show Cocoscrapers status"""
    if not cocoscrapers_client:
        message = "❌ Cocoscrapers Client Error\n\nThe Cocoscrapers client failed to initialize."
        xbmcgui.Dialog().ok('Cocoscrapers Status', message)
        return
    
    if cocoscrapers_client.is_available():
        message = "✅ Cocoscrapers Available\n\n"
        message += "Status: Ready to scrape sources\n"
        message += "Module: Loaded successfully\n\n"
        message += "Settings:\n"
        message += f"• Enabled: {addon.getSettingBool('enable_cocoscrapers')}\n"
        message += f"• Timeout: {addon.getSetting('scraper_timeout') or '30'}s\n"
        message += f"• Max Sources: {addon.getSetting('max_sources') or '20'}\n"
        message += f"• Auto-play: {addon.getSettingBool('auto_play_best_source')}"
    else:
        message = "❌ Cocoscrapers Not Available\n\n"
        message += "To enable Cocoscrapers:\n\n"
        message += "1. Install 'script.module.cocoscrapers'\n"
        message += "2. Install 'script.module.resolveurl'\n"
        message += "3. Restart Kodi\n"
        message += "4. Enable in MovieStream settings"
    
    xbmcgui.Dialog().ok('Cocoscrapers Status', message)

def debug_info():
    """Show debug information"""
    try:
        info = []
        info.append("MovieStream Debug Information")
        info.append("=" * 30)
        info.append(f"Addon Version: {addon.getAddonInfo('version')}")
        info.append(f"Kodi Version: {xbmc.getInfoLabel('System.BuildVersion')}")
        info.append("")
        info.append("Module Status:")
        info.append(f"• Cocoscrapers: {'✅' if cocoscrapers_client and cocoscrapers_client.is_available() else '❌'}")
        info.append(f"• Debrid Client: {'✅' if debrid_client else '❌'}")
        info.append(f"• TV Client: {'✅' if tvshow_client else '❌'}")
        info.append(f"• Watchlist: {'✅' if watchlist_manager else '❌'}")
        info.append("")
        info.append("Settings:")
        info.append(f"• Enable Cocoscrapers: {addon.getSettingBool('enable_cocoscrapers')}")
        info.append(f"• Scraper Timeout: {addon.getSetting('scraper_timeout') or '30'}s")
        info.append(f"• Auto-play Best: {addon.getSettingBool('auto_play_best_source')}")
        
        message = "\n".join(info)
        xbmcgui.Dialog().textviewer('MovieStream Debug Info', message)
        
    except Exception as e:
        xbmcgui.Dialog().ok('Debug Error', f'Error getting debug info: {str(e)}')

def test_tmdb():
    """Test TMDB connection"""
    try:
        api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
        url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page=1'
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result and 'results' in result:
            message = f"✅ TMDB Connection Successful!\n\n"
            message += f"Movies found: {len(result['results'])}\n"
            message += f"Total pages: {result.get('total_pages', 0)}"
            xbmcgui.Dialog().ok('TMDB Test', message)
        else:
            xbmcgui.Dialog().ok('TMDB Test', '⚠️ TMDB Connected but no results.')
    
    except Exception as e:
        xbmcgui.Dialog().ok('TMDB Test', f'❌ TMDB Test Failed!\n\n{str(e)}')

def test_github():
    """Test GitHub connection"""
    try:
        github_url = addon.getSetting('github_repo_url') or 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
        if not github_url.endswith('/'):
            github_url += '/'
        movies_url = github_url + 'movies.json'
        
        response = requests.get(movies_url, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result:
            message = f"✅ GitHub Connection Successful!\n\n"
            message += f"Movies found: {len(result)}"
            xbmcgui.Dialog().ok('GitHub Test', message)
        else:
            xbmcgui.Dialog().ok('GitHub Test', '⚠️ GitHub connected but no movies found.')
    
    except Exception as e:
        xbmcgui.Dialog().ok('GitHub Test', f'❌ GitHub Test Failed!\n\n{str(e)}')

def addon_info():
    """Show addon information"""
    addon_version = addon.getAddonInfo('version')
    addon_name = addon.getAddonInfo('name')
    
    message = f"{addon_name} v{addon_version}\n\n"
    message += "Features:\n"
    message += "• TMDB Integration\n"
    message += "• GitHub Database\n"
    message += "• Cocoscrapers Support\n"
    message += "• Advanced Search"
    
    xbmcgui.Dialog().ok('Addon Information', message)

def open_settings():
    """Open addon settings"""
    addon.openSettings()

def router(paramstring):
    """Route to the appropriate function"""
    try:
        params = dict(urlparse.parse_qsl(paramstring))
        xbmc.log(f"MovieStream: Router called with params: {params}", xbmc.LOGDEBUG)
        
        if params:
            action = params.get('action')
            xbmc.log(f"MovieStream: Routing action: {action}", xbmc.LOGINFO)
            
            # Main menus
            if action == 'movies_menu':
                movies_menu()
            elif action == 'search_menu':
                search_menu()
            elif action == 'github_collection':
                github_collection()
            elif action == 'tools_menu':
                tools_menu()
            
            # Movies
            elif action == 'tmdb_movies':
                list_tmdb_movies(params.get('category', 'popular'), int(params.get('page', 1)))
            elif action == 'play_movie':
                xbmc.log(f"MovieStream: PLAY_MOVIE ACTION TRIGGERED", xbmc.LOGINFO)
                play_movie(params.get('movie_data', '{}'))
            elif action == 'search_movies':
                search_movies()
            
            # Tools
            elif action == 'test_tmdb':
                test_tmdb()
            elif action == 'test_github':
                test_github()
            elif action == 'cocoscrapers_status':
                cocoscrapers_status()
            elif action == 'test_movie_playback':
                test_movie_playback()
            elif action == 'debug_info':
                debug_info()
            elif action == 'addon_info':
                addon_info()
            elif action == 'settings':
                open_settings()
            
            else:
                xbmc.log(f"MovieStream: Unknown action: {action}", xbmc.LOGWARNING)
                list_categories()
        else:
            xbmc.log(f"MovieStream: No params, showing main categories", xbmc.LOGDEBUG)
            list_categories()
            
    except Exception as e:
        xbmc.log(f"MovieStream: Router error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', f'Navigation error: {str(e)}', xbmcgui.NOTIFICATION_ERROR)
        list_categories()

if __name__ == '__main__':
    try:
        xbmc.log(f"MovieStream: Main execution started with args: {sys.argv}", xbmc.LOGINFO)
        router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
    except Exception as e:
        xbmc.log(f"MovieStream: Main execution error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Addon startup error', xbmcgui.NOTIFICATION_ERROR)
