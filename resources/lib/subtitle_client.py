#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Subtitle Client for MovieStream Kodi Addon
Handles subtitle downloading and management
"""

import xbmc
import xbmcaddon
import xbmcvfs
import requests
import os
import json
from urllib.parse import quote

class SubtitleClient:
    """Client for subtitle management"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.session = requests.Session()
        self.cache_dir = xbmcvfs.translatePath(os.path.join(self.addon.getAddonInfo('profile'), 'subtitles'))
        
        # Create cache directory
        if not xbmcvfs.exists(self.cache_dir):
            xbmcvfs.mkdirs(self.cache_dir)
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': 'MovieStream Kodi Addon 1.0.0'
        })
    
    def download_subtitle(self, subtitle_url, movie_title, language='en'):
        """Download subtitle file to cache"""
        try:
            # Create safe filename
            safe_title = self._sanitize_filename(movie_title)
            filename = f"{safe_title}_{language}.srt"
            file_path = os.path.join(self.cache_dir, filename)
            
            # Check if already cached
            if xbmcvfs.exists(file_path):
                return file_path
            
            # Download subtitle
            response = self.session.get(subtitle_url, timeout=10)
            response.raise_for_status()
            
            # Save to file
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            xbmc.log(f"MovieStream: Downloaded subtitle for {movie_title} ({language})", xbmc.LOGINFO)
            return file_path
            
        except Exception as e:
            xbmc.log(f"MovieStream Subtitle Error: {str(e)}", xbmc.LOGERROR)
            return None
    
    def _sanitize_filename(self, filename):
        """Create safe filename from movie title"""
        import re
        
        # Remove invalid characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '', filename)
        safe_name = safe_name.replace(' ', '_')
        
        # Limit length
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
        
        return safe_name
    
    def search_opensubtitles(self, movie_title, year=None, language='en'):
        """Search OpenSubtitles for subtitles (placeholder implementation)"""
        
        # This is a placeholder implementation
        # In a real scenario, you would integrate with:
        # - OpenSubtitles API
        # - Subscene
        # - Other subtitle databases
        
        try:
            # Example OpenSubtitles API call structure
            params = {
                'query': movie_title,
                'languages': language
            }
            
            if year:
                params['year'] = year
            
            # Placeholder response
            return [
                {
                    'url': f'https://example.com/subtitles/{quote(movie_title)}_{language}.srt',
                    'language': language,
                    'format': 'srt',
                    'rating': 8.5,
                    'downloads': 1000
                }
            ]
            
        except Exception as e:
            xbmc.log(f"MovieStream OpenSubtitles Error: {str(e)}", xbmc.LOGERROR)
            return []
    
    def get_subtitle_languages(self):
        """Get supported subtitle languages"""
        return [
            {'code': 'en', 'name': 'English'},
            {'code': 'es', 'name': 'Spanish'},
            {'code': 'fr', 'name': 'French'},
            {'code': 'de', 'name': 'German'},
            {'code': 'it', 'name': 'Italian'},
            {'code': 'pt', 'name': 'Portuguese'},
            {'code': 'ru', 'name': 'Russian'},
            {'code': 'zh', 'name': 'Chinese'},
            {'code': 'ja', 'name': 'Japanese'},
            {'code': 'ko', 'name': 'Korean'}
        ]
    
    def convert_subtitle_format(self, subtitle_path, target_format='srt'):
        """Convert subtitle format (placeholder implementation)"""
        
        # This would handle conversion between subtitle formats
        # SRT, VTT, ASS, SSA, etc.
        
        if target_format.lower() == 'srt':
            return subtitle_path  # Already SRT
        
        # Placeholder for format conversion
        return subtitle_path
    
    def clean_subtitle_cache(self):
        """Clean old subtitle files from cache"""
        try:
            import time
            
            if not xbmcvfs.exists(self.cache_dir):
                return
            
            # Get cache duration from settings (hours)
            cache_duration = int(self.addon.getSetting('subtitle_cache_duration') or '24')
            max_age = cache_duration * 3600  # Convert to seconds
            
            current_time = time.time()
            
            # List files in cache directory
            dirs, files = xbmcvfs.listdir(self.cache_dir)
            
            for filename in files:
                if filename.endswith('.srt'):
                    file_path = os.path.join(self.cache_dir, filename)
                    
                    # Check file age
                    stat = xbmcvfs.Stat(file_path)
                    if current_time - stat.st_mtime() > max_age:
                        xbmcvfs.delete(file_path)
                        xbmc.log(f"MovieStream: Cleaned old subtitle: {filename}", xbmc.LOGINFO)
            
        except Exception as e:
            xbmc.log(f"MovieStream Subtitle Cache Error: {str(e)}", xbmc.LOGERROR)