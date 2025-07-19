f#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MovieStream Pro - Complete Kodi Addon
Features: TMDB, GitHub, Cocoscrapers, Debrid Services, TV Shows, Watchlist, Favorites
Version: 2.0.0
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
    xbmcplugin.setPluginCategory(plugin_handle, 'MovieStream Pro')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    categories = [
        ('🎬 Movies', 'movies_menu', 'DefaultMovies.png'),
        ('📺 TV Shows', 'tvshows_menu', 'DefaultTVShows.png'),
        ('🔍 Search', 'search_menu', 'DefaultSearch.png'),
        ('⭐ My Lists', 'my_lists', 'DefaultPlaylist.png'),
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

def tvshows_menu():
    """TV shows submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '📺 TV Shows')
    
    if not tvshow_client:
        list_item = xbmcgui.ListItem(label='❌ TV Shows client not available')
        list_item.setInfo('video', {'title': 'Error', 'plot': 'TV Shows functionality is not available'})
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
        xbmcplugin.endOfDirectory(plugin_handle)
        return
    
    menu_items = [
        ('Popular TV Shows', 'list_tv_shows', 'popular'),
        ('Top Rated TV Shows', 'list_tv_shows', 'top_rated'),
        ('Airing Today', 'list_tv_shows', 'airing_today'),
        ('Search TV Shows', 'search_tv_shows', '')
    ]
    
    for name, action, category in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultTVShows.png'})
        
        url = get_url(action=action, category=category)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def search_menu():
    """Search submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '🔍 Search')
    
    menu_items = [
        ('Search Movies', 'search_movies', ''),
        ('Search TV Shows', 'search_tv_shows', ''),
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultSearch.png'})
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def my_lists():
    """My Lists submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '⭐ My Lists')
    
    if not watchlist_manager:
        list_item = xbmcgui.ListItem(label='❌ Watchlist manager not available')
        list_item.setInfo('video', {'title': 'Error', 'plot': 'Watchlist functionality is not available'})
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
        xbmcplugin.endOfDirectory(plugin_handle)
        return
    
    try:
        stats = watchlist_manager.get_stats()
    except:
        stats = {'watchlist_count': 0, 'favorites_count': 0, 'history_count': 0, 'resume_count': 0}
    
    menu_items = [
        (f"📋 Watchlist ({stats['watchlist_count']})", 'list_watchlist', ''),
        (f"❤️ Favorites ({stats['favorites_count']})", 'list_favorites', ''),
        (f"📖 Watch History ({stats['history_count']})", 'list_history', ''),
        (f"⏸️ Resume ({stats['resume_count']})", 'list_resume', '')
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultPlaylist.png'})
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def tools_menu():
    """Tools submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '⚙️ Tools')
    
    menu_items = [
        ('🔍 Test TMDB Connection', 'test_tmdb', ''),
        ('📁 Test GitHub Connection', 'test_github', ''),
        ('🎬 Cocoscrapers Status', 'cocoscrapers_status', ''),
        ('💎 Debrid Account Status', 'debrid_status', ''),
        ('📊 Addon Statistics', 'addon_stats', ''),
        ('🗑️ Clear All Cache', 'clear_cache', ''),
        ('ℹ️ Addon Information', 'addon_info', '')
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultAddonProgram.png'})
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def github_collection():
    """Show GitHub collection"""
    xbmcplugin.setPluginCategory(plugin_handle, '📁 GitHub Collection')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    try:
        github_url = addon.getSetting('github_repo_url') or 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
        if not github_url.endswith('/'):
            github_url += '/'
        movies_url = github_url + 'movies.json'
        
        xbmc.log(f"MovieStream: Attempting to load GitHub collection from: {movies_url}", xbmc.LOGINFO)
        
        response = requests.get(movies_url, timeout=10)
        response.raise_for_status()
        movies = response.json()
        
        if not movies:
            list_item = xbmcgui.ListItem(label='⚠️ No movies found in GitHub collection')
            list_item.setInfo('video', {'title': 'Warning', 'plot': 'GitHub collection is empty'})
            xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
        else:
            for movie in movies:
                add_movie_item(movie, from_tmdb=False)
    
    except requests.exceptions.RequestException as e:
        xbmc.log(f"MovieStream: GitHub connection error: {str(e)}", xbmc.LOGERROR)
        list_item = xbmcgui.ListItem(label='❌ GitHub Connection Error')
        list_item.setInfo('video', {'title': 'Connection Error', 'plot': f'Cannot connect to GitHub repository: {str(e)}'})
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    except json.JSONDecodeError as e:
        xbmc.log(f"MovieStream: GitHub JSON error: {str(e)}", xbmc.LOGERROR)
        list_item = xbmcgui.ListItem(label='❌ GitHub JSON Error')
        list_item.setInfo('video', {'title': 'JSON Error', 'plot': 'Invalid JSON format in movies.json file'})
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    except Exception as e:
        xbmc.log(f"MovieStream: GitHub general error: {str(e)}", xbmc.LOGERROR)
        list_item = xbmcgui.ListItem(label='❌ Error loading GitHub collection')
        list_item.setInfo('video', {'title': 'Error', 'plot': 'Check GitHub repository URL in settings'})
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def test_github():
    """Test GitHub connection with detailed feedback"""
    try:
        github_url = addon.getSetting('github_repo_url') or 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
        if not github_url.endswith('/'):
            github_url += '/'
        
        # Test movies.json
        movies_url = github_url + 'movies.json'
        xbmc.log(f"MovieStream: Testing GitHub URL: {movies_url}", xbmc.LOGINFO)
        
        response = requests.get(movies_url, timeout=10)
        response.raise_for_status()
        
        try:
            result = response.json()
            if isinstance(result, list):
                message = f"✅ GitHub Connection Successful!\n\n"
                message += f"Repository URL: {github_url}\n"
                message += f"Movies found: {len(result)}\n"
                message += f"Status code: {response.status_code}\n\n"
                
                if len(result) > 0:
                    sample_movie = result[0]
                    message += f"Sample movie: {sample_movie.get('title', 'Unknown')}"
                
                xbmcgui.Dialog().ok('GitHub Test - Success', message)
            else:
                xbmcgui.Dialog().ok('GitHub Test - Warning', 
                    f"⚠️ GitHub Connected but Invalid Format!\n\n"
                    f"Expected: JSON array\n"
                    f"Found: {type(result)}\n\n"
                    f"Check your movies.json file structure.")
        except json.JSONDecodeError as je:
            xbmcgui.Dialog().ok('GitHub Test - JSON Error', 
                f"❌ Invalid JSON Format!\n\n"
                f"URL: {movies_url}\n"
                f"Error: {str(je)}\n\n"
                f"Please validate your JSON syntax.")
    
    except requests.exceptions.ConnectionError:
        xbmcgui.Dialog().ok('GitHub Test - Connection Error', 
            f"❌ Cannot Connect to GitHub!\n\n"
            f"URL: {github_url}\n\n"
            f"Check:\n"
            f"• Internet connection\n"
            f"• Repository URL spelling\n"
            f"• Repository is public")
    
    except requests.exceptions.HTTPError as he:
        status_code = he.response.status_code if he.response else 'Unknown'
        xbmcgui.Dialog().ok('GitHub Test - HTTP Error', 
            f"❌ HTTP Error {status_code}!\n\n"
            f"URL: {movies_url}\n\n"
            f"Common causes:\n"
            f"• File not found (404)\n"
            f"• Repository is private\n"
            f"• Invalid URL format")
    
    except Exception as e:
        xbmcgui.Dialog().ok('GitHub Test - Error', f'❌ GitHub Test Failed!\n\n{str(e)}')

# Rest of the functions remain the same but with better error handling...
def get_tmdb_movies(category='popular', page=1):
    """Get movies from TMDB API with error handling"""
    api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
    
    endpoints = {
        'popular': f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page={page}',
        'top_rated': f'https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}&page={page}',
        'now_playing': f'https://api.themoviedb.org/3/movie/now_playing?api_key={api_key}&page={page}',
        'upcoming': f'https://api.themoviedb.org/3/movie/upcoming?api_key={api_key}&page={page}'
    }
    
    try:
        url = endpoints.get(category, endpoints['popular'])
        xbmc.log(f"MovieStream: Requesting TMDB: {url}", xbmc.LOGDEBUG)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        xbmc.log(f"MovieStream: Error getting TMDB movies: {str(e)}", xbmc.LOGERROR)
        return None

def list_tmdb_movies(category='popular', page=1):
    """List movies from TMDB with error handling"""
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
            list_item.setInfo('video', {'title': 'No Results', 'plot': 'No movies found for this category'})
            xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    else:
        # TMDB API error
        list_item = xbmcgui.ListItem(label='❌ TMDB API Error')
        list_item.setInfo('video', {'title': 'API Error', 'plot': 'Cannot connect to TMDB. Check your API key and internet connection.'})
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def add_movie_item(movie, from_tmdb=False):
    """Add a movie item to the directory with error handling"""
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
        
        # Set artwork with error handling
        try:
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
        except Exception as e:
            xbmc.log(f"MovieStream: Error setting artwork: {str(e)}", xbmc.LOGWARNING)
        
        # Set video info
        list_item.setInfo('video', {
            'title': title,
            'plot': plot,
            'year': int(year) if year.isdigit() else 0,
            'genre': movie.get('genre', ''),
            'rating': float(movie.get('vote_average', movie.get('rating', 0))),
            'votes': str(movie.get('vote_count', 0)),
            'director': movie.get('director', ''),
            'duration': movie.get('runtime', 0) * 60 if movie.get('runtime') else 0,
            'mediatype': 'movie'
        })
        
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
            'video_url': movie.get('video_url', ''),
            'm3u8_url': movie.get('m3u8_url', '')
        }
        
        # Add context menu items if watchlist manager is available
        try:
            if addon.getSettingBool('enable_context_menus') and watchlist_manager:
                context_items = watchlist_manager.get_context_menu_items(movie_data)
                
                if cocoscrapers_client and cocoscrapers_client.is_available():
                    context_items.append((
                        'Select Source',
                        f'RunPlugin({get_url(action="select_movie_source", movie_data=json.dumps(movie_data))})'
                    ))
                
                list_item.addContextMenuItems(context_items)
        except Exception as e:
            xbmc.log(f"MovieStream: Error adding context menu: {str(e)}", xbmc.LOGWARNING)
        
        url = get_url(action='play_movie', movie_data=json.dumps(movie_data))
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error adding movie item: {str(e)}", xbmc.LOGERROR)
        # Add error item
        list_item = xbmcgui.ListItem(label=f'❌ Error: {movie.get("title", "Unknown")}')
        list_item.setInfo('video', {'title': 'Error', 'plot': f'Error loading movie: {str(e)}'})
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)

