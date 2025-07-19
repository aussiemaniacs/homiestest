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
        
        # Initialize progress dialog
        progress = xbmcgui.DialogProgress()
        progress.create('MovieStream', 'Searching for sources...')
        
        sources = []
        self.sources = []  # Reset sources list
        
        try:
            # Get enabled scrapers
            scrapers = self._get_enabled_scrapers()
            total_scrapers = len(scrapers)
            
            if total_scrapers == 0:
                progress.close()
                return []
            
            # Thread for scraping
            scrape_thread = threading.Thread(
                target=self._perform_scraping,
                args=(data, content_type, scrapers)
            )
            scrape_thread.daemon = True
            scrape_thread.start()
            
            # Progress monitoring
            timeout = 30  # 30 seconds timeout
            start_time = time.time()
            
            while scrape_thread.is_alive():
                if progress.iscanceled():
                    break
                
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    break
                
                # Update progress
                percent = min(int((elapsed / timeout) * 100), 100)
                progress.update(percent, f'Found {len(self.sources)} sources...')
                
                xbmc.sleep(500)
            
            sources = self.sources.copy()
            
        except Exception as e:
            xbmc.log(f"MovieStream: Scraping error: {str(e)}", xbmc.LOGERROR)
        
        finally:
            progress.close()
        
        return sources
    
    def _perform_scraping(self, data, content_type, scrapers):
        """Perform the actual scraping in a separate thread"""
        try:
            # Import cocoscrapers functions
            if content_type == 'movie':
                # Use cocoscrapers movie scraping function
                self.sources = self.cocoscrapers.scrape_movie(data, scrapers)
            else:
                # Use cocoscrapers episode scraping function  
                self.sources = self.cocoscrapers.scrape_episode(data, scrapers)
        except Exception as e:
            xbmc.log(f"MovieStream: Scraping thread error: {str(e)}", xbmc.LOGERROR)
            self.sources = []
    
    def _get_enabled_scrapers(self):
        """Get list of enabled scrapers"""
        try:
            # Get all available scrapers from cocoscrapers
            if hasattr(self.cocoscrapers, 'relevant_scrapers'):
                all_scrapers = self.cocoscrapers.relevant_scrapers()
            elif hasattr(self.cocoscrapers, 'get_scrapers'):
                all_scrapers = self.cocoscrapers.get_scrapers()
            else:
                # Fallback - return empty list if method not found
                xbmc.log("MovieStream: No scraper method found in cocoscrapers", xbmc.LOGWARNING)
                return []
            
            # Filter enabled scrapers (you can add settings for this)
            enabled_scrapers = []
            
            for scraper in all_scrapers:
                # Check if scraper is enabled (default: enable all)
                if self._is_scraper_enabled(scraper):
                    enabled_scrapers.append(scraper)
            
            return enabled_scrapers
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error getting scrapers: {str(e)}", xbmc.LOGERROR)
            return []
    
    def _is_scraper_enabled(self, scraper):
        """Check if a scraper is enabled"""
        # You can add addon settings for individual scrapers
        # For now, enable all scrapers
        return True
    
    def _filter_sources(self, sources):
        """Filter and sort sources by quality and reliability"""
        if not sources:
            return []
        
        try:
            # Filter out invalid sources
            valid_sources = []
            
            for source in sources:
                if self._is_valid_source(source):
                    valid_sources.append(source)
            
            # Sort by quality and other factors
            sorted_sources = sorted(valid_sources, key=self._source_sort_key, reverse=True)
            
            # Limit number of sources
            max_sources = int(self.addon.getSetting('max_sources') or '20')
            return sorted_sources[:max_sources]
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error filtering sources: {str(e)}", xbmc.LOGERROR)
            return sources
    
    def _is_valid_source(self, source):
        """Check if a source is valid"""
        try:
            # Basic validation
            if not source.get('url'):
                return False
            
            # Check quality filter
            quality_filter = self.addon.getSetting('quality_filter') or 'all'
            if quality_filter != 'all':
                source_quality = source.get('quality', '').lower()
                if quality_filter not in source_quality:
                    return False
            
            return True
            
        except:
            return False
    
    def _source_sort_key(self, source):
        """Generate sort key for source ranking"""
        try:
            score = 0
            
            # Quality scoring
            quality = source.get('quality', '').lower()
            if '4k' in quality or '2160p' in quality:
                score += 100
            elif '1080p' in quality:
                score += 80
            elif '720p' in quality:
                score += 60
            elif '480p' in quality:
                score += 40
            
            # Provider scoring (you can customize this)
            provider = source.get('provider', '').lower()
            if 'premium' in provider:
                score += 20
            
            # Direct link bonus
            if source.get('direct', False):
                score += 10
            
            return score
            
        except:
            return 0
    
    def show_source_selection(self, sources, title):
        """Show source selection dialog"""
        if not sources:
            xbmcgui.Dialog().notification('MovieStream', 'No sources found', xbmcgui.NOTIFICATION_WARNING)
            return None
        
        try:
            # Prepare source list for dialog
            source_labels = []
            
            for i, source in enumerate(sources):
                provider = source.get('provider', 'Unknown')
                quality = source.get('quality', 'Unknown')
                size = source.get('size', '')
                
                # Format label
                label = f"{provider} - {quality}"
                if size:
                    label += f" ({size})"
                
                # Add source info
                info = source.get('info', [])
                if info:
                    label += f" [{', '.join(info)}]"
                
                source_labels.append(label)
            
            # Show selection dialog
            dialog = xbmcgui.Dialog()
            selected = dialog.select(f'Select source for: {title}', source_labels)
            
            if selected >= 0:
                return sources[selected]
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error showing source selection: {str(e)}", xbmc.LOGERROR)
        
        return None
    
    def resolve_source(self, source):
        """Resolve a source to get playable URL"""
        try:
            if not source or not source.get('url'):
                return None
            
            # Show resolving dialog
            progress = xbmcgui.DialogProgress()
            progress.create('MovieStream', 'Resolving source...')
            
            try:
                # Use cocoscrapers to resolve the source
                resolved_url = self.cocoscrapers.resolve_url(source['url'])
                
                progress.close()
                
                if resolved_url:
                    xbmc.log(f"MovieStream: Source resolved successfully", xbmc.LOGINFO)
                    return resolved_url
                else:
                    xbmc.log("MovieStream: Failed to resolve source", xbmc.LOGWARNING)
                    return None
                    
            except Exception as e:
                progress.close()
                xbmc.log(f"MovieStream: Error resolving source: {str(e)}", xbmc.LOGERROR)
                return None
                
        except Exception as e:
            xbmc.log(f"MovieStream: General resolve error: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_scraper_stats(self):
        """Get statistics about available scrapers"""
        if not self.cocoscrapers_available:
            return {'available': False, 'scrapers': 0}
        
        try:
            scrapers = self._get_enabled_scrapers()
            return {
                'available': True,
                'total_scrapers': len(scrapers),
                'enabled_scrapers': len([s for s in scrapers if self._is_scraper_enabled(s)])
            }
        except:
            return {'available': False, 'scrapers': 0}