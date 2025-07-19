#!/usr/bin/env python
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

# Import our enhanced modules
try:
    from resources.lib.cocoscrapers_client import CocoScrapersClient
    from resources.lib.debrid_client import DebridClient
    from resources.lib.tvshow_client import TVShowClient
    from resources.lib.watchlist_manager import WatchlistManager
except ImportError as e:
    xbmc.log(f"MovieStream: Import error: {str(e)}", xbmc.LOGERROR)

# Get addon info
addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
plugin_handle = int(sys.argv[1])
base_url = sys.argv[0]

# Initialize clients
try:
    cocoscrapers_client = CocoScrapersClient()
    debrid_client = DebridClient()
    tvshow_client = TVShowClient()
    watchlist_manager = WatchlistManager()
except Exception as e:
    xbmc.log(f"MovieStream: Client initialization error: {str(e)}", xbmc.LOGERROR)
    # Initialize with basic functionality
    cocoscrapers_client = None
    debrid_client = None
    tvshow_client = None
    watchlist_manager = None

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
        ('Movie Genres', 'movie_genres', ''),
        ('Search Movies', 'search_movies', '')
    ]
    
    for name, action, category in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultMovies.png'})
        
        url = get_url(action=action, category=category)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def search_menu():
    """Search submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '🔍 Search')
    
    menu_items = [
        ('Search Movies', 'search_movies', ''),
        ('Search TV Shows', 'search_tv_shows', ''),
        ('Search All', 'search_all', '')
    ]
    
    for name, action, param in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultSearch.png'})
        
        url = get_url(action=action)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

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
        response = requests.get(endpoints.get(category, endpoints['popular']), timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        xbmc.log(f"MovieStream: Error getting TMDB movies: {str(e)}", xbmc.LOGERROR)
        return None

def list_tmdb_movies(category='popular', page=1):
    """List movies from TMDB"""
    category_names = {
        'popular': 'Popular Movies',
        'top_rated': 'Top Rated Movies',
        'now_playing': 'Now Playing',
        'upcoming': 'Upcoming Movies'
    }
    
    xbmcplugin.setPluginCategory(plugin_handle, category_names.get(category, 'Movies'))
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    movies_data = get_tmdb_movies(category, page)
    if movies_data:
        for movie in movies_data.get('results', []):
            add_movie_item(movie, from_tmdb=True)
        
        if page < movies_data.get('total_pages', 1):
            list_item = xbmcgui.ListItem(label='➡️ Next Page >>')
            list_item.setArt({'thumb': 'DefaultFolder.png'})
            url = get_url(action='tmdb_movies', category=category, page=page + 1)
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def add_movie_item(movie, from_tmdb=False):
    """Add a movie item to the directory"""
    title = movie.get('title', 'Unknown Title')
    year = movie.get('release_date', '')[:4] if movie.get('release_date') else movie.get('year', '')
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
        'year': int(year) if str(year).isdigit() else 0,
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
        'tmdb_id': movie.get('id', movie.get('tmdb_id', '')),
        'imdb_id': movie.get('imdb_id', ''),
        'type': 'movie',
        'poster_url': movie.get('poster_url', ''),
        'plot': plot
    }
    
    # Add context menu items
    if addon.getSettingBool('enable_context_menus') and watchlist_manager:
        context_items = watchlist_manager.get_context_menu_items(movie_data)
        
        if cocoscrapers_client and cocoscrapers_client.is_available():
            context_items.append((
                'Select Source',
                f'RunPlugin({get_url(action="select_movie_source", movie_data=json.dumps(movie_data))})'
            ))
        
        list_item.addContextMenuItems(context_items)
    
    url = get_url(action='play_movie', movie_data=json.dumps(movie_data))
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)

def tvshows_menu():
    """TV shows submenu"""
    xbmcplugin.setPluginCategory(plugin_handle, '📺 TV Shows')
    
    menu_items = [
        ('Popular TV Shows', 'list_tv_shows', 'popular'),
        ('Top Rated TV Shows', 'list_tv_shows', 'top_rated'),
        ('Airing Today', 'list_tv_shows', 'airing_today'),
        ('TV Show Genres', 'tv_genres', ''),
        ('Search TV Shows', 'search_tv_shows', '')
    ]
    
    for name, action, category in menu_items:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': 'DefaultTVShows.png'})
        
        url = get_url(action=action, category=category)
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def list_tv_shows(category='popular', page=1):
    """List TV shows"""
    if not tvshow_client:
        xbmcgui.Dialog().notification('MovieStream', 'TV Show client not available', xbmcgui.NOTIFICATION_ERROR)
        return
    
    category_names = {
        'popular': 'Popular TV Shows',
        'top_rated': 'Top Rated TV Shows',
        'airing_today': 'Airing Today'
    }
    
    xbmcplugin.setPluginCategory(plugin_handle, category_names.get(category, 'TV Shows'))
    xbmcplugin.setContent(plugin_handle, 'tvshows')
    
    if category == 'popular':
        shows_data = tvshow_client.get_popular_shows(page)
    elif category == 'top_rated':
        shows_data = tvshow_client.get_top_rated_shows(page)
    elif category == 'airing_today':
        shows_data = tvshow_client.get_airing_today(page)
    else:
        shows_data = tvshow_client.get_popular_shows(page)
    
    if shows_data:
        for show in shows_data.get('results', []):
            add_tv_show_item(show)
        
        if page < shows_data.get('total_pages', 1):
            list_item = xbmcgui.ListItem(label='➡️ Next Page >>')
            list_item.setArt({'thumb': 'DefaultFolder.png'})
            url = get_url(action='list_tv_shows', category=category, page=page + 1)
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def add_tv_show_item(show):
    """Add a TV show item to the directory"""
    title = show.get('name', 'Unknown Title')
    year = show.get('first_air_date', '')[:4] if show.get('first_air_date') else ''
    plot = show.get('overview', 'No description available')
    
    display_title = f"{title} ({year})" if year else title
    list_item = xbmcgui.ListItem(label=display_title)
    
    # Set artwork
    poster_path = show.get('poster_path')
    backdrop_path = show.get('backdrop_path')
    
    poster_url = ''
    if poster_path:
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        list_item.setArt({'thumb': poster_url, 'poster': poster_url})
    
    if backdrop_path:
        fanart_url = f"https://image.tmdb.org/t/p/w1280{backdrop_path}"
        list_item.setArt({'fanart': fanart_url})
    
    list_item.setInfo('video', {
        'title': title,
        'plot': plot,
        'year': int(year) if year.isdigit() else 0,
        'rating': float(show.get('vote_average', 0)),
        'votes': str(show.get('vote_count', 0)),
        'mediatype': 'tvshow'
    })
    
    show_data = {
        'title': title,
        'year': str(year),
        'tmdb_id': show.get('id', ''),
        'type': 'tvshow',
        'poster_url': poster_url,
        'plot': plot
    }
    
    if addon.getSettingBool('enable_context_menus') and watchlist_manager:
        context_items = watchlist_manager.get_context_menu_items(show_data)
        list_item.addContextMenuItems(context_items)
    
    url = get_url(action='show_seasons', show_id=show.get('id'))
    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, True)

def show_seasons(show_id):
    """Show seasons for a TV show"""
    if not tvshow_client:
        return
    
    show_details = tvshow_client.get_show_details(show_id)
    
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

def show_episodes(show_id, season_number):
    """Show episodes for a season"""
    if not tvshow_client:
        return
    
    season_details = tvshow_client.get_season_details(show_id, season_number)
    
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
            
            if addon.getSettingBool('enable_context_menus') and watchlist_manager:
                context_items = watchlist_manager.get_context_menu_items(episode_data)
                list_item.addContextMenuItems(context_items)
            
            url = get_url(action='play_episode', episode_data=json.dumps(episode_data))
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
        
        xbmcplugin.endOfDirectory(plugin_handle)

def my_lists():
    """My Lists submenu"""
    if not watchlist_manager:
        xbmcgui.Dialog().notification('MovieStream', 'Watchlist manager not available', xbmcgui.NOTIFICATION_ERROR)
        return
    
    xbmcplugin.setPluginCategory(plugin_handle, '⭐ My Lists')
    
    stats = watchlist_manager.get_stats()
    
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

def list_watchlist():
    """List watchlist items"""
    if not watchlist_manager:
        return
    
    xbmcplugin.setPluginCategory(plugin_handle, '📋 Watchlist')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    watchlist_items = watchlist_manager.get_watchlist()
    
    for item in watchlist_items:
        list_item = xbmcgui.ListItem(label=item.get('title', 'Unknown'))
        
        if item.get('poster_url'):
            list_item.setArt({'thumb': item['poster_url']})
        
        list_item.setInfo('video', {
            'title': item.get('title', ''),
            'plot': item.get('plot', ''),
            'year': item.get('year', 0),
            'mediatype': item.get('type', 'video')
        })
        
        list_item.setProperty('IsPlayable', 'true')
        
        if item.get('type') == 'movie':
            url = get_url(action='play_movie', movie_data=json.dumps(item))
        else:
            url = get_url(action='play_episode', episode_data=json.dumps(item))
        
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def github_collection():
    """Show GitHub collection"""
    xbmcplugin.setPluginCategory(plugin_handle, '📁 GitHub Collection')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    try:
        github_url = addon.getSetting('github_repo_url') or 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
        movies_url = github_url + 'movies.json'
        
        response = requests.get(movies_url, timeout=10)
        response.raise_for_status()
        movies = response.json()
        
        for movie in movies:
            add_movie_item(movie, from_tmdb=False)
    
    except Exception as e:
        xbmc.log(f"MovieStream: Error loading GitHub collection: {str(e)}", xbmc.LOGERROR)
        
        list_item = xbmcgui.ListItem(label='❌ Error loading GitHub collection')
        list_item.setInfo('video', {'title': 'Error', 'plot': 'Check GitHub repository URL in settings'})
        xbmcplugin.addDirectoryItem(plugin_handle, '', list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

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
                
                for movie in results.get('results', [])[:20]:
                    add_movie_item(movie, from_tmdb=True)
                
                xbmcplugin.endOfDirectory(plugin_handle)
                
            except Exception as e:
                xbmc.log(f"MovieStream: Search error: {str(e)}", xbmc.LOGERROR)
                xbmcgui.Dialog().notification('MovieStream', 'Search failed', xbmcgui.NOTIFICATION_ERROR)

def search_tv_shows():
    """Search for TV shows"""
    keyboard = xbmc.Keyboard('', 'Search TV Shows')
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if query and tvshow_client:
            try:
                results = tvshow_client.search_shows(query)
                
                xbmcplugin.setPluginCategory(plugin_handle, f'Search: {query}')
                xbmcplugin.setContent(plugin_handle, 'tvshows')
                
                for show in results.get('results', [])[:20]:
                    add_tv_show_item(show)
                
                xbmcplugin.endOfDirectory(plugin_handle)
                
            except Exception as e:
                xbmc.log(f"MovieStream: TV search error: {str(e)}", xbmc.LOGERROR)
                xbmcgui.Dialog().notification('MovieStream', 'Search failed', xbmcgui.NOTIFICATION_ERROR)

def play_movie(movie_data_str):
    """Play a movie with proper cocoscrapers integration"""
    try:
        movie_data = json.loads(movie_data_str)
        
        # Check for resume point
        resume_point = None
        if watchlist_manager:
            resume_point = watchlist_manager.get_resume_point(movie_data)
            if resume_point:
                choice = xbmcgui.Dialog().yesno(
                    'Resume Playback',
                    f"Resume from {int(resume_point['percentage'])}%?",
                    'Start Over', 'Resume'
                )
                if not choice:  # Start over
                    watchlist_manager.remove_resume_point(movie_data)
        
        # Get enhanced TMDB info if available
        tmdb_id = movie_data.get('tmdb_id')
        imdb_id = movie_data.get('imdb_id')
        
        if tmdb_id:
            try:
                movie_details = get_enhanced_tmdb_details(tmdb_id, 'movie')
                if movie_details:
                    movie_data.update(movie_details)
                    imdb_id = movie_details.get('imdb_id') or imdb_id
            except Exception as e:
                xbmc.log(f"MovieStream: Error getting enhanced TMDB details: {str(e)}", xbmc.LOGERROR)
        
        # Try Cocoscrapers with enhanced data
        sources_found = False
        if cocoscrapers_client and cocoscrapers_client.is_available() and addon.getSettingBool('enable_cocoscrapers'):
            xbmc.log(f"MovieStream: Attempting to scrape sources for {movie_data['title']}", xbmc.LOGINFO)
            
            sources = cocoscrapers_client.scrape_movie_sources(
                title=movie_data['title'],
                year=movie_data.get('year', ''),
                tmdb_id=tmdb_id,
                imdb_id=imdb_id
            )
            
            if debrid_client and debrid_client.is_available():
                sources = debrid_client.filter_debrid_sources(sources)
            
            if sources:
                sources_found = True
                xbmc.log(f"MovieStream: Found {len(sources)} sources", xbmc.LOGINFO)
                
                selected_source = None
                if addon.getSettingBool('auto_play_best_source') and len(sources) > 0:
                    selected_source = sources[0]
                    xbmc.log(f"MovieStream: Auto-playing best source: {selected_source.get('provider', 'Unknown')}", xbmc.LOGINFO)
                else:
                    selected_source = cocoscrapers_client.show_source_selection(sources, movie_data['title'])
                
                if selected_source:
                    resolved_url = cocoscrapers_client.resolve_source(selected_source)
                    
                    if resolved_url:
                        xbmc.log(f"MovieStream: Playing resolved URL for {movie_data['title']}", xbmc.LOGINFO)
                        play_resolved_url(resolved_url, movie_data, resume_point)
                        return
                    else:
                        xbmc.log(f"MovieStream: Failed to resolve source for {movie_data['title']}", xbmc.LOGERROR)
        
        # If cocoscrapers failed or no sources found
        if not sources_found:
            xbmc.log(f"MovieStream: No sources found via cocoscrapers for {movie_data['title']}", xbmc.LOGWARNING)
            
            # Try direct video URL from movie data
            video_url = movie_data.get('video_url')
            if video_url:
                xbmc.log(f"MovieStream: Using direct video URL for {movie_data['title']}", xbmc.LOGINFO)
                play_resolved_url(video_url, movie_data, resume_point)
                return
            
            # Last resort: notify user
            xbmcgui.Dialog().notification(
                'MovieStream', 
                f'No sources found for {movie_data["title"]}', 
                xbmcgui.NOTIFICATION_WARNING,
                5000
            )
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing movie: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Playback error occurred', xbmcgui.NOTIFICATION_ERROR)

def play_episode(episode_data_str):
    """Play a TV episode with proper cocoscrapers integration"""
    try:
        episode_data = json.loads(episode_data_str)
        
        resume_point = None
        if watchlist_manager:
            resume_point = watchlist_manager.get_resume_point(episode_data)
            if resume_point:
                choice = xbmcgui.Dialog().yesno(
                    'Resume Playback',
                    f"Resume from {int(resume_point['percentage'])}%?",
                    'Start Over', 'Resume'
                )
                if not choice:
                    watchlist_manager.remove_resume_point(episode_data)
        
        show_tmdb_id = episode_data.get('show_tmdb_id')
        
        sources_found = False
        if cocoscrapers_client and cocoscrapers_client.is_available() and addon.getSettingBool('enable_cocoscrapers') and tvshow_client:
            xbmc.log(f"MovieStream: Attempting to scrape episode sources for {episode_data.get('show_title', '')} S{episode_data.get('season')}E{episode_data.get('episode')}", xbmc.LOGINFO)
            
            sources = tvshow_client.scrape_episode_sources(
                show_title=episode_data.get('show_title', ''),
                year=episode_data.get('year', ''),
                season=episode_data.get('season'),
                episode=episode_data.get('episode'),
                show_id=show_tmdb_id
            )
            
            if debrid_client and debrid_client.is_available():
                sources = debrid_client.filter_debrid_sources(sources)
            
            if sources:
                sources_found = True
                xbmc.log(f"MovieStream: Found {len(sources)} episode sources", xbmc.LOGINFO)
                
                selected_source = None
                if addon.getSettingBool('auto_play_best_source') and len(sources) > 0:
                    selected_source = sources[0]
                else:
                    episode_title = f"{episode_data.get('show_title', '')} S{episode_data.get('season')}E{episode_data.get('episode')}"
                    selected_source = cocoscrapers_client.show_source_selection(sources, episode_title)
                
                if selected_source:
                    resolved_url = cocoscrapers_client.resolve_source(selected_source)
                    
                    if resolved_url:
                        play_resolved_url(resolved_url, episode_data, resume_point)
                        return
        
        if not sources_found:
            video_url = episode_data.get('video_url')
            if video_url:
                play_resolved_url(video_url, episode_data, resume_point)
                return
            
            episode_title = f"{episode_data.get('show_title', 'Unknown')} S{episode_data.get('season')}E{episode_data.get('episode')}"
            xbmcgui.Dialog().notification(
                'MovieStream', 
                f'No sources found for {episode_title}', 
                xbmcgui.NOTIFICATION_WARNING,
                5000
            )
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing episode: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Playback error occurred', xbmcgui.NOTIFICATION_ERROR)

def play_resolved_url(url, item_data, resume_point=None):
    """Play a resolved URL with metadata"""
    try:
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
        
        # Set resume point
        if resume_point:
            list_item.setProperty('ResumeTime', str(resume_point['position']))
            list_item.setProperty('TotalTime', str(resume_point['total_time']))
        
        # Handle different stream types
        if url.lower().endswith('.m3u8') or 'manifest.m3u8' in url.lower():
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            list_item.setMimeType('application/vnd.apple.mpegurl')
        
        # Add to history
        if watchlist_manager:
            watchlist_manager.add_to_history(item_data)
        
        xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing resolved URL: {str(e)}", xbmc.LOGERROR)

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

def test_tmdb():
    """Test TMDB connection"""
    try:
        api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
        url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page=1'
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result and 'results' in result:
            message = f"✅ TMDB Connection Successful!\n\nFound {len(result['results'])} popular movies.\nTotal pages: {result.get('total_pages', 0)}"
            xbmcgui.Dialog().ok('TMDB Test', message)
        else:
            xbmcgui.Dialog().ok('TMDB Test', '❌ TMDB Connection Failed!\n\nNo results returned from API.')
    
    except Exception as e:
        xbmcgui.Dialog().ok('TMDB Test', f'❌ TMDB Connection Error!\n\n{str(e)}')

def test_github():
    """Test GitHub connection"""
    try:
        github_url = addon.getSetting('github_repo_url') or 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
        movies_url = github_url + 'movies.json'
        
        response = requests.get(movies_url, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result:
            message = f"✅ GitHub Connection Successful!\n\nFound {len(result)} movies in collection."
            xbmcgui.Dialog().ok('GitHub Test', message)
        else:
            message = "⚠️ GitHub Connection Warning!\n\nConnected but no movies found.\nCheck your repository URL and JSON files."
            xbmcgui.Dialog().ok('GitHub Test', message)
    
    except Exception as e:
        xbmcgui.Dialog().ok('GitHub Test', f'❌ GitHub Connection Error!\n\n{str(e)}')

def cocoscrapers_status():
    """Show Cocoscrapers status"""
    if not cocoscrapers_client:
        message = "❌ Cocoscrapers Client Error\n\nCocoscrapers client failed to initialize."
        xbmcgui.Dialog().ok('Cocoscrapers Status', message)
        return
    
    stats = cocoscrapers_client.get_scraper_stats()
    
    if stats['available']:
        message = f"✅ Cocoscrapers Available\n\n"
        message += f"Total Scrapers: {stats.get('total_scrapers', 0)}\n"
        message += f"Enabled Scrapers: {stats.get('enabled_scrapers', 0)}\n\n"
        message += "Cocoscrapers will be used to find streaming sources."
    else:
        message = "❌ Cocoscrapers Not Available\n\n"
        message += "To use Cocoscrapers:\n"
        message += "1. Install 'script.module.cocoscrapers' addon\n"
        message += "2. Restart MovieStream addon\n\n"
        message += "Without Cocoscrapers, only direct links will play."
    
    xbmcgui.Dialog().ok('Cocoscrapers Status', message)

def debrid_status():
    """Show debrid services status"""
    if not debrid_client or not debrid_client.is_available():
        message = "❌ No Debrid Services Configured\n\n"
        message += "Available services:\n"
        message += "• Real-Debrid\n"
        message += "• Premiumize\n"
        message += "• All-Debrid\n\n"
        message += "Configure API keys in Settings."
        xbmcgui.Dialog().ok('Debrid Status', message)
        return
    
    status = debrid_client.check_account_status()
    
    message = "💎 Debrid Services Status\n\n"
    
    for service, info in status.items():
        if info:
            message += f"{info['service']}: ✅ Active\n"
            message += f"User: {info.get('username', 'N/A')}\n"
            message += f"Premium: {'Yes' if info.get('premium', False) else 'No'}\n\n"
        else:
            message += f"{service}: ❌ Error\n\n"
    
    xbmcgui.Dialog().ok('Debrid Status', message)

def addon_stats():
    """Show addon statistics"""
    stats = {'watchlist_count': 0, 'favorites_count': 0, 'history_count': 0, 'resume_count': 0}
    cocoscrapers_stats = {'available': False}
    debrid_available = False
    
    if watchlist_manager:
        stats = watchlist_manager.get_stats()
    if cocoscrapers_client:
        cocoscrapers_stats = cocoscrapers_client.get_scraper_stats()
    if debrid_client:
        debrid_available = debrid_client.is_available()
    
    message = f"📊 MovieStream Pro Statistics\n\n"
    message += f"Watchlist: {stats['watchlist_count']} items\n"
    message += f"Favorites: {stats['favorites_count']} items\n"
    message += f"History: {stats['history_count']} items\n"
    message += f"Resume Points: {stats['resume_count']} items\n\n"
    message += f"Cocoscrapers: {'✅ Available' if cocoscrapers_stats['available'] else '❌ Not Available'}\n"
    message += f"Debrid Services: {'✅ Available' if debrid_available else '❌ Not Available'}\n\n"
    message += f"Version: {addon.getAddonInfo('version')}"
    
    xbmcgui.Dialog().ok('Addon Statistics', message)

def addon_info():
    """Show addon information"""
    addon_version = addon.getAddonInfo('version')
    addon_name = addon.getAddonInfo('name')
    
    message = f"{addon_name} v{addon_version}\n\n"
    message += "Features:\n"
    message += "• TMDB Integration\n"
    message += "• GitHub Database\n"
    message += "• Cocoscrapers Support\n"
    message += "• Debrid Services\n"
    message += "• TV Shows & Episodes\n"
    message += "• Watchlist & Favorites\n"
    message += "• Resume Points\n"
    message += "• M3U/M3U8 Support\n"
    message += "• Advanced Search"
    
    xbmcgui.Dialog().ok('Addon Information', message)

def clear_cache():
    """Clear all cache"""
    try:
        if watchlist_manager:
            watchlist_manager.clear_history()
        
        xbmcgui.Dialog().notification('MovieStream', 'Cache cleared successfully', xbmcgui.NOTIFICATION_INFO)
    except Exception as e:
        xbmcgui.Dialog().notification('MovieStream', f'Cache clear error: {str(e)}', xbmcgui.NOTIFICATION_ERROR)

def add_to_watchlist(item_data_str):
    """Add item to watchlist"""
    if not watchlist_manager:
        return
    
    try:
        item_data = json.loads(item_data_str)
        success = watchlist_manager.add_to_watchlist(item_data)
        
        if success:
            xbmcgui.Dialog().notification('MovieStream', f'Added to Watchlist: {item_data.get("title", "Item")}', xbmcgui.NOTIFICATION_INFO)
        else:
            xbmcgui.Dialog().notification('MovieStream', 'Already in Watchlist', xbmcgui.NOTIFICATION_WARNING)
            
    except Exception as e:
        xbmc.log(f"MovieStream: Error adding to watchlist: {str(e)}", xbmc.LOGERROR)

def remove_from_watchlist(item_data_str):
    """Remove item from watchlist"""
    if not watchlist_manager:
        return
    
    try:
        item_data = json.loads(item_data_str)
        success = watchlist_manager.remove_from_watchlist(item_data)
        
        if success:
            xbmcgui.Dialog().notification('MovieStream', f'Removed from Watchlist: {item_data.get("title", "Item")}', xbmcgui.NOTIFICATION_INFO)
            
    except Exception as e:
        xbmc.log(f"MovieStream: Error removing from watchlist: {str(e)}", xbmc.LOGERROR)

def add_to_favorites(item_data_str):
    """Add item to favorites"""
    if not watchlist_manager:
        return
    
    try:
        item_data = json.loads(item_data_str)
        success = watchlist_manager.add_to_favorites(item_data)
        
        if success:
            xbmcgui.Dialog().notification('MovieStream', f'Added to Favorites: {item_data.get("title", "Item")}', xbmcgui.NOTIFICATION_INFO)
        else:
            xbmcgui.Dialog().notification('MovieStream', 'Already in Favorites', xbmcgui.NOTIFICATION_WARNING)
            
    except Exception as e:
        xbmc.log(f"MovieStream: Error adding to favorites: {str(e)}", xbmc.LOGERROR)

def open_settings():
    """Open addon settings"""
    addon.openSettings()

def router(paramstring):
    """Route to the appropriate function"""
    params = dict(urlparse.parse_qsl(paramstring))
    
    if params:
        action = params.get('action')
        
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
        
        # TV Shows
        elif action == 'list_tv_shows':
            list_tv_shows(params.get('category', 'popular'), int(params.get('page', 1)))
        elif action == 'show_seasons':
            show_seasons(params.get('show_id'))
        elif action == 'show_episodes':
            show_episodes(params.get('show_id'), params.get('season_number'))
        elif action == 'play_episode':
            play_episode(params.get('episode_data', '{}'))
        elif action == 'search_tv_shows':
            search_tv_shows()
        
        # Watchlist actions
        elif action == 'add_watchlist':
            add_to_watchlist(params.get('item_data', '{}'))
        elif action == 'remove_watchlist':
            remove_from_watchlist(params.get('item_data', '{}'))
        elif action == 'add_favorite':
            add_to_favorites(params.get('item_data', '{}'))
        elif action == 'list_watchlist':
            list_watchlist()
        
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
            list_categories()
    else:
        list_categories()

if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else '')