def play_movie(movie_data_str):
    """Play a movie with Cocoscrapers prioritized"""
    try:
        movie_data = json.loads(movie_data_str)
        title = movie_data.get('title', 'Unknown')
        
        xbmc.log(f"MovieStream: Play movie requested: {title}", xbmc.LOGINFO)
        
        # Check for resume point
        resume_point = None
        if watchlist_manager:
            try:
                resume_point = watchlist_manager.get_resume_point(movie_data)
                if resume_point:
                    choice = xbmcgui.Dialog().yesno(
                        'Resume Playback',
                        f"Resume from {int(resume_point['percentage'])}%?",
                        'Start Over', 'Resume'
                    )
                    if not choice:  # Start over
                        watchlist_manager.remove_resume_point(movie_data)
            except Exception as e:
                xbmc.log(f"MovieStream: Resume point error: {str(e)}", xbmc.LOGWARNING)
        
        # PRIORITY 1: Try Cocoscrapers if enabled and available
        if cocoscrapers_client and cocoscrapers_client.is_available() and addon.getSettingBool('enable_cocoscrapers'):
            xbmc.log(f"MovieStream: Attempting Cocoscrapers scraping for: {title}", xbmc.LOGINFO)
            
            try:
                # Get enhanced TMDB info if available
                tmdb_id = movie_data.get('tmdb_id')
                imdb_id = movie_data.get('imdb_id')
                year = movie_data.get('year', '')
                
                # If we have TMDB ID, try to get external IDs
                if tmdb_id and not imdb_id:
                    try:
                        enhanced_data = get_enhanced_tmdb_details(tmdb_id, 'movie')
                        if enhanced_data.get('imdb_id'):
                            imdb_id = enhanced_data['imdb_id']
                            xbmc.log(f"MovieStream: Got IMDB ID from TMDB: {imdb_id}", xbmc.LOGDEBUG)
                    except Exception as e:
                        xbmc.log(f"MovieStream: Error getting enhanced TMDB details: {str(e)}", xbmc.LOGWARNING)
                
                # Scrape sources with Cocoscrapers
                sources = cocoscrapers_client.scrape_movie_sources(
                    title=title,
                    year=year,
                    tmdb_id=tmdb_id,
                    imdb_id=imdb_id
                )
                
                # Filter with debrid services if available
                if debrid_client and debrid_client.is_available() and sources:
                    xbmc.log("MovieStream: Filtering sources with debrid services", xbmc.LOGDEBUG)
                    sources = debrid_client.filter_debrid_sources(sources)
                
                if sources:
                    xbmc.log(f"MovieStream: Found {len(sources)} sources via Cocoscrapers", xbmc.LOGINFO)
                    
                    # Handle source selection
                    selected_source = None
                    if addon.getSettingBool('auto_play_best_source') and len(sources) > 0:
                        selected_source = sources[0]
                        xbmc.log(f"MovieStream: Auto-playing best source: {selected_source.get('provider', 'Unknown')}", xbmc.LOGINFO)
                    else:
                        selected_source = cocoscrapers_client.show_source_selection(sources, title)
                    
                    if selected_source:
                        # Resolve the selected source
                        resolved_url = cocoscrapers_client.resolve_source(selected_source)
                        
                        if resolved_url:
                            xbmc.log(f"MovieStream: Playing resolved URL for {title}", xbmc.LOGINFO)
                            play_resolved_url(resolved_url, movie_data, resume_point)
                            return
                        else:
                            xbmc.log(f"MovieStream: Failed to resolve selected source for {title}", xbmc.LOGERROR)
                    else:
                        xbmc.log(f"MovieStream: No source selected for {title}", xbmc.LOGINFO)
                else:
                    xbmc.log(f"MovieStream: No sources found via Cocoscrapers for {title}", xbmc.LOGWARNING)
                    
            except Exception as e:
                xbmc.log(f"MovieStream: Cocoscrapers error for {title}: {str(e)}", xbmc.LOGERROR)
        
        # PRIORITY 2: Try direct M3U8 URL (if available)
        m3u8_url = movie_data.get('m3u8_url')
        if m3u8_url and m3u8_url.strip():
            xbmc.log(f"MovieStream: Using M3U8 URL for {title}", xbmc.LOGINFO)
            play_resolved_url(m3u8_url, movie_data, resume_point)
            return
        
        # PRIORITY 3: Try direct video URL (if available)
        video_url = movie_data.get('video_url')
        if video_url and video_url.strip():
            xbmc.log(f"MovieStream: Using direct video URL for {title}", xbmc.LOGINFO)
            play_resolved_url(video_url, movie_data, resume_point)
            return
        
        # No sources found anywhere
        xbmc.log(f"MovieStream: No playable sources found for {title}", xbmc.LOGWARNING)
        
        # Show detailed error message
        error_msg = f'No sources found for {title}\n\n'
        if not cocoscrapers_client or not cocoscrapers_client.is_available():
            error_msg += 'Cocoscrapers not available.\n'
        if not addon.getSettingBool('enable_cocoscrapers'):
            error_msg += 'Cocoscrapers disabled in settings.\n'
        if not movie_data.get('video_url') and not movie_data.get('m3u8_url'):
            error_msg += 'No direct URLs in database.\n'
        
        error_msg += '\nCheck Tools > Cocoscrapers Status'
        
        xbmcgui.Dialog().ok('MovieStream - No Sources', error_msg)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing movie: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', f'Playback error: {str(e)}', xbmcgui.NOTIFICATION_ERROR)

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
        
        # No sources found
        xbmc.log(f"MovieStream: No playable sources found for {title}", xbmc.LOGWARNING)
        xbmcgui.Dialog().notification(
            'MovieStream', 
            f'No sources found for {title}', 
            xbmcgui.NOTIFICATION_WARNING,
            5000
        )
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing movie: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Playback error occurred', xbmcgui.NOTIFICATION_ERROR)

