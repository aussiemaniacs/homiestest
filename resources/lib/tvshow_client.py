#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TV Show Client for MovieStream Kodi Addon
Handles TV show metadata, seasons, episodes with Cocoscrapers integration
"""

import xbmc
import xbmcaddon
import requests
import json

class TVShowClient:
    """Client for TV show management"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.api_key = self.addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
        self.base_url = 'https://api.themoviedb.org/3'
        self.session = requests.Session()
        
        # Import cocoscrapers client
        try:
            from resources.lib.cocoscrapers_client import CocoScrapersClient
            self.cocoscrapers = CocoScrapersClient()
        except ImportError:
            self.cocoscrapers = None
            xbmc.log("MovieStream: Cocoscrapers client not available in TVShowClient", xbmc.LOGWARNING)
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': 'MovieStream Pro 2.0.0'
        })
    
    def get_popular_shows(self, page=1):
        """Get popular TV shows from TMDB"""
        try:
            url = f"{self.base_url}/tv/popular?api_key={self.api_key}&page={page}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            xbmc.log(f"MovieStream: Error getting popular shows: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_top_rated_shows(self, page=1):
        """Get top rated TV shows"""
        try:
            url = f"{self.base_url}/tv/top_rated?api_key={self.api_key}&page={page}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            xbmc.log(f"MovieStream: Error getting top rated shows: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_airing_today(self, page=1):
        """Get shows airing today"""
        try:
            url = f"{self.base_url}/tv/airing_today?api_key={self.api_key}&page={page}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            xbmc.log(f"MovieStream: Error getting airing today: {str(e)}", xbmc.LOGERROR)
            return None
    
    def search_shows(self, query, page=1):
        """Search TV shows"""
        try:
            url = f"{self.base_url}/search/tv?api_key={self.api_key}&query={query}&page={page}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            xbmc.log(f"MovieStream: Error searching shows: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_show_details(self, show_id):
        """Get detailed show information"""
        try:
            url = f"{self.base_url}/tv/{show_id}?api_key={self.api_key}&append_to_response=external_ids,credits,videos,similar"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            xbmc.log(f"MovieStream: Error getting show details: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_season_details(self, show_id, season_number):
        """Get season details with episodes"""
        try:
            url = f"{self.base_url}/tv/{show_id}/season/{season_number}?api_key={self.api_key}&append_to_response=credits,videos"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            xbmc.log(f"MovieStream: Error getting season details: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_episode_details(self, show_id, season_number, episode_number):
        """Get episode details"""
        try:
            url = f"{self.base_url}/tv/{show_id}/season/{season_number}/episode/{episode_number}?api_key={self.api_key}&append_to_response=credits,videos"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            xbmc.log(f"MovieStream: Error getting episode details: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_show_external_ids(self, show_id):
        """Get external IDs (IMDB, TVDB, etc.)"""
        try:
            url = f"{self.base_url}/tv/{show_id}/external_ids?api_key={self.api_key}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            xbmc.log(f"MovieStream: Error getting external IDs: {str(e)}", xbmc.LOGERROR)
            return None
    
    def scrape_episode_sources(self, show_title, year, season, episode, show_id=None):
        """Scrape episode sources using Cocoscrapers"""
        if not self.cocoscrapers or not self.cocoscrapers.is_available():
            xbmc.log("MovieStream: Cocoscrapers not available for episode scraping", xbmc.LOGWARNING)
            return []
        
        try:
            # Get external IDs for better scraping
            external_ids = {}
            if show_id:
                external_ids = self.get_show_external_ids(show_id) or {}
            
            # Scrape sources
            sources = self.cocoscrapers.scrape_episode_sources(
                title=show_title,
                year=year,
                season=season,
                episode=episode,
                imdb_id=external_ids.get('imdb_id'),
                tmdb_id=show_id,
                tvdb_id=external_ids.get('tvdb_id')
            )
            
            return sources
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error scraping episode sources: {str(e)}", xbmc.LOGERROR)
            return []
    
    def get_next_episode(self, show_id, current_season, current_episode):
        """Get next episode information"""
        try:
            # First try next episode in current season
            next_episode = current_episode + 1
            episode_details = self.get_episode_details(show_id, current_season, next_episode)
            
            if episode_details:
                return {
                    'season': current_season,
                    'episode': next_episode,
                    'details': episode_details
                }
            
            # If no next episode, try first episode of next season
            next_season = current_season + 1
            episode_details = self.get_episode_details(show_id, next_season, 1)
            
            if episode_details:
                return {
                    'season': next_season,
                    'episode': 1,
                    'details': episode_details
                }
            
            return None
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error getting next episode: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_github_shows(self):
        """Get TV shows from GitHub JSON"""
        try:
            github_url = self.addon.getSetting('github_repo_url') or 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
            shows_url = github_url + 'tvshows.json'
            
            response = self.session.get(shows_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            xbmc.log(f"MovieStream: Error getting GitHub shows: {str(e)}", xbmc.LOGERROR)
            return []
    
    def get_show_genres(self):
        """Get TV show genres"""
        try:
            url = f"{self.base_url}/genre/tv/list?api_key={self.api_key}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            xbmc.log(f"MovieStream: Error getting show genres: {str(e)}", xbmc.LOGERROR)
            return None
    
    def discover_shows(self, **kwargs):
        """Discover TV shows with filters"""
        try:
            params = {'api_key': self.api_key}
            params.update(kwargs)
            
            url = f"{self.base_url}/discover/tv"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            xbmc.log(f"MovieStream: Error discovering shows: {str(e)}", xbmc.LOGERROR)
            return None
