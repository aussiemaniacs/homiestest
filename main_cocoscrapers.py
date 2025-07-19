#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import urllib.parse as urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import json

# Import our modules
from resources.lib.cocoscrapers_client import CocoScrapersClient

# Get addon info
addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
plugin_handle = int(sys.argv[1])
base_url = sys.argv[0]

# Initialize Cocoscrapers client
cocoscrapers_client = CocoScrapersClient()

def get_url(**kwargs):
    """Create a URL for calling the plugin"""
    return '{}?{}'.format(base_url, urlparse.urlencode(kwargs))

def list_categories():
    """Display main categories"""
    xbmcplugin.setPluginCategory(plugin_handle, 'MovieStream')
    xbmcplugin.setContent(plugin_handle, 'videos')
    
    categories = [
        ('Movies from TMDB', 'tmdb_movies', 'DefaultMovies.png'),
        ('GitHub Movies', 'github_movies', 'DefaultFolder.png'),
        ('Search Movies', 'search_movies', 'DefaultSearch.png'),
        ('Cocoscrapers Status', 'cocoscrapers_status', 'DefaultAddonProgram.png'),
        ('Settings', 'settings', 'DefaultAddonProgram.png')
    ]
    
    for name, action, icon in categories:
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'thumb': icon, 'icon': icon})
        url = get_url(action=action)
        is_folder = action not in ['settings', 'cocoscrapers_status']
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, is_folder)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def get_tmdb_movies():
    """Get movies from TMDB API"""
    api_key = addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}'
    
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return None

def list_tmdb_movies():
    """List popular movies from TMDB"""
    xbmcplugin.setPluginCategory(plugin_handle, 'TMDB Movies')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    movies_data = get_tmdb_movies()
    if movies_data:
        for movie in movies_data.get('results', [])[:20]:  # Increased to 20
            title = movie.get('title', 'Unknown Title')
            year = movie.get('release_date', '')[:4] if movie.get('release_date') else ''
            plot = movie.get('overview', 'No description available')
            
            list_item = xbmcgui.ListItem(label=f"{title} ({year})" if year else title)
            
            # Set poster
            poster_path = movie.get('poster_path')
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                list_item.setArt({'thumb': poster_url, 'poster': poster_url})
            
            list_item.setInfo('video', {
                'title': title,
                'plot': plot,
                'year': int(year) if year.isdigit() else 0,
                'mediatype': 'movie'
            })
            list_item.setProperty('IsPlayable', 'true')
            
            # Use cocoscrapers for TMDB movies
            url = get_url(
                action='play_movie_cocoscrapers',
                title=title,
                year=year,
                tmdb_id=movie.get('id'),
                imdb_id=''  # We don't have IMDB ID from TMDB popular endpoint
            )
            xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def get_github_movies():
    """Get movies from GitHub JSON"""
    github_url = addon.getSetting('github_repo_url') or 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
    movies_url = github_url + 'movies.json'
    
    try:
        response = requests.get(movies_url, timeout=10)
        return response.json()
    except:
        return []

def list_github_movies():
    """List movies from GitHub"""
    xbmcplugin.setPluginCategory(plugin_handle, 'GitHub Movies')
    xbmcplugin.setContent(plugin_handle, 'movies')
    
    movies = get_github_movies()
    for movie in movies:
        title = movie.get('title', 'Unknown')
        year = movie.get('year', '')
        
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
        
        # Add context menu for source selection
        context_menu = []
        
        # Option 1: Play with Cocoscrapers
        if cocoscrapers_client.is_available():
            context_menu.append((
                'Play with Cocoscrapers',
                f'RunPlugin({get_url(action="play_movie_cocoscrapers", title=title, year=str(year), tmdb_id=movie.get("tmdb_id", ""), imdb_id="")})'
            ))
        
        # Option 2: Play direct (if available)
        if movie.get('video_url'):
            context_menu.append((
                'Play Direct Link',
                f'RunPlugin({get_url(action="play_github", video_url=movie.get("video_url", ""))})'
            ))
        
        if context_menu:
            list_item.addContextMenuItems(context_menu)
        
        # Default action - prefer Cocoscrapers if available
        if cocoscrapers_client.is_available():
            url = get_url(
                action='play_movie_cocoscrapers',
                title=title,
                year=str(year),
                tmdb_id=movie.get('tmdb_id', ''),
                imdb_id=''
            )
        else:
            url = get_url(action='play_github', video_url=movie.get('video_url', ''))
        
        xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(plugin_handle)