def play_resolved_url(url, item_data, resume_point=None):
    """Play a resolved URL with metadata and error handling"""
    try:
        if not url:
            raise ValueError("No URL provided")
        
        title = item_data.get('title', 'Unknown')
        xbmc.log(f"MovieStream: Playing URL for {title}: {url[:100]}...", xbmc.LOGINFO)
        
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
        
        # Set resume point
        if resume_point:
            list_item.setProperty('ResumeTime', str(resume_point['position']))
            list_item.setProperty('TotalTime', str(resume_point['total_time']))
        
        # Handle M3U8/HLS streams
        if url.lower().endswith('.m3u8') or 'manifest.m3u8' in url.lower() or '/playlist.m3u8' in url.lower():
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            list_item.setMimeType('application/vnd.apple.mpegurl')
            xbmc.log(f"MovieStream: Set HLS properties for {title}", xbmc.LOGINFO)
        
        # Add to history
        if watchlist_manager:
            try:
                watchlist_manager.add_to_history(item_data)
            except Exception as e:
                xbmc.log(f"MovieStream: Error adding to history: {str(e)}", xbmc.LOGWARNING)
        
        xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing resolved URL: {str(e)}", xbmc.LOGERROR)
        xbmcplugin.setResolvedUrl(plugin_handle, False, xbmcgui.ListItem())
        xbmcgui.Dialog().notification('MovieStream', f'Playback failed: {str(e)}', xbmcgui.NOTIFICATION_ERROR)

