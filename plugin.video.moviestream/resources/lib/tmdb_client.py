#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import xbmc
import xbmcaddon
import json
from urllib.parse import urlencode

class TMDBClient:
    """Client for The Movie Database (TMDB) API"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.api_key = self.addon.getSetting('tmdb_api_key') or 'd0f489a129429db6f2dd4751e5dbeb82'
        self.base_url = 'https://api.themoviedb.org/3'
        self.session = requests.Session()
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': 'MovieStream Kodi Addon 1.0.0'
        })
    
    def _make_request(self, endpoint, params=None):
        """Make a request to the TMDB API"""
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            xbmc.log(f"MovieStream TMDB API Error: {str(e)}", xbmc.LOGERROR)
            return None
        except json.JSONDecodeError as e:
            xbmc.log(f"MovieStream TMDB JSON Error: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_popular_movies(self, page=1):
        """Get popular movies"""
        return self._make_request('movie/popular', {'page': page})
    
    def get_top_rated_movies(self, page=1):
        """Get top rated movies"""
        return self._make_request('movie/top_rated', {'page': page})
    
    def get_now_playing_movies(self, page=1):
        """Get now playing movies"""
        return self._make_request('movie/now_playing', {'page': page})
    
    def get_upcoming_movies(self, page=1):
        """Get upcoming movies"""
        return self._make_request('movie/upcoming', {'page': page})
    
    def get_movie_details(self, movie_id):
        """Get detailed information about a movie"""
        return self._make_request(f'movie/{movie_id}', {
            'append_to_response': 'credits,videos,images,similar,reviews'
        })
    
    def search_movies(self, query, page=1):
        """Search for movies"""
        return self._make_request('search/movie', {
            'query': query,
            'page': page
        })
    
    def get_popular_tv_shows(self, page=1):
        """Get popular TV shows"""
        return self._make_request('tv/popular', {'page': page})
    
    def get_top_rated_tv_shows(self, page=1):
        """Get top rated TV shows"""
        return self._make_request('tv/top_rated', {'page': page})
    
    def get_tv_show_details(self, show_id):
        """Get detailed information about a TV show"""
        return self._make_request(f'tv/{show_id}', {
            'append_to_response': 'credits,videos,images,similar,reviews'
        })
    
    def get_season_details(self, show_id, season_number):
        """Get detailed information about a TV season"""
        return self._make_request(f'tv/{show_id}/season/{season_number}', {
            'append_to_response': 'credits,videos,images'
        })
    
    def get_episode_details(self, show_id, season_number, episode_number):
        """Get detailed information about a TV episode"""
        return self._make_request(f'tv/{show_id}/season/{season_number}/episode/{episode_number}', {
            'append_to_response': 'credits,videos,images'
        })
    
    def search_tv_shows(self, query, page=1):
        """Search for TV shows"""
        return self._make_request('search/tv', {
            'query': query,
            'page': page
        })
    
    def get_person_details(self, person_id):
        """Get detailed information about a person"""
        return self._make_request(f'person/{person_id}', {
            'append_to_response': 'movie_credits,tv_credits,images'
        })
    
    def search_people(self, query, page=1):
        """Search for people"""
        return self._make_request('search/person', {
            'query': query,
            'page': page
        })
    
    def get_genres(self, media_type='movie'):
        """Get list of genres"""
        return self._make_request(f'genre/{media_type}/list')
    
    def discover_movies(self, **kwargs):
        """Discover movies with filters"""
        return self._make_request('discover/movie', kwargs)
    
    def discover_tv_shows(self, **kwargs):
        """Discover TV shows with filters"""
        return self._make_request('discover/tv', kwargs)
    
    def get_trending(self, media_type='all', time_window='day'):
        """Get trending content"""
        return self._make_request(f'trending/{media_type}/{time_window}')
    
    def get_configuration(self):
        """Get TMDB configuration"""
        return self._make_request('configuration')