#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Torrent Client for MovieStream Kodi Addon
Handles magnet links and torrent streaming
"""

import xbmc
import xbmcaddon
import requests
import json
from urllib.parse import quote, urlencode

class TorrentClient:
    """Client for torrent streaming integration"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.session = requests.Session()
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': 'MovieStream Kodi Addon 1.0.0'
        })
    
    def is_magnet_link(self, url):
        """Check if URL is a magnet link"""
        return url.startswith('magnet:')
    
    def get_torrent_info(self, magnet_link):
        """Extract torrent information from magnet link"""
        try:
            # Parse magnet link
            if not self.is_magnet_link(magnet_link):
                return None
            
            # Extract info hash and name
            info_hash = self._extract_info_hash(magnet_link)
            name = self._extract_name(magnet_link)
            
            return {
                'info_hash': info_hash,
                'name': name,
                'magnet': magnet_link
            }
            
        except Exception as e:
            xbmc.log(f"MovieStream Torrent Error: {str(e)}", xbmc.LOGERROR)
            return None
    
    def _extract_info_hash(self, magnet_link):
        """Extract info hash from magnet link"""
        import re
        
        # Look for btih parameter
        match = re.search(r'btih:([a-fA-F0-9]{40})', magnet_link)
        if match:
            return match.group(1).lower()
        
        return None
    
    def _extract_name(self, magnet_link):
        """Extract display name from magnet link"""
        import re
        from urllib.parse import unquote
        
        # Look for dn parameter (display name)
        match = re.search(r'dn=([^&]+)', magnet_link)
        if match:
            return unquote(match.group(1))
        
        return "Unknown Torrent"
    
    def convert_to_stream_url(self, magnet_link):
        """Convert magnet link to streamable URL (placeholder implementation)"""
        
        # This is a placeholder implementation
        # In a real scenario, you would integrate with:
        # - Elementum addon
        # - Torrest addon  
        # - External torrent-to-http services
        # - Cloud torrent services
        
        torrent_info = self.get_torrent_info(magnet_link)
        if not torrent_info:
            return None
        
        # Example integration with Elementum
        elementum_url = f"plugin://plugin.video.elementum/play?uri={quote(magnet_link)}"
        
        return elementum_url
    
    def is_elementum_available(self):
        """Check if Elementum addon is available"""
        try:
            import xbmcaddon
            elementum_addon = xbmcaddon.Addon('plugin.video.elementum')
            return True
        except:
            return False
    
    def is_torrest_available(self):
        """Check if Torrest addon is available"""
        try:
            import xbmcaddon
            torrest_addon = xbmcaddon.Addon('plugin.video.torrest')
            return True
        except:
            return False
    
    def get_available_torrent_clients(self):
        """Get list of available torrent clients"""
        clients = []
        
        if self.is_elementum_available():
            clients.append({
                'name': 'Elementum',
                'id': 'elementum',
                'addon_id': 'plugin.video.elementum'
            })
        
        if self.is_torrest_available():
            clients.append({
                'name': 'Torrest',
                'id': 'torrest', 
                'addon_id': 'plugin.video.torrest'
            })
        
        return clients