# Simplified search functions with error handling
def search_movies():
    """Search for movies with error handling"""
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
                
                movies = results.get('results', [])[:20]  # Limit to 20 results
                if movies:
                    for movie in movies:
                        add_movie_item(movie, from_tmdb=True)
                else:
                    list_item = xbmcgui.ListItem(label='No results found')
                    list_item.setInfo('video', {'title': 'No Results', 'plot': f'No movies found for: {query}'})
                    xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
                
                xbmcplugin.endOfDirectory(plugin_handle)
                
            except Exception as e:
                xbmc.log(f"MovieStream: Search error: {str(e)}", xbmc.LOGERROR)
                xbmcgui.Dialog().notification('MovieStream', 'Search failed', xbmcgui.NOTIFICATION_ERROR)

def search_tv_shows():
    """Search for TV shows"""
    if not tvshow_client:
        xbmcgui.Dialog().notification('MovieStream', 'TV Shows not available', xbmcgui.NOTIFICATION_WARNING)
        return
    
    keyboard = xbmc.Keyboard('', 'Search TV Shows')
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if query:
            try:
                results = tvshow_client.search_shows(query)
                
                xbmcplugin.setPluginCategory(plugin_handle, f'Search: {query}')
                xbmcplugin.setContent(plugin_handle, 'tvshows')
                
                shows = results.get('results', [])[:20] if results else []
                if shows:
                    for show in shows:
                        add_tv_show_item(show)
                else:
                    list_item = xbmcgui.ListItem(label='No results found')
                    list_item.setInfo('video', {'title': 'No Results', 'plot': f'No TV shows found for: {query}'})
                    xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
                
                xbmcplugin.endOfDirectory(plugin_handle)
                
            except Exception as e:
                xbmc.log(f"MovieStream: TV search error: {str(e)}", xbmc.LOGERROR)
                xbmcgui.Dialog().notification('MovieStream', 'Search failed', xbmcgui.NOTIFICATION_ERROR)

