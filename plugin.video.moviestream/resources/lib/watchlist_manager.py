#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Watchlist Manager for MovieStream Kodi Addon
Handles watchlist, favorites, and watch history
"""

import xbmc
import xbmcaddon
import xbmcvfs
import json
import os
from datetime import datetime

class WatchlistManager:
    """Manages user watchlist, favorites, and history"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.profile_path = xbmcvfs.translatePath(self.addon.getAddonInfo('profile'))
        
        # Ensure profile directory exists
        if not xbmcvfs.exists(self.profile_path):
            xbmcvfs.mkdirs(self.profile_path)
        
        self.watchlist_file = os.path.join(self.profile_path, 'watchlist.json')
        self.favorites_file = os.path.join(self.profile_path, 'favorites.json') 
        self.history_file = os.path.join(self.profile_path, 'history.json')
    
    def _load_json_file(self, filepath):
        """Load data from JSON file"""
        try:
            if xbmcvfs.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            xbmc.log(f"MovieStream: Error loading {filepath}: {str(e)}", xbmc.LOGERROR)
        
        return []
    
    def _save_json_file(self, filepath, data):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            xbmc.log(f"MovieStream: Error saving {filepath}: {str(e)}", xbmc.LOGERROR)
            return False
    
    def add_to_watchlist(self, item_data):
        """Add item to watchlist"""
        try:
            watchlist = self._load_json_file(self.watchlist_file)
            
            # Check if item already exists
            item_id = item_data.get('tmdb_id') or item_data.get('imdb_id') or item_data.get('title')
            
            for item in watchlist:
                if (item.get('tmdb_id') == item_id or 
                    item.get('imdb_id') == item_id or 
                    item.get('title') == item_data.get('title')):
                    return False  # Already exists
            
            # Add timestamp
            item_data['added_date'] = datetime.now().isoformat()
            watchlist.append(item_data)
            
            return self._save_json_file(self.watchlist_file, watchlist)
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error adding to watchlist: {str(e)}", xbmc.LOGERROR)
            return False
    
    def remove_from_watchlist(self, item_data):
        """Remove item from watchlist"""
        try:
            watchlist = self._load_json_file(self.watchlist_file)
            
            item_id = item_data.get('tmdb_id') or item_data.get('imdb_id') or item_data.get('title')
            
            watchlist = [item for item in watchlist if not (
                item.get('tmdb_id') == item_id or 
                item.get('imdb_id') == item_id or 
                item.get('title') == item_data.get('title')
            )]
            
            return self._save_json_file(self.watchlist_file, watchlist)
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error removing from watchlist: {str(e)}", xbmc.LOGERROR)
            return False
    
    def get_watchlist(self):
        """Get user's watchlist"""
        return self._load_json_file(self.watchlist_file)
    
    def add_to_favorites(self, item_data):
        """Add item to favorites"""
        try:
            favorites = self._load_json_file(self.favorites_file)
            
            # Check if item already exists
            item_id = item_data.get('tmdb_id') or item_data.get('imdb_id') or item_data.get('title')
            
            for item in favorites:
                if (item.get('tmdb_id') == item_id or 
                    item.get('imdb_id') == item_id or 
                    item.get('title') == item_data.get('title')):
                    return False  # Already exists
            
            # Add timestamp
            item_data['added_date'] = datetime.now().isoformat()
            favorites.append(item_data)
            
            return self._save_json_file(self.favorites_file, favorites)
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error adding to favorites: {str(e)}", xbmc.LOGERROR)
            return False
    
    def get_favorites(self):
        """Get user's favorites"""
        return self._load_json_file(self.favorites_file)
    
    def add_to_history(self, item_data):
        """Add item to watch history"""
        try:
            history = self._load_json_file(self.history_file)
            
            # Remove if already exists (to move to top)
            item_id = item_data.get('tmdb_id') or item_data.get('imdb_id') or item_data.get('title')
            
            history = [item for item in history if not (
                item.get('tmdb_id') == item_id or 
                item.get('imdb_id') == item_id or 
                item.get('title') == item_data.get('title')
            )]
            
            # Add to beginning with timestamp
            item_data['watched_date'] = datetime.now().isoformat()
            history.insert(0, item_data)
            
            # Limit history to 100 items
            history = history[:100]
            
            return self._save_json_file(self.history_file, history)
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error adding to history: {str(e)}", xbmc.LOGERROR)
            return False
    
    def get_history(self):
        """Get watch history"""
        return self._load_json_file(self.history_file)
    
    def get_stats(self):
        """Get statistics for all lists"""
        return {
            'watchlist_count': len(self.get_watchlist()),
            'favorites_count': len(self.get_favorites()),
            'history_count': len(self.get_history())
        }
    
    def get_context_menu_items(self, item_data):
        """Get context menu items for an item"""
        items = []
        
        # Add to Watchlist
        items.append((
            'Add to Watchlist',
            f'RunPlugin({self._get_action_url("add_watchlist", item_data)})'
        ))
        
        # Add to Favorites
        items.append((
            'Add to Favorites', 
            f'RunPlugin({self._get_action_url("add_favorites", item_data)})'
        ))
        
        return items
    
    def _get_action_url(self, action, item_data):
        """Get action URL for context menu"""
        # This would be implemented with the main plugin's get_url function
        # For now, return a placeholder
        return f'plugin://plugin.video.moviestream/?action={action}&item_data={json.dumps(item_data)}'