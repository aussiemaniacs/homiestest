#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Video Player Client for MovieStream Kodi Addon
Handles video playback with various formats and streaming protocols
"""

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

class VideoPlayer:
    """Video Player with support for various formats"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.player = xbmc.Player()
    
    def play_url(self, url, title="", subtitle_url=None, headers=None):
        """Play a video URL with metadata"""
        try:
            # Create list item
            list_item = xbmcgui.ListItem(label=title, path=url)
            
            # Set video info
            if title:
                list_item.setInfo('video', {'title': title})
            
            # Handle different URL types
            if url.endswith('.m3u8') or 'm3u8' in url:
                # M3U8/HLS stream
                list_item.setProperty('inputstream', 'inputstream.adaptive')
                list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
                
            elif url.endswith('.mpd') or 'mpd' in url:
                # DASH stream
                list_item.setProperty('inputstream', 'inputstream.adaptive')
                list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            
            # Add headers if provided
            if headers:
                header_string = '|' + '&'.join([f'{k}={v}' for k, v in headers.items()])
                list_item.setPath(url + header_string)
            
            # Add subtitles if provided
            if subtitle_url:
                list_item.setSubtitles([subtitle_url])
            
            # Play the video
            self.player.play(url, list_item)
            return True
            
        except Exception as e:
            xbmc.log(f"MovieStream: Video player error: {str(e)}", xbmc.LOGERROR)
            return False
    
    def is_playing(self):
        """Check if player is currently playing"""
        return self.player.isPlaying()
    
    def stop(self):
        """Stop playback"""
        if self.player.isPlaying():
            self.player.stop()