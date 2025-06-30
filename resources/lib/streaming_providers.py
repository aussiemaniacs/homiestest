#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Streaming Providers for MovieStream Kodi Addon
Handles multiple video streaming sources
"""

import xbmc
import xbmcaddon
import requests
import json
import re
from urllib.parse import quote, urlencode

class StreamingProviders:
    """Manager for multiple streaming providers"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.session = requests.Session()
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': 'MovieStream Kodi Addon 1.0.0'
        })
        
        # Initialize providers
        self.providers = {
            'direct': DirectVideoProvider(self.session),
            'youtube': YouTubeProvider(self.session),
            'vimeo': VimeoProvider(self.session),
            'dailymotion': DailymotionProvider(self.session),
            'custom': CustomProvider(self.session)
        }
    
    def get_video_url(self, movie_details, provider_preference=None):
        """Get video URL from available providers"""
        
        # Try provider preference first
        if provider_preference and provider_preference in self.providers:
            url = self.providers[provider_preference].get_video_url(movie_details)
            if url:
                return url
        
        # Try all providers in order of preference
        provider_order = ['direct', 'youtube', 'vimeo', 'dailymotion', 'custom']
        
        for provider_name in provider_order:
            if provider_name in self.providers:
                try:
                    url = self.providers[provider_name].get_video_url(movie_details)
                    if url:
                        xbmc.log(f"MovieStream: Found video URL via {provider_name}", xbmc.LOGINFO)
                        return url
                except Exception as e:
                    xbmc.log(f"MovieStream Provider Error ({provider_name}): {str(e)}", xbmc.LOGERROR)
        
        return None
    
    def get_available_providers(self):
        """Get list of available streaming providers"""
        return list(self.providers.keys())
    
    def get_provider_info(self, provider_name):
        """Get information about a specific provider"""
        if provider_name in self.providers:
            return self.providers[provider_name].get_info()
        return None

class BaseProvider:
    """Base class for streaming providers"""
    
    def __init__(self, session):
        self.session = session
    
    def get_video_url(self, movie_details):
        """Get video URL for movie (to be implemented by subclasses)"""
        raise NotImplementedError
    
    def get_info(self):
        """Get provider information"""
        return {
            'name': self.__class__.__name__,
            'description': 'Base streaming provider'
        }

class DirectVideoProvider(BaseProvider):
    """Provider for direct video file URLs"""
    
    def get_video_url(self, movie_details):
        """Get direct video URL"""
        
        # Check if movie has direct video URL
        if 'video_url' in movie_details:
            url = movie_details['video_url']
            
            # Validate URL
            if self._is_valid_video_url(url):
                return url
        
        # Try to construct URL from title and year
        title = movie_details.get('title', '')
        year = movie_details.get('year', '')
        
        if title:
            # This is where you would implement your video source logic
            # For example, searching your own video server or CDN
            return self._search_video_server(title, year)
        
        return None
    
    def _is_valid_video_url(self, url):
        """Check if URL is a valid video URL"""
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm']
        
        # Check for direct file extensions
        for ext in video_extensions:
            if url.lower().endswith(ext):
                return True
        
        # Check for streaming formats
        streaming_indicators = ['m3u8', 'mpd', '/stream/', '/play/']
        for indicator in streaming_indicators:
            if indicator in url.lower():
                return True
        
        return False
    
    def _search_video_server(self, title, year):
        """Search your video server for the movie (placeholder)"""
        
        # Placeholder implementation
        # In a real scenario, you would:
        # 1. Search your video server/database
        # 2. Query your CDN
        # 3. Check multiple video sources
        # 4. Return the best quality available
        
        # Example URLs (replace with your actual logic)
        sample_urls = [
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"
        ]
        
        # Simple title matching (implement your own logic)
        title_lower = title.lower()
        if 'bunny' in title_lower:
            return sample_urls[0]
        elif 'elephant' in title_lower:
            return sample_urls[1]
        elif 'sintel' in title_lower:
            return sample_urls[2]
        
        return None
    
    def get_info(self):
        return {
            'name': 'Direct Video',
            'description': 'Direct video file URLs and streaming sources'
        }

class YouTubeProvider(BaseProvider):
    """Provider for YouTube videos"""
    
    def get_video_url(self, movie_details):
        """Get YouTube video URL"""
        
        # Check for trailer URL first
        if 'trailer_url' in movie_details:
            trailer_url = movie_details['trailer_url']
            if 'youtube.com' in trailer_url or 'youtu.be' in trailer_url:
                video_id = self._extract_youtube_id(trailer_url)
                if video_id:
                    return f"plugin://plugin.video.youtube/play/?video_id={video_id}"
        
        # Search YouTube for full movie
        title = movie_details.get('title', '')
        year = movie_details.get('year', '')
        
        if title:
            return self._search_youtube(title, year)
        
        return None
    
    def _extract_youtube_id(self, url):
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _search_youtube(self, title, year):
        """Search YouTube for movie (placeholder)"""
        
        # In a real implementation, you would use YouTube API
        # to search for full movies that are legally available
        
        search_query = f"{title} {year} full movie"
        encoded_query = quote(search_query)
        
        # Return YouTube search URL that can be handled by YouTube addon
        return f"plugin://plugin.video.youtube/search/?q={encoded_query}"
    
    def get_info(self):
        return {
            'name': 'YouTube',
            'description': 'YouTube videos and trailers'
        }

class VimeoProvider(BaseProvider):
    """Provider for Vimeo videos"""
    
    def get_video_url(self, movie_details):
        """Get Vimeo video URL"""
        
        # Check for Vimeo URL in movie details
        if 'vimeo_url' in movie_details:
            return movie_details['vimeo_url']
        
        # Placeholder for Vimeo search
        return None
    
    def get_info(self):
        return {
            'name': 'Vimeo',
            'description': 'Vimeo videos'
        }

class DailymotionProvider(BaseProvider):
    """Provider for Dailymotion videos"""
    
    def get_video_url(self, movie_details):
        """Get Dailymotion video URL"""
        
        # Check for Dailymotion URL in movie details
        if 'dailymotion_url' in movie_details:
            return movie_details['dailymotion_url']
        
        # Placeholder for Dailymotion search
        return None
    
    def get_info(self):
        return {
            'name': 'Dailymotion',
            'description': 'Dailymotion videos'
        }

class CustomProvider(BaseProvider):
    """Custom provider for user-defined sources"""
    
    def get_video_url(self, movie_details):
        """Get video URL from custom sources"""
        
        # Check for custom video sources
        custom_sources = movie_details.get('custom_sources', [])
        
        for source in custom_sources:
            if isinstance(source, dict) and 'url' in source:
                # Validate and return first valid URL
                if self._is_valid_url(source['url']):
                    return source['url']
        
        return None
    
    def _is_valid_url(self, url):
        """Basic URL validation"""
        return url.startswith(('http://', 'https://', 'plugin://'))
    
    def get_info(self):
        return {
            'name': 'Custom',
            'description': 'User-defined custom video sources'
        }