# Tool functions with enhanced feedback
def test_tmdb():
    """Test TMDB connection with detailed feedback"""
    try:
        api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
        url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page=1'
        
        xbmc.log(f"MovieStream: Testing TMDB with URL: {url}", xbmc.LOGINFO)
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result and 'results' in result:
            message = f"✅ TMDB Connection Successful!\n\n"
            message += f"API Key: {api_key[:10]}...\n"
            message += f"Movies found: {len(result['results'])}\n"
            message += f"Total pages: {result.get('total_pages', 0)}\n"
            message += f"Status: {response.status_code}"
            xbmcgui.Dialog().ok('TMDB Test - Success', message)
        else:
            xbmcgui.Dialog().ok('TMDB Test - Warning', '⚠️ TMDB Connected but no results returned.')
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 'Unknown'
        if status_code == 401:
            xbmcgui.Dialog().ok('TMDB Test - API Key Error', 
                '❌ Invalid TMDB API Key!\n\n'
                'Get a free API key from:\n'
                'https://www.themoviedb.org/settings/api')
        else:
            xbmcgui.Dialog().ok('TMDB Test - HTTP Error', f'❌ HTTP Error {status_code}!\n\n{str(e)}')
    
    except Exception as e:
        xbmcgui.Dialog().ok('TMDB Test - Error', f'❌ TMDB Test Failed!\n\n{str(e)}')

