#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Streaming Providers for MovieStream Kodi Addon
Handles multiple video streaming sources including M3U/M3U8
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
            'User-Agent': 'MovieStream Kodi Addon 2.0.0'
        })
        
        # Initialize providers
        self.providers = {
            'direct': DirectVideoProvider(self.session),
            'youtube': YouTubeProvider(self.session),
            'vimeo': VimeoProvider(self.session),
            'dailymotion': DailymotionProvider(self.session),
            'm3u': M3UProvider(self.session),
            'm3u8': M3U8Provider(self.session),
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
        provider_order = ['direct', 'm3u8', 'm3u', 'youtube', 'vimeo', 'dailymotion', 'custom']
        
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
            return self._search_video_server(title, year)
        
        return None
    
    def _is_valid_video_url(self, url):
        """Check if URL is a valid video URL"""
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m3u', '.m3u8']
        
        # Check for direct file extensions
        for ext in video_extensions:
            if url.lower().endswith(ext):
                return True
        
        # Check for streaming formats
        streaming_indicators = ['m3u8', 'mpd', '/stream/', '/play/', 'manifest']
        for indicator in streaming_indicators:
            if indicator in url.lower():
                return True
        
        return False
    
    def _search_video_server(self, title, year):
        """Search your video server for the movie (placeholder)"""
        
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

class M3UProvider(BaseProvider):
    """Provider for M3U playlist files"""
    
    def get_video_url(self, movie_details):
        """Get M3U playlist URL"""
        
        # Check for M3U URL in movie details
        if 'm3u_url' in movie_details:
            return self._process_m3u_url(movie_details['m3u_url'])
        
        # Check if video_url is M3U
        video_url = movie_details.get('video_url', '')
        if video_url.lower().endswith('.m3u') or '/playlist.m3u' in video_url.lower():
            return self._process_m3u_url(video_url)
        
        return None
    
    def _process_m3u_url(self, url):
        """Process M3U URL and extract playable streams"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            content = response.text
            
            # Parse M3U content
            streams = self._parse_m3u_content(content, url)
            
            if streams:
                # Return first valid stream or best quality stream
                return self._select_best_stream(streams)
            
        except Exception as e:
            xbmc.log(f"MovieStream M3U Error: {str(e)}", xbmc.LOGERROR)
        
        return url  # Return original URL as fallback
    
    def _parse_m3u_content(self, content, base_url):
        """Parse M3U content and extract stream URLs"""
        streams = []
        lines = content.split('\n')
        
        current_info = {}
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF:'):
                # Parse stream info
                info_match = re.search(r'#EXTINF:([^,]*),(.*)$', line)
                if info_match:
                    duration = info_match.group(1)
                    title = info_match.group(2)
                    current_info = {'duration': duration, 'title': title}
            
            elif line and not line.startswith('#'):
                # This is a stream URL
                stream_url = line
                
                # Make absolute URL if relative
                if not stream_url.startswith('http'):
                    from urllib.parse import urljoin
                    stream_url = urljoin(base_url, stream_url)
                
                current_info['url'] = stream_url
                streams.append(current_info.copy())
                current_info = {}
        
        return streams
    
    def _select_best_stream(self, streams):
        """Select the best quality stream from available streams"""
        if not streams:
            return None
        
        # Prefer streams with quality indicators
        quality_keywords = ['1080p', '720p', '480p', 'hd', 'high']
        
        for keyword in quality_keywords:
            for stream in streams:
                if keyword in stream.get('title', '').lower():
                    return stream['url']
        
        # Return first stream if no quality preference found
        return streams[0]['url']
    
    def get_info(self):
        return {
            'name': 'M3U Playlists',
            'description': 'M3U playlist files for IPTV and streaming'
        }

class M3U8Provider(BaseProvider):
    """Provider for M3U8 HLS (HTTP Live Streaming) files"""
    
    def get_video_url(self, movie_details):
        """Get M3U8 HLS URL"""
        
        # Check for M3U8 URL in movie details
        if 'm3u8_url' in movie_details:
            return self._process_m3u8_url(movie_details['m3u8_url'])
        
        # Check if video_url is M3U8
        video_url = movie_details.get('video_url', '')
        if (video_url.lower().endswith('.m3u8') or 
            '/playlist.m3u8' in video_url.lower() or
            'manifest.m3u8' in video_url.lower()):
            return self._process_m3u8_url(video_url)
        
        return None
    
    def _process_m3u8_url(self, url):
        """Process M3U8 URL and extract best quality stream"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            content = response.text
            
            # Check if this is a master playlist
            if '#EXT-X-STREAM-INF:' in content:
                # This is a master playlist, find best quality variant
                best_variant = self._parse_master_playlist(content, url)
                if best_variant:
                    return best_variant
            else:
                # This is already a media playlist
                return url
            
        except Exception as e:
            xbmc.log(f"MovieStream M3U8 Error: {str(e)}", xbmc.LOGERROR)
        
        return url  # Return original URL as fallback
    
    def _parse_master_playlist(self, content, base_url):
        """Parse master M3U8 playlist and select best variant"""
        lines = content.split('\n')
        variants = []
        
        current_variant = {}
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXT-X-STREAM-INF:'):
                # Parse stream info
                current_variant = self._parse_stream_inf(line)
            
            elif line and not line.startswith('#'):
                # This is a variant playlist URL
                variant_url = line
                
                # Make absolute URL if relative
                if not variant_url.startswith('http'):
                    from urllib.parse import urljoin
                    variant_url = urljoin(base_url, variant_url)
                
                current_variant['url'] = variant_url
                variants.append(current_variant.copy())
                current_variant = {}
        
        # Select best quality variant
        return self._select_best_variant(variants)
    
    def _parse_stream_inf(self, line):
        """Parse EXT-X-STREAM-INF line"""
        info = {}
        
        # Extract bandwidth
        bandwidth_match = re.search(r'BANDWIDTH=(\d+)', line)
        if bandwidth_match:
            info['bandwidth'] = int(bandwidth_match.group(1))
        
        # Extract resolution
        resolution_match = re.search(r'RESOLUTION=(\d+x\d+)', line)
        if resolution_match:
            info['resolution'] = resolution_match.group(1)
        
        # Extract codecs
        codecs_match = re.search(r'CODECS="([^"]+)"', line)
        if codecs_match:
            info['codecs'] = codecs_match.group(1)
        
        return info
    
    def _select_best_variant(self, variants):
        """Select the best quality variant"""
        if not variants:
            return None
        
        # Sort by bandwidth (higher is better)
        variants.sort(key=lambda x: x.get('bandwidth', 0), reverse=True)
        
        # Get user's quality preference
        quality_pref = self.addon.getSetting('video_quality') or '1080p'
        
        # Try to match quality preference
        if quality_pref == '4K':
            target_height = 2160
        elif quality_pref == '1080p':
            target_height = 1080
        elif quality_pref == '720p':
            target_height = 720
        else:
            target_height = 480
        
        # Find variant closest to target quality
        for variant in variants:
            if 'resolution' in variant:
                height = int(variant['resolution'].split('x')[1])
                if height <= target_height:
                    return variant['url']
        
        # Return highest quality if no match found
        return variants[0]['url']
    
    def get_info(self):
        return {
            'name': 'M3U8 HLS',
            'description': 'HTTP Live Streaming (HLS) M3U8 playlists'
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
        """Search YouTube for movie"""
        search_query = f"{title} {year} full movie"
        encoded_query = quote(search_query)
        
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
        
        if 'vimeo_url' in movie_details:
            return movie_details['vimeo_url']
        
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
        
        if 'dailymotion_url' in movie_details:
            return movie_details['dailymotion_url']
        
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
