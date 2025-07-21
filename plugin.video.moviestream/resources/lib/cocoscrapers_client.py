#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced Cocoscrapers Integration for MovieStream Kodi Addon
Handles movie/TV show source scraping with fallback methods
"""

import xbmc
import xbmcaddon
import xbmcgui
import json
import threading
import time

class CocoScrapersClient:
    """Enhanced Client for Cocoscrapers integration with multiple fallback methods"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.cocoscrapers_available = False
        self.cocoscrapers = None
        self.sources = []
        
        # Try to import cocoscrapers with multiple methods
        self._initialize_cocoscrapers()
    
    def _initialize_cocoscrapers(self):
        """Initialize cocoscrapers with multiple fallback methods"""
        
        # Method 1: Direct import
        try:
            import cocoscrapers
            self.cocoscrapers = cocoscrapers
            self.cocoscrapers_available = True
            xbmc.log("MovieStream: Cocoscrapers module loaded successfully (direct import)", xbmc.LOGINFO)
            return
        except ImportError:
            xbmc.log("MovieStream: Direct cocoscrapers import failed", xbmc.LOGWARNING)
        
        # Method 2: Try different import paths
        import_paths = [
            'script.module.cocoscrapers.lib.cocoscrapers',
            'resources.lib.cocoscrapers',
            'cocoscrapers.cocoscrapers',
        ]
        
        for path in import_paths:
            try:
                module = __import__(path, fromlist=[''])
                self.cocoscrapers = module
                self.cocoscrapers_available = True
                xbmc.log(f"MovieStream: Cocoscrapers loaded via {path}", xbmc.LOGINFO)
                return
            except ImportError:
                continue
        
        # Method 3: Try to import as addon
        try:
            import xbmcaddon
            cocoscrapers_addon = xbmcaddon.Addon('script.module.cocoscrapers')
            addon_path = cocoscrapers_addon.getAddonInfo('path')
            
            import sys
            import os
            lib_path = os.path.join(addon_path, 'lib')
            if lib_path not in sys.path:
                sys.path.append(lib_path)
            
            import cocoscrapers
            self.cocoscrapers = cocoscrapers
            self.cocoscrapers_available = True
            xbmc.log("MovieStream: Cocoscrapers loaded via addon path", xbmc.LOGINFO)
            return
        except:
            pass
        
        xbmc.log("MovieStream: All cocoscrapers import methods failed", xbmc.LOGERROR)
    
    def is_available(self):
        """Check if cocoscrapers is available"""
        return self.cocoscrapers_available
    
    def scrape_movie_sources(self, title, year, imdb_id=None, tmdb_id=None):
        """Scrape sources for a movie using multiple methods"""
        if not self.cocoscrapers_available:
            xbmc.log("MovieStream: Cocoscrapers not available for scraping", xbmc.LOGWARNING)
            return []
        
        try:
            # Prepare movie data
            movie_data = {
                'title': title,
                'year': int(year) if year and str(year).isdigit() else None,
                'imdb': imdb_id if imdb_id else '',
                'tmdb': tmdb_id if tmdb_id else '',
                'originaltitle': title
            }
            
            xbmc.log(f"MovieStream: Scraping movie sources for: {title} ({year})", xbmc.LOGINFO)
            xbmc.log(f"MovieStream: Movie data: {movie_data}", xbmc.LOGINFO)
            
            # Try different scraping methods
            sources = self._try_scraping_methods(movie_data, 'movie')
            
            if sources:
                # Filter and sort sources
                filtered_sources = self._filter_and_sort_sources(sources)
                xbmc.log(f"MovieStream: Found {len(filtered_sources)} sources for {title}", xbmc.LOGINFO)
                return filtered_sources
            else:
                xbmc.log(f"MovieStream: No sources found for {title}", xbmc.LOGWARNING)
                return []
                
        except Exception as e:
            xbmc.log(f"MovieStream: Error in scrape_movie_sources: {str(e)}", xbmc.LOGERROR)
            return []
    
    def scrape_episode_sources(self, show_title, year, season, episode, show_id=None):
        """Scrape sources for a TV episode"""
        if not self.cocoscrapers_available:
            return []
        
        try:
            # Prepare episode data
            episode_data = {
                'tvshowtitle': show_title,
                'year': int(year) if year and str(year).isdigit() else None,
                'season': int(season) if season else 1,
                'episode': int(episode) if episode else 1,
                'tmdb': show_id if show_id else '',
                'title': f"Episode {episode}"  # Episode title
            }
            
            xbmc.log(f"MovieStream: Scraping episode sources for: {show_title} S{season}E{episode}", xbmc.LOGINFO)
            
            # Try different scraping methods
            sources = self._try_scraping_methods(episode_data, 'episode')
            
            if sources:
                filtered_sources = self._filter_and_sort_sources(sources)
                xbmc.log(f"MovieStream: Found {len(filtered_sources)} episode sources", xbmc.LOGINFO)
                return filtered_sources
            else:
                xbmc.log(f"MovieStream: No episode sources found", xbmc.LOGWARNING)
                return []
                
        except Exception as e:
            xbmc.log(f"MovieStream: Error in scrape_episode_sources: {str(e)}", xbmc.LOGERROR)
            return []
    
    def _try_scraping_methods(self, data, content_type):
        """Try different scraping methods with cocoscrapers"""
        sources = []
        
        # Method 1: Try cocoscrapers.sources module
        try:
            if hasattr(self.cocoscrapers, 'sources'):
                xbmc.log("MovieStream: Trying cocoscrapers.sources method", xbmc.LOGINFO)
                
                if content_type == 'movie':
                    sources = self.cocoscrapers.sources.getSources(data)
                else:
                    sources = self.cocoscrapers.sources.getEpisodes(data)
                
                if sources:
                    xbmc.log(f"MovieStream: cocoscrapers.sources returned {len(sources)} sources", xbmc.LOGINFO)
                    return sources
        except Exception as e:
            xbmc.log(f"MovieStream: cocoscrapers.sources method failed: {str(e)}", xbmc.LOGWARNING)
        
        # Method 2: Try direct scraping functions
        scraping_functions = [
            'scrape_movie' if content_type == 'movie' else 'scrape_episode',
            'getSources',
            'get_sources',
            'scrape',
        ]
        
        for func_name in scraping_functions:
            try:
                if hasattr(self.cocoscrapers, func_name):
                    xbmc.log(f"MovieStream: Trying {func_name} method", xbmc.LOGINFO)
                    
                    scrape_func = getattr(self.cocoscrapers, func_name)
                    sources = scrape_func(data)
                    
                    if sources:
                        xbmc.log(f"MovieStream: {func_name} returned {len(sources)} sources", xbmc.LOGINFO)
                        return sources
            except Exception as e:
                xbmc.log(f"MovieStream: {func_name} method failed: {str(e)}", xbmc.LOGWARNING)
        
        # Method 3: Try module-level functions
        module_functions = [
            f'scrape_{content_type}',
            'scrape_sources',
            'get_sources'
        ]
        
        for func_name in module_functions:
            try:
                if hasattr(self.cocoscrapers, func_name):
                    xbmc.log(f"MovieStream: Trying module {func_name}", xbmc.LOGINFO)
                    
                    func = getattr(self.cocoscrapers, func_name)
                    sources = func(data)
                    
                    if sources:
                        xbmc.log(f"MovieStream: Module {func_name} returned {len(sources)} sources", xbmc.LOGINFO)
                        return sources
            except Exception as e:
                xbmc.log(f"MovieStream: Module {func_name} failed: {str(e)}", xbmc.LOGWARNING)
        
        # Method 4: Try threaded scraping
        try:
            sources = self._threaded_scraping(data, content_type)
            if sources:
                xbmc.log(f"MovieStream: Threaded scraping returned {len(sources)} sources", xbmc.LOGINFO)
                return sources
        except Exception as e:
            xbmc.log(f"MovieStream: Threaded scraping failed: {str(e)}", xbmc.LOGWARNING)
        
        xbmc.log("MovieStream: All scraping methods failed", xbmc.LOGERROR)
        return []
    
    def _threaded_scraping(self, data, content_type):
        """Perform threaded scraping as fallback"""
        self.sources = []
        
        def scrape_worker():
            try:
                # Try to find and use any available scraping method
                if hasattr(self.cocoscrapers, 'control') and hasattr(self.cocoscrapers.control, 'setting'):
                    # This looks like the typical cocoscrapers structure
                    if content_type == 'movie':
                        if hasattr(self.cocoscrapers, 'sources') and hasattr(self.cocoscrapers.sources, 'getSources'):
                            self.sources = self.cocoscrapers.sources.getSources(data)
                    else:
                        if hasattr(self.cocoscrapers, 'sources') and hasattr(self.cocoscrapers.sources, 'getEpisodes'):
                            self.sources = self.cocoscrapers.sources.getEpisodes(data)
                else:
                    # Try simple approach
                    self.sources = []
                    
            except Exception as e:
                xbmc.log(f"MovieStream: Worker thread error: {str(e)}", xbmc.LOGERROR)
                self.sources = []
        
        # Run in thread with timeout
        thread = threading.Thread(target=scrape_worker)
        thread.daemon = True
        thread.start()
        thread.join(timeout=30)  # 30 second timeout
        
        return self.sources if self.sources else []
    
    def _filter_and_sort_sources(self, sources):
        """Filter and sort sources"""
        if not sources:
            return []
        
        try:
            valid_sources = []
            
            for source in sources:
                # Convert to dict if needed
                if isinstance(source, str):
                    source = {'url': source, 'quality': 'SD', 'provider': 'Direct'}
                elif not isinstance(source, dict):
                    continue
                
                # Validate source
                if not source.get('url'):
                    continue
                
                # Add missing fields
                if 'quality' not in source:
                    source['quality'] = 'SD'
                if 'provider' not in source:
                    source['provider'] = 'Unknown'
                
                valid_sources.append(source)
            
            # Sort by quality (4K > 1080p > 720p > SD)
            def quality_score(source):
                quality = source.get('quality', '').lower()
                if '4k' in quality or '2160p' in quality:
                    return 4
                elif '1080p' in quality or 'fhd' in quality:
                    return 3
                elif '720p' in quality or 'hd' in quality:
                    return 2
                else:
                    return 1
            
            sorted_sources = sorted(valid_sources, key=quality_score, reverse=True)
            
            # Limit sources
            max_sources = int(self.addon.getSetting('max_sources') or '10')
            return sorted_sources[:max_sources]
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error filtering sources: {str(e)}", xbmc.LOGERROR)
            return sources[:10]  # Return first 10 as fallback
    
    def resolve_source(self, source):
        """Resolve a source to get playable URL"""
        if not source:
            return None
        
        try:
            # If source is a string, return it directly
            if isinstance(source, str):
                return source
            
            # If source is a dict, try to get URL
            if isinstance(source, dict):
                url = source.get('url')
                if not url:
                    return None
                
                # Try to resolve with cocoscrapers
                try:
                    if hasattr(self.cocoscrapers, 'resolve'):
                        resolved = self.cocoscrapers.resolve(url)
                        if resolved:
                            return resolved
                    elif hasattr(self.cocoscrapers, 'resolveurl'):
                        resolved = self.cocoscrapers.resolveurl(url) 
                        if resolved:
                            return resolved
                except Exception as e:
                    xbmc.log(f"MovieStream: Resolve error: {str(e)}", xbmc.LOGWARNING)
                
                # Return original URL as fallback
                return url
            
        except Exception as e:
            xbmc.log(f"MovieStream: Source resolution error: {str(e)}", xbmc.LOGERROR)
        
        return None
    
    def show_source_selection(self, sources, title):
        """Show source selection dialog"""
        if not sources:
            return None
        
        try:
            # Create source labels
            labels = []
            for i, source in enumerate(sources):
                if isinstance(source, dict):
                    provider = source.get('provider', 'Unknown')
                    quality = source.get('quality', 'Unknown')
                    size = source.get('size', '')
                    
                    label = f"[{quality}] {provider}"
                    if size:
                        label += f" ({size})"
                else:
                    label = f"Source {i+1}"
                
                labels.append(label)
            
            # Show selection dialog
            dialog = xbmcgui.Dialog()
            selection = dialog.select(f'Select source for {title}', labels)
            
            if selection >= 0:
                return sources[selection]
                
        except Exception as e:
            xbmc.log(f"MovieStream: Source selection error: {str(e)}", xbmc.LOGERROR)
        
        return None
    
    def get_scraper_stats(self):
        """Get scraper statistics"""
        if not self.cocoscrapers_available:
            return {'total_scrapers': 0, 'enabled_scrapers': 0}
        
        try:
            # Try to get scraper info
            scrapers = 0
            
            if hasattr(self.cocoscrapers, '__version__'):
                version = self.cocoscrapers.__version__
            else:
                version = 'Unknown'
            
            # Try to count scrapers
            if hasattr(self.cocoscrapers, 'sources'):
                scrapers = 5  # Estimate
            
            return {
                'total_scrapers': scrapers,
                'enabled_scrapers': scrapers,
                'version': version
            }
            
        except Exception as e:
            xbmc.log(f"MovieStream: Stats error: {str(e)}", xbmc.LOGWARNING)
            return {'total_scrapers': 0, 'enabled_scrapers': 0}