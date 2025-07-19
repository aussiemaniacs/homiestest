#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Watchlist and Favorites Manager for MovieStream Kodi Addon
Handles local and cloud-sync watchlists, favorites, watch history
"""

import xbmc
import xbmcaddon
import xbmcvfs
import json
import os
import time
from datetime import datetime
try:
    from urllib.parse import quote as urlparse_quote
except ImportError:
    from urllib import quote as urlparse_quote

class WatchlistManager:
    """Manager for watchlists, favorites, and watch history"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.profile_path = xbmcvfs.translatePath(self.addon.getAddonInfo('profile'))
        
        # Ensure profile directory exists
        if not xbmcvfs.exists(self.profile_path):
            xbmcvfs.mkdirs(self.profile_path)
        
        # File paths
        self.watchlist_file = os.path.join(self.profile_path, 'watchlist.json')
        self.favorites_file = os.path.join(self.profile_path, 'favorites.json')
        self.history_file = os.path.join(self.profile_path, 'watch_history.json')
        self.resume_file = os.path.join(self.profile_path, 'resume_points.json')
        
        # Initialize data
        self.watchlist = self._load_json_file(self.watchlist_file)
        self.favorites = self._load_json_file(self.favorites_file)
        self.history = self._load_json_file(self.history_file)
        self.resume_points = self._load_json_file(self.resume_file)
    
    def _load_json_file(self, file_path):
        """Load JSON data from file"""
        try:
            if xbmcvfs.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            xbmc.log(f"MovieStream: Error loading {file_path}: {str(e)}", xbmc.LOGERROR)
        
        return []
    
    def _save_json_file(self, file_path, data):
        """Save JSON data to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            xbmc.log(f"MovieStream: Error saving {file_path}: {str(e)}", xbmc.LOGERROR)
            return False
    
    def _create_item_id(self, item):
        """Create unique ID for an item"""
        if item.get('type') == 'movie':
            return f"movie_{item.get('tmdb_id', item.get('title', '').replace(' ', '_'))}"
        elif item.get('type') == 'tvshow':
            return f"show_{item.get('tmdb_id', item.get('title', '').replace(' ', '_'))}"
        elif item.get('type') == 'episode':
            return f"episode_{item.get('show_tmdb_id')}_{item.get('season')}_{item.get('episode')}"
        else:
            return f"unknown_{item.get('title', '').replace(' ', '_')}"
    
    # WATCHLIST METHODS
    
    def add_to_watchlist(self, item):
        """Add item to watchlist"""
        try:
            item_id = self._create_item_id(item)
            
            # Check if already in watchlist
            if any(w.get('id') == item_id for w in self.watchlist):
                return False
            
            # Add timestamp and ID
            item_data = item.copy()
            item_data['id'] = item_id
            item_data['added_date'] = datetime.now().isoformat()
            
            self.watchlist.append(item_data)
            self._save_json_file(self.watchlist_file, self.watchlist)
            
            return True
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error adding to watchlist: {str(e)}", xbmc.LOGERROR)
            return False
    
    def remove_from_watchlist(self, item):
        """Remove item from watchlist"""
        try:
            item_id = self._create_item_id(item)
            
            self.watchlist = [w for w in self.watchlist if w.get('id') != item_id]
            self._save_json_file(self.watchlist_file, self.watchlist)
            
            return True
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error removing from watchlist: {str(e)}", xbmc.LOGERROR)
            return False
    
    def is_in_watchlist(self, item):
        """Check if item is in watchlist"""
        item_id = self._create_item_id(item)
        return any(w.get('id') == item_id for w in self.watchlist)
    
    def get_watchlist(self, item_type=None):
        """Get watchlist items"""
        if item_type:
            return [w for w in self.watchlist if w.get('type') == item_type]
        return self.watchlist
    
    def clear_watchlist(self):
        """Clear entire watchlist"""
        self.watchlist = []
        return self._save_json_file(self.watchlist_file, self.watchlist)
    
    # FAVORITES METHODS
    
    def add_to_favorites(self, item):
        """Add item to favorites"""
        try:
            item_id = self._create_item_id(item)
            
            # Check if already in favorites
            if any(f.get('id') == item_id for f in self.favorites):
                return False
            
            # Add timestamp and ID
            item_data = item.copy()
            item_data['id'] = item_id
            item_data['added_date'] = datetime.now().isoformat()
            
            self.favorites.append(item_data)
            self._save_json_file(self.favorites_file, self.favorites)
            
            return True
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error adding to favorites: {str(e)}", xbmc.LOGERROR)
            return False
    
    def remove_from_favorites(self, item):
        """Remove item from favorites"""
        try:
            item_id = self._create_item_id(item)
            
            self.favorites = [f for f in self.favorites if f.get('id') != item_id]
            self._save_json_file(self.favorites_file, self.favorites)
            
            return True
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error removing from favorites: {str(e)}", xbmc.LOGERROR)
            return False
    
    def is_favorite(self, item):
        """Check if item is favorite"""
        item_id = self._create_item_id(item)
        return any(f.get('id') == item_id for f in self.favorites)
    
    def get_favorites(self, item_type=None):
        """Get favorite items"""
        if item_type:
            return [f for f in self.favorites if f.get('type') == item_type]
        return self.favorites
    
    def clear_favorites(self):
        """Clear all favorites"""
        self.favorites = []
        return self._save_json_file(self.favorites_file, self.favorites)
    
    # WATCH HISTORY METHODS
    
    def add_to_history(self, item, watch_time=None):
        """Add item to watch history"""
        try:
            item_id = self._create_item_id(item)
            current_time = datetime.now().isoformat()
            
            # Remove existing entry if present
            self.history = [h for h in self.history if h.get('id') != item_id]
            
            # Add new entry at the beginning
            item_data = item.copy()
            item_data['id'] = item_id
            item_data['watched_date'] = current_time
            item_data['watch_time'] = watch_time or current_time
            
            self.history.insert(0, item_data)
            
            # Limit history size
            max_history = 1000
            if len(self.history) > max_history:
                self.history = self.history[:max_history]
            
            self._save_json_file(self.history_file, self.history)
            
            # Auto-remove from watchlist if enabled
            if self.addon.getSettingBool('auto_remove_watched'):
                self.remove_from_watchlist(item)
            
            return True
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error adding to history: {str(e)}", xbmc.LOGERROR)
            return False
    
    def is_watched(self, item):
        """Check if item has been watched"""
        item_id = self._create_item_id(item)
        return any(h.get('id') == item_id for h in self.history)
    
    def get_watch_history(self, item_type=None, limit=None):
        """Get watch history"""
        history = self.history
        
        if item_type:
            history = [h for h in history if h.get('type') == item_type]
        
        if limit:
            history = history[:limit]
        
        return history
    
    def clear_history(self):
        """Clear watch history"""
        self.history = []
        return self._save_json_file(self.history_file, self.history)
    
    # RESUME POINTS
    
    def save_resume_point(self, item, position, total_time):
        """Save resume point for item"""
        try:
            item_id = self._create_item_id(item)
            
            # Calculate percentage watched
            percentage = (position / total_time * 100) if total_time > 0 else 0
            
            # Don't save if watched past the threshold
            watch_threshold = self.addon.getSettingInt('mark_watched_percentage') or 90
            if percentage >= watch_threshold:
                # Mark as watched instead
                self.add_to_history(item)
                # Remove resume point
                self.resume_points = [r for r in self.resume_points if r.get('id') != item_id]
            else:
                # Save resume point
                resume_data = {
                    'id': item_id,
                    'position': position,
                    'total_time': total_time,
                    'percentage': percentage,
                    'timestamp': datetime.now().isoformat(),
                    'title': item.get('title', 'Unknown'),
                    'type': item.get('type', 'unknown')
                }
                
                # Remove existing resume point
                self.resume_points = [r for r in self.resume_points if r.get('id') != item_id]
                # Add new resume point
                self.resume_points.insert(0, resume_data)
                
                # Limit resume points
                if len(self.resume_points) > 100:
                    self.resume_points = self.resume_points[:100]
            
            self._save_json_file(self.resume_file, self.resume_points)
            return True
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error saving resume point: {str(e)}", xbmc.LOGERROR)
            return False
    
    def get_resume_point(self, item):
        """Get resume point for item"""
        item_id = self._create_item_id(item)
        
        for resume in self.resume_points:
            if resume.get('id') == item_id:
                return resume
        
        return None
    
    def remove_resume_point(self, item):
        """Remove resume point for item"""
        item_id = self._create_item_id(item)
        self.resume_points = [r for r in self.resume_points if r.get('id') != item_id]
        return self._save_json_file(self.resume_file, self.resume_points)
    
    def get_resume_list(self, limit=20):
        """Get list of items with resume points"""
        return self.resume_points[:limit]
    
    # STATISTICS
    
    def get_stats(self):
        """Get watchlist statistics"""
        return {
            'watchlist_count': len(self.watchlist),
            'favorites_count': len(self.favorites),
            'history_count': len(self.history),
            'resume_count': len(self.resume_points),
            'watchlist_movies': len([w for w in self.watchlist if w.get('type') == 'movie']),
            'watchlist_shows': len([w for w in self.watchlist if w.get('type') == 'tvshow']),
            'favorite_movies': len([f for f in self.favorites if f.get('type') == 'movie']),
            'favorite_shows': len([f for f in self.favorites if f.get('type') == 'tvshow'])
        }
    
    # CONTEXT MENU HELPERS
    
    def get_context_menu_items(self, item):
        """Get context menu items for an item"""
        context_items = []
        
        # Watchlist
        if self.is_in_watchlist(item):
            context_items.append(('Remove from Watchlist', f'RunPlugin(plugin://plugin.video.moviestream/?action=remove_watchlist&item_data={json.dumps(item)})'))
        else:
            context_items.append(('Add to Watchlist', f'RunPlugin(plugin://plugin.video.moviestream/?action=add_watchlist&item_data={json.dumps(item)})'))
        
        # Favorites
        if self.is_favorite(item):
            context_items.append(('Remove from Favorites', f'RunPlugin(plugin://plugin.video.moviestream/?action=remove_favorite&item_data={json.dumps(item)})'))
        else:
            context_items.append(('Add to Favorites', f'RunPlugin(plugin://plugin.video.moviestream/?action=add_favorite&item_data={json.dumps(item)})'))
        
        # Resume point
        resume_point = self.get_resume_point(item)
        if resume_point:
            context_items.append(('Clear Resume Point', f'RunPlugin(plugin://plugin.video.moviestream/?action=clear_resume&item_data={json.dumps(item)})'))
        
        return context_items