def cocoscrapers_status():
    """Show detailed Cocoscrapers status"""
    if not cocoscrapers_client:
        message = "❌ Cocoscrapers Client Error\n\n"
        message += "The Cocoscrapers client failed to initialize.\n\n"
        message += "This could be due to:\n"
        message += "• Missing dependencies\n"
        message += "• Import errors\n"
        message += "• Module conflicts"
        xbmcgui.Dialog().ok('Cocoscrapers Status', message)
        return
    
    try:
        stats = cocoscrapers_client.get_scraper_stats()
        
        if stats['available']:
            message = f"✅ Cocoscrapers Available\n\n"
            message += f"Total Scrapers: {stats.get('total_scrapers', 0)}\n"
            message += f"Enabled Scrapers: {stats.get('enabled_scrapers', 0)}\n\n"
            message += "Status: Ready to find streaming sources\n\n"
            message += "Configure in Settings:\n"
            message += "• Maximum sources\n"
            message += "• Quality filters\n"
            message += "• Auto-play preferences"
        else:
            message = "❌ Cocoscrapers Not Available\n\n"
            message += "To enable Cocoscrapers:\n\n"
            message += "1. Install 'script.module.cocoscrapers'\n"
            message += "2. Install 'script.module.resolveurl'\n"
            message += "3. Restart Kodi\n"
            message += "4. Enable in MovieStream settings\n\n"
            message += "Without Cocoscrapers:\n"
            message += "• Only direct links will work\n"
            message += "• GitHub database content only"
        
        xbmcgui.Dialog().ok('Cocoscrapers Status', message)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error getting Cocoscrapers status: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Cocoscrapers Status', f'❌ Error checking status!\n\n{str(e)}')

def debrid_status():
    """Show detailed debrid services status"""
    if not debrid_client:
        message = "❌ Debrid Client Error\n\n"
        message += "The debrid client failed to initialize."
        xbmcgui.Dialog().ok('Debrid Status', message)
        return
    
    if not debrid_client.is_available():
        message = "❌ No Debrid Services Configured\n\n"
        message += "Available premium services:\n\n"
        message += "• Real-Debrid (real-debrid.com)\n"
        message += "• Premiumize (premiumize.me)\n"
        message += "• All-Debrid (alldebrid.com)\n\n"
        message += "Benefits:\n"
        message += "• High-speed downloads\n"
        message += "• Premium file hosters\n"
        message += "• Better source quality\n\n"
        message += "Configure API keys in addon settings."
        xbmcgui.Dialog().ok('Debrid Status', message)
        return
    
    try:
        status = debrid_client.check_account_status()
        
        message = "💎 Debrid Services Status\n\n"
        
        for service_key, info in status.items():
            if info:
                service_name = info.get('service', service_key.title())
                message += f"{service_name}: ✅ Active\n"
                
                if 'username' in info:
                    message += f"User: {info['username']}\n"
                if 'premium' in info:
                    message += f"Premium: {'Yes' if info['premium'] else 'No'}\n"
                if 'expiration' in info and info['expiration'] != 'Unknown':
                    message += f"Expires: {info['expiration']}\n"
                
                message += "\n"
            else:
                message += f"{service_key.title()}: ❌ Error\n\n"
        
        message += "Debrid sources will be prioritized in search results."
        
    except Exception as e:
        message = f"💎 Debrid Services\n\n❌ Error checking status:\n{str(e)}"
    
    xbmcgui.Dialog().ok('Debrid Status', message)

