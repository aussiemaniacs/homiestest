#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import os
import json
from urllib.parse import urlencode

class VideoPlayer:
    """Handle video playback functionality with M3U/M3U8 support"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.player = xbmc.Player()
    
    def play_video(self, video_url, metadata=None):
        """Play a video with metadata"""
        if not video_url:
            xbmcgui.Dialog().notification('MovieStream', 'No video URL provided', xbmcgui.NOTIFICATION_ERROR)
            return False
        
        try:
            # Create ListItem for the video
            list_item = self._create_list_item(video_url, metadata)
            
            # Handle different URL types
            if self._is_plugin_url(video_url):
                # For plugin URLs, play directly
                self.player.play(video_url, list_item)
            else:
                # Set resolved URL for plugin playbook
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, list_item)
            
            return True
            
        except Exception as e:
            xbmc.log(f"MovieStream Player Error: {str(e)}", xbmc.LOGERROR)
            xbmcgui.Dialog().notification('MovieStream', 'Playback failed', xbmcgui.NOTIFICATION_ERROR)
            return False
    
    def _is_plugin_url(self, url):
        """Check if URL is a plugin URL"""
        return url.startswith('plugin://')
    
    def _create_list_item(self, video_url, metadata=None):
        """Create a ListItem with metadata for playback"""
        if metadata is None:
            metadata = {}
        
        # Create the ListItem
        title = metadata.get('title', 'Unknown Title')
        list_item = xbmcgui.ListItem(label=title, path=video_url)
        
        # Set video properties
        list_item.setProperty('IsPlayable', 'true')
        
        # Set specific properties for M3U8/HLS streams
        if self._is_hls_stream(video_url):
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            list_item.setMimeType('application/vnd.apple.mpegurl')
        
        # Set video info
        info_dict = self._build_info_dict(metadata)
        list_item.setInfo('video', info_dict)
        
        # Set artwork
        art_dict = self._build_art_dict(metadata)
        if art_dict:
            list_item.setArt(art_dict)
        
        # Set subtitles if available
        subtitles = metadata.get('subtitles', [])
        if subtitles and self.addon.getSettingBool('enable_subtitles'):
            subtitle_urls = [sub.get('url') for sub in subtitles if sub.get('url')]
            if subtitle_urls:
                list_item.setSubtitles(subtitle_urls)
        
        # Set stream info
        self._set_stream_info(list_item, metadata)
        
        return list_item
    
    def _is_hls_stream(self, url):
        """Check if URL is an HLS stream"""
        return (url.lower().endswith('.m3u8') or 
                'manifest.m3u8' in url.lower() or
                'playlist.m3u8' in url.lower())
    
    def _build_info_dict(self, metadata):
        """Build the info dictionary for the ListItem"""
        info = {}
        
        # Basic info
        if 'title' in metadata:
            info['title'] = metadata['title']
        
        if 'plot' in metadata:
            info['plot'] = metadata['plot']
        elif 'overview' in metadata:
            info['plot'] = metadata['overview']
        
        if 'year' in metadata:
            info['year'] = int(metadata['year']) if str(metadata['year']).isdigit() else 0
        elif 'release_date' in metadata:
            year = metadata['release_date'][:4] if metadata['release_date'] else ''
            info['year'] = int(year) if year.isdigit() else 0
        
        if 'genre' in metadata:
            info['genre'] = metadata['genre']
        elif 'genres' in metadata:
            if isinstance(metadata['genres'], list):
                info['genre'] = ', '.join([g.get('name', '') for g in metadata['genres']])
            else:
                info['genre'] = str(metadata['genres'])
        
        if 'rating' in metadata:
            info['rating'] = float(metadata['rating'])
        elif 'vote_average' in metadata:
            info['rating'] = float(metadata['vote_average'])
        
        if 'votes' in metadata:
            info['votes'] = str(metadata['votes'])
        elif 'vote_count' in metadata:
            info['votes'] = str(metadata['vote_count'])
        
        if 'runtime' in metadata:
            info['duration'] = int(metadata['runtime']) * 60  # Convert minutes to seconds
        elif 'episode_run_time' in metadata and metadata['episode_run_time']:
            info['duration'] = int(metadata['episode_run_time'][0]) * 60
        
        if 'director' in metadata:
            info['director'] = metadata['director']
        elif 'created_by' in metadata and metadata['created_by']:
            info['director'] = ', '.join([c.get('name', '') for c in metadata['created_by']])
        
        if 'cast' in metadata:
            if isinstance(metadata['cast'], list):
                info['cast'] = metadata['cast']
            else:
                info['cast'] = [str(metadata['cast'])]
        elif 'credits' in metadata and 'cast' in metadata['credits']:
            cast_list = metadata['credits']['cast'][:10]  # Limit to first 10 cast members
            info['cast'] = [actor.get('name', '') for actor in cast_list]
        
        # Handle different media types
        if 'season_number' in metadata:
            info['season'] = int(metadata['season_number'])
        elif 'season' in metadata:
            info['season'] = int(metadata['season'])
        
        if 'episode_number' in metadata:
            info['episode'] = int(metadata['episode_number'])
        elif 'episode' in metadata:
            info['episode'] = int(metadata['episode'])
        
        # Set media type
        if 'episode_number' in metadata or 'episode' in metadata:
            info['mediatype'] = 'episode'
        elif 'season_number' in metadata or 'first_air_date' in metadata:
            info['mediatype'] = 'tvshow'
        else:
            info['mediatype'] = 'movie'
        
        return info
    
    def _build_art_dict(self, metadata):
        """Build the art dictionary for the ListItem"""
        art = {}
        
        # Poster
        if 'poster_url' in metadata:
            art['poster'] = metadata['poster_url']
            art['thumb'] = metadata['poster_url']
        elif 'poster_path' in metadata:
            art['poster'] = f"https://image.tmdb.org/t/p/w500{metadata['poster_path']}"
            art['thumb'] = f"https://image.tmdb.org/t/p/w500{metadata['poster_path']}"
        
        # Fanart/Backdrop
        if 'backdrop_url' in metadata:
            art['fanart'] = metadata['backdrop_url']
            art['landscape'] = metadata['backdrop_url']
        elif 'backdrop_path' in metadata:
            art['fanart'] = f"https://image.tmdb.org/t/p/w1280{metadata['backdrop_path']}"
            art['landscape'] = f"https://image.tmdb.org/t/p/w1280{metadata['backdrop_path']}"
        
        # Episode still
        if 'still_path' in metadata:
            art['thumb'] = f"https://image.tmdb.org/t/p/w500{metadata['still_path']}"
        
        return art
    
    def _set_stream_info(self, list_item, metadata):
        """Set stream information for the ListItem"""
        # Video stream info
        video_info = {}
        
        if 'quality' in metadata:
            quality = metadata['quality'].lower()
            if '4k' in quality or '2160p' in quality:
                video_info['width'] = 3840
                video_info['height'] = 2160
            elif '1080p' in quality:
                video_info['width'] = 1920
                video_info['height'] = 1080
            elif '720p' in quality:
                video_info['width'] = 1280
                video_info['height'] = 720
            elif '480p' in quality:
                video_info['width'] = 854
                video_info['height'] = 480
        
        if video_info:
            list_item.addStreamInfo('video', video_info)
        
        # Audio stream info
        audio_info = {
            'codec': 'aac',
            'channels': 2
        }
        list_item.addStreamInfo('audio', audio_info)
    
    def play_trailer(self, trailer_url, title="Trailer"):
        """Play a trailer"""
        if not trailer_url:
            return False
        
        # Handle YouTube URLs
        if 'youtube.com' in trailer_url or 'youtu.be' in trailer_url:
            video_id = self._extract_youtube_id(trailer_url)
            if video_id:
                youtube_url = f"plugin://plugin.video.youtube/play/?video_id={video_id}"
                list_item = xbmcgui.ListItem(label=title, path=youtube_url)
                list_item.setProperty('IsPlayable', 'true')
                xbmc.Player().play(youtube_url, list_item)
                return True
        
        # For direct video URLs
        list_item = xbmcgui.ListItem(label=title, path=trailer_url)
        list_item.setProperty('IsPlayable', 'true')
        
        # Handle HLS streams for trailers too
        if self._is_hls_stream(trailer_url):
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            list_item.setMimeType('application/vnd.apple.mpegurl')
        
        xbmc.Player().play(trailer_url, list_item)
        return True
    
    def _extract_youtube_id(self, url):
        """Extract YouTube video ID from URL"""
        import re
        
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_player_status(self):
        """Get current player status"""
        if self.player.isPlaying():
            return {
                'playing': True,
                'time': self.player.getTime(),
                'total_time': self.player.getTotalTime(),
                'file': self.player.getPlayingFile()
            }
        return {'playing': False}
    
    def seek_to(self, position):
        """Seek to a specific position"""
        if self.player.isPlaying():
            self.player.seekTime(position)
    
    def set_volume(self, volume):
        """Set player volume (0-100)"""
        xbmc.executebuiltin(f'SetVolume({volume})')
    
    def add_subtitle(self, subtitle_url):
        """Add subtitle to current playback"""
        if self.player.isPlaying():
            self.player.setSubtitles(subtitle_url)
