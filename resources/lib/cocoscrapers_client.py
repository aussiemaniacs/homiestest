#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cocoscrapers Integration for MovieStream Kodi Addon
Handles movie/TV show source scraping and playback
"""

import xbmc
import xbmcaddon
import xbmcgui
import json
import threading
import time

class CocoScrapersClient:
    """Client for Cocoscrapers integration"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.cocoscrapers_available = False
        self.sources = []
        
        # Check if cocoscrapers is available
        try:
            import cocoscrapers
            self.cocoscrapers_available = True
            self.cocoscrapers = cocoscrapers
            xbmc.log("MovieStream: Cocoscrapers module loaded successfully", xbmc.LOGINFO)
        except ImportError:
            xbmc.log("MovieStream: Cocoscrapers module not found", xbmc.LOGWARNING)
    
    def is_available(self):
        """Check if cocoscrapers is available"""
        return self.cocoscrapers_available
    
    def scrape_movie_sources(self, title, year, imdb_id=None, tmdb_id=None):
        """Scrape sources for a movie"""
        if not self.cocoscrapers_available:
            return []
        
        try:
            # Prepare movie data for cocoscrapers
            movie_data = {
                'title': title,
                'year': int(year) if year else None,
                'imdb': imdb_id,
                'tmdb': tmdb_id
            }
            
            xbmc.log(f"MovieStream: Scraping sources for movie: {title} ({year})", xbmc.LOGINFO)
            
            # Start scraping with progress dialog
            sources = self._scrape_with_progress(movie_data, 'movie')
            
            # Filter and sort sources
            filtered_sources = self._filter_sources(sources)
            
            xbmc.log(f"MovieStream: Found {len(filtered_sources)} sources for {title}", xbmc.LOGINFO)
            return filtered_sources
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error scraping movie sources: {str(e)}", xbmc.LOGERROR)
            return []
    
    def scrape_episode_sources(self, title, year, season, episode, imdb_id=None, tmdb_id=None, tvdb_id=None):
        """Scrape sources for a TV episode"""
        if not self.cocoscrapers_available:
            return []
        
        try:
            # Prepare episode data for cocoscrapers
            episode_data = {
                'tvshowtitle': title,
                'year': int(year) if year else None,
                'season': int(season),
                'episode': int(episode),
                'imdb': imdb_id,
                'tmdb': tmdb_id,
                'tvdb': tvdb_id
            }
            
            xbmc.log(f"MovieStream: Scraping sources for episode: {title} S{season}E{episode}", xbmc.LOGINFO)
            
            # Start scraping with progress dialog
            sources = self._scrape_with_progress(episode_data, 'episode')
            
            # Filter and sort sources
            filtered_sources = self._filter_sources(sources)
            
            xbmc.log(f"MovieStream: Found {len(filtered_sources)} sources for {title} S{season}E{episode}", xbmc.LOGINFO)
            return filtered_sources
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error scraping episode sources: {str(e)}", xbmc.LOGERROR)
            return []
    
    def _scrape_with_progress(self, data, content_type):
        """Scrape sources with progress dialog"""
        