def addon_stats():
    """Show comprehensive addon statistics"""
    try:
        # Get stats with error handling
        stats = {'watchlist_count': 0, 'favorites_count': 0, 'history_count': 0, 'resume_count': 0}
        if watchlist_manager:
            try:
                stats = watchlist_manager.get_stats()
            except:
                pass
        
        cocoscrapers_stats = {'available': False}
        if cocoscrapers_client:
            try:
                cocoscrapers_stats = cocoscrapers_client.get_scraper_stats()
            except:
                pass
        
        debrid_available = False
        if debrid_client:
            try:
                debrid_available = debrid_client.is_available()
            except:
                pass
        
        # Build message
        message = f"📊 MovieStream Pro Statistics\n\n"
        
        # Personal stats
        message += "Personal Library:\n"
        message += f"• Watchlist: {stats['watchlist_count']} items\n"
        message += f"• Favorites: {stats['favorites_count']} items\n"
        message += f"• History: {stats['history_count']} items\n"
        message += f"• Resume: {stats['resume_count']} items\n\n"
        
        # Service status
        message += "Services Status:\n"
        message += f"• TMDB: ✅ Enabled\n"
        message += f"• Cocoscrapers: {'✅ Available' if cocoscrapers_stats['available'] else '❌ Not Available'}\n"
        message += f"• Debrid: {'✅ Available' if debrid_available else '❌ Not Available'}\n\n"
        
        # Addon info
        message += f"Version: {addon.getAddonInfo('version')}\n"
        message += f"ID: {addon.getAddonInfo('id')}"
        
        xbmcgui.Dialog().ok('Addon Statistics', message)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error getting addon stats: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Addon Statistics', f'❌ Error getting statistics!\n\n{str(e)}')

def addon_info():
    """Show detailed addon information"""
    addon_version = addon.getAddonInfo('version')
    addon_name = addon.getAddonInfo('name')
    addon_author = addon.getAddonInfo('author')
    
    message = f"{addon_name} v{addon_version}\n"
    if addon_author:
        message += f"by {addon_author}\n"
    message += "\n"
    
    message += "🎬 Core Features:\n"
    message += "• TMDB movie/TV database\n"
    message += "• GitHub custom collections\n"
    message += "• Advanced search functionality\n"
    message += "• Multiple video formats\n\n"
    
    message += "🔧 Advanced Features:\n"
    message += "• Cocoscrapers integration\n"
    message += "• Premium debrid services\n"
    message += "• Watchlist & favorites\n"
    message += "• Resume playback points\n"
    message += "• M3U/M3U8 streaming\n"
    message += "• Subtitle support\n\n"
    
    message += "🛠️ Tools:\n"
    message += "• Connection testing\n"
    message += "• Service diagnostics\n"
    message += "• Cache management\n"
    message += "• Usage statistics"
    
    xbmcgui.Dialog().ok('Addon Information', message)

def clear_cache():
    """Clear all cache with confirmation"""
    if xbmcgui.Dialog().yesno('Clear Cache', 'Clear all cached data?', 'This will remove:', '• Watch history\n• Resume points\n• Cached metadata'):
        try:
            cleared_items = 0
            
            if watchlist_manager:
                try:
                    watchlist_manager.clear_history()
                    cleared_items += 1
                except:
                    pass
            
            message = f'✅ Cache cleared successfully!\n\n{cleared_items} cache types cleared.'
            xbmcgui.Dialog().notification('MovieStream', 'Cache cleared', xbmcgui.NOTIFICATION_INFO)
            xbmcgui.Dialog().ok('Cache Cleared', message)
            
        except Exception as e:
            xbmc.log(f"MovieStream: Cache clear error: {str(e)}", xbmc.LOGERROR)
            xbmcgui.Dialog().notification('MovieStream', f'Cache clear error: {str(e)}', xbmcgui.NOTIFICATION_ERROR)

def open_settings():
    """Open addon settings"""
    addon.openSettings()