def play_movie_cocoscrapers(title, year, tmdb_id='', imdb_id=''):
    """Play movie using Cocoscrapers"""
    if not cocoscrapers_client.is_available():
        xbmcgui.Dialog().notification('MovieStream', 'Cocoscrapers not available', xbmcgui.NOTIFICATION_ERROR)
        return
    
    try:
        # Scrape sources
        sources = cocoscrapers_client.scrape_movie_sources(
            title=title,
            year=year,
            tmdb_id=tmdb_id if tmdb_id else None,
            imdb_id=imdb_id if imdb_id else None
        )
        
        if not sources:
            # Fallback to sample video
            play_sample()
            return
        
        # Auto-play best source or show selection
        auto_play = addon.getSettingBool('auto_play_best_source')
        
        if auto_play and sources:
            selected_source = sources[0]  # Best source is first
        else:
            selected_source = cocoscrapers_client.show_source_selection(sources, title)
        
        if selected_source:
            # Resolve source
            resolved_url = cocoscrapers_client.resolve_source(selected_source)
            
            if resolved_url:
                # Play resolved URL
                list_item = xbmcgui.ListItem(label=title, path=resolved_url)
                list_item.setInfo('video', {
                    'title': title,
                    'year': int(year) if year.isdigit() else 0,
                    'mediatype': 'movie'
                })
                xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
            else:
                xbmcgui.Dialog().notification('MovieStream', 'Could not resolve source', xbmcgui.NOTIFICATION_ERROR)
                # Fallback to sample
                play_sample()
        
    except Exception as e:
        xbmc.log(f"MovieStream: Error playing movie with cocoscrapers: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MovieStream', 'Playback failed', xbmcgui.NOTIFICATION_ERROR)
        # Fallback to sample
        play_sample()

def play_sample():
    """Play sample video"""
    sample_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    list_item = xbmcgui.ListItem(path=sample_url)
    xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)

def play_github(video_url):
    """Play video from GitHub database"""
    if video_url:
        list_item = xbmcgui.ListItem(path=video_url)
        xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
    else:
        xbmcgui.Dialog().notification('MovieStream', 'No video URL found', xbmcgui.NOTIFICATION_ERROR)

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
                    title = movie.get('title', 'Unknown')
                    year = movie.get('release_date', '')[:4] if movie.get('release_date') else ''
                    
                    list_item = xbmcgui.ListItem(label=f"{title} ({year})" if year else title)
                    
                    poster_path = movie.get('poster_path')
                    if poster_path:
                        list_item.setArt({'thumb': f"https://image.tmdb.org/t/p/w500{poster_path}"})
                    
                    list_item.setInfo('video', {
                        'title': title,
                        'plot': movie.get('overview', ''),
                        'year': int(year) if year.isdigit() else 0,
                        'mediatype': 'movie'
                    })
                    list_item.setProperty('IsPlayable', 'true')
                    
                    # Use cocoscrapers for search results too
                    if cocoscrapers_client.is_available():
                        url = get_url(
                            action='play_movie_cocoscrapers',
                            title=title,
                            year=year,
                            tmdb_id=movie.get('id'),
                            imdb_id=''
                        )
                    else:
                        url = get_url(action='play_sample')
                    
                    xbmcplugin.addDirectoryItem(plugin_handle, url, list_item, False)
                
                xbmcplugin.endOfDirectory(plugin_handle)
            except:
                xbmcgui.Dialog().notification('MovieStream', 'Search failed', xbmcgui.NOTIFICATION_ERROR)

def cocoscrapers_status():
    """Show Cocoscrapers status and information"""
    stats = cocoscrapers_client.get_scraper_stats()
    
    if stats['available']:
        message = f"✅ Cocoscrapers Available\n\n"
        message += f"Total Scrapers: {stats.get('total_scrapers', 0)}\n"
        message += f"Enabled Scrapers: {stats.get('enabled_scrapers', 0)}\n\n"
        message += "Cocoscrapers will be used to find streaming sources for movies."
    else:
        message = "❌ Cocoscrapers Not Available\n\n"
        message += "To use Cocoscrapers:\n"
        message += "1. Install 'script.module.cocoscrapers' addon\n"
        message += "2. Restart MovieStream addon\n\n"
        message += "Without Cocoscrapers, only direct links and samples will play."
    
    xbmcgui.Dialog().ok('Cocoscrapers Status', message)

def open_settings():
    """Open addon settings"""
    addon.openSettings()

def router(paramstring):
    """Route to the appropriate function"""
    params = dict(urlparse.parse_qsl(paramstring))
    
    if params:
        action = params.get('action')
        
        if action == 'tmdb_movies':
            list_tmdb_movies()
        elif action == 'github_movies':
            list_github_movies()
        elif action == 'search_movies':
            search_movies()
        elif action == 'play_sample':
            play_sample()
        elif action == 'play_github':
            play_github(params.get('video_url'))
        elif action == 'play_movie_cocoscrapers':
            play_movie_cocoscrapers(
                title=params.get('title'),
                year=params.get('year'),
                tmdb_id=params.get('tmdb_id'),
                imdb_id=params.get('imdb_id')
            )
        elif action == 'cocoscrapers_status':
            cocoscrapers_status()
        elif action == 'settings':
            open_settings()
        else:
            list_categories()
    else:
        list_categories()

if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else '')