# Simplified router with error handling
def router(paramstring):
    """Route to the appropriate function with error handling"""
    try:
        params = dict(urlparse.parse_qsl(paramstring))
        
        if params:
            action = params.get('action')
            xbmc.log(f"MovieStream: Routing action: {action}", xbmc.LOGDEBUG)
            
            # Main menus
            if action == 'movies_menu':
                movies_menu()
            elif action == 'tvshows_menu':
                tvshows_menu()
            elif action == 'search_menu':
                search_menu()
            elif action == 'my_lists':
                my_lists()
            elif action == 'github_collection':
                github_collection()
            elif action == 'tools_menu':
                tools_menu()
            
            # Movies
            elif action == 'tmdb_movies':
                list_tmdb_movies(params.get('category', 'popular'), int(params.get('page', 1)))
            elif action == 'play_movie':
                play_movie(params.get('movie_data', '{}'))
            elif action == 'search_movies':
                search_movies()
            elif action == 'search_tv_shows':
                search_tv_shows()
            
            # Tools
            elif action == 'test_tmdb':
                test_tmdb()
            elif action == 'test_github':
                test_github()
            elif action == 'cocoscrapers_status':
                cocoscrapers_status()
            elif action == 'debrid_status':
                debrid_status()
            elif action == 'addon_stats':
                addon_stats()
            elif action == 'addon_info':
                addon_info()
            elif action == 'clear_cache':
                clear_cache()
            elif action == 'settings':
                open_settings()
            
            else:
                xbmc.log(f"MovieStream: Unknown action: {action}", xbmc.LOGWARNING)
                list_categories()
        else:
            list_categories()
            
    except Exception as e:
        xbmc.log(f"MovieStream: Router error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', f'Navigation error: {str(e)}', xbmcgui.NOTIFICATION_ERROR)
        list_categories()  # Fallback to main menu

if __name__ == '__main__':
    try:
        router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
    except Exception as e:
        xbmc.log(f"MovieStream: Main execution error: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Addon startup error', xbmcgui.NOTIFICATION_ERROR)

def test_cocoscrapers_scraping():
    """Test Cocoscrapers with a known movie"""
    try:
        if not cocoscrapers_client or not cocoscrapers_client.is_available():
            xbmcgui.Dialog().ok('Cocoscrapers Test', '❌ Cocoscrapers not available!\n\nInstall script.module.cocoscrapers first.')
            return
        
        # Test with a popular movie
        test_movie = {
            'title': 'Avatar',
            'year': '2009',
            'tmdb_id': '19995',
            'imdb_id': 'tt0499549'
        }
        
        progress = xbmcgui.DialogProgress()
        progress.create('Testing Cocoscrapers', 'Testing with Avatar (2009)...')
        progress.update(0)
        
        sources = cocoscrapers_client.scrape_movie_sources(
            title=test_movie['title'],
            year=test_movie['year'],
            tmdb_id=test_movie['tmdb_id'],
            imdb_id=test_movie['imdb_id']
        )
        
        progress.close()
        
        if sources:
            message = f"✅ Cocoscrapers Working!\n\n"
            message += f"Test Movie: {test_movie['title']} ({test_movie['year']})\n"
            message += f"Sources Found: {len(sources)}\n\n"
            message += "Sample sources:\n"
            for i, source in enumerate(sources[:3]):
                message += f"• {source.get('provider', 'Unknown')} ({source.get('quality', 'Unknown')})\n"
        else:
            message = f"⚠️ Cocoscrapers Loaded but No Sources\n\n"
            message += f"Test Movie: {test_movie['title']} ({test_movie['year']})\n"
            message += "This could be due to:\n"
            message += "• No active scrapers\n"
            message += "• Network issues\n"
            message += "• Regional restrictions\n\n"
            message += "Try different content or check scraper settings."
        
        xbmcgui.Dialog().ok('Cocoscrapers Test Results', message)
        
    except Exception as e:
        xbmcgui.Dialog().ok('Cocoscrapers Test Error', f'❌ Test failed!\n\n{str(e)}')

# Add to tools_menu:
def tools_menu():
    """Tools submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '⚙️ Tools')
    
    menu_items = [
        ('🔍 Test TMDB Connection', 'test_tmdb', ''),
        ('📁 Test GitHub Connection', 'test_github', ''),
        ('🎬 Cocoscrapers Status', 'cocoscrapers_status', ''),
        ('🧪 Test Cocoscrapers Scraping', 'test_cocoscrapers_scraping', ''),  # NEW
        ('💎 Debrid Account Status', 'debrid_status', ''),
        ('📊 Addon Statistics', 'addon_stats', ''),
        ('🗑️ Clear All Cache', 'clear_cache', ''),
        ('ℹ️ Addon Information', 'addon_info', '')
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultAddonProgram.png'})
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

# Add to router:
elif action == 'test_cocoscrapers_scraping':
    test_cocoscrapers_scraping()
