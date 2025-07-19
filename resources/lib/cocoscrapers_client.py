#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cocoscrapers Integration for MovieStream Kodi Addon
Handles movie/TV show source scraping with proper TMDB integration
"""

import xbmc
import xbmcaddon
import xbmcgui
import json
import threading
import time

class CocoScrapersClient:
    """Client for Cocoscrapers integration with TMDB"""
    
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
            try:
                # Try alternative import paths
                import script.module.cocoscrapers.lib.cocoscrapers as cocoscrapers
                self.cocoscrapers_available = True
                self.cocoscrapers = cocoscrapers
                xbmc.log("MovieStream: Cocoscrapers module loaded via alternative path", xbmc.LOGINFO)
            except ImportError:
                xbmc.log("MovieStream: Cocoscrapers module not found", xbmc.LOGWARNING)
                self.cocoscrapers_available = False
    
    def is_available(self):
        """Check if cocoscrapers is available"""
        return self.cocoscrapers_available
    
    def scrape_movie_sources(self, title, year, imdb_id=None, tmdb_id=None):
        """Scrape sources for a movie using TMDB data"""
        if not self.cocoscrapers_available:
            xbmc.log("MovieStream: Cocoscrapers not available for movie scraping", xbmc.LOGWARNING)
            return []
        
        try:
            # Prepare movie data for cocoscrapers with enhanced TMDB info
            movie_data = {
                'title': title,
                'originaltitle': title,
                'year': str(year) if year else '',
                'imdb': str(imdb_id) if imdb_id else '',
                'tmdb': str(tmdb_id) if tmdb_id else '',
                'mediatype': 'movie'
            }
            
            xbmc.log(f"MovieStream: Scraping sources for movie: {title} ({year}) - TMDB: {tmdb_id}, IMDB: {imdb_id}", xbmc.LOGINFO)
            
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
        """Scrape sources for a TV episode using TMDB data"""
        if not self.cocoscrapers_available:
            xbmc.log("MovieStream: Cocoscrapers not available for episode scraping", xbmc.LOGWARNING)
            return []
        
        try:
            # Prepare episode data for cocoscrapers with enhanced TMDB info
            episode_data = {
                'tvshowtitle': title,
                'title': title,
                'originaltitle': title,
                'year': str(year) if year else '',
                'season': str(season),
                'episode': str(episode),
                'imdb': str(imdb_id) if imdb_id else '',
                'tmdb': str(tmdb_id) if tmdb_id else '',
                'tvdb': str(tvdb_id) if tvdb_id else '',
                'mediatype': 'episode'
            }
            
            xbmc.log(f"MovieStream: Scraping sources for episode: {title} S{season}E{episode} - TMDB: {tmdb_id}", xbmc.LOGINFO)
            
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
            # Get scraping timeout from settings
            timeout = int(self.addon.getSetting('scraper_timeout') or '40')
            
            # Thread for scraping
            scrape_thread = threading.Thread(
                target=self._perform_scraping,
                args=(data, content_type)
            )
            scrape_thread.daemon = True
            scrape_thread.start()
            
            # Progress monitoring
            start_time = time.time()
            
            while scrape_thread.is_alive():
                if progress.iscanceled():
                    xbmc.log("MovieStream: Scraping cancelled by user", xbmc.LOGINFO)
                    break
                
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    xbmc.log("MovieStream: Scraping timeout reached", xbmc.LOGINFO)
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
    
    def _perform_scraping(self, data, content_type):
        """Perform the actual scraping in a separate thread"""
        try:
            sources = []
            
            if content_type == 'movie':
                # Use cocoscrapers movie scraping
                if hasattr(self.cocoscrapers, 'scrape_movie'):
                    sources = self.cocoscrapers.scrape_movie(data)
                elif hasattr(self.cocoscrapers, 'scrapeMovie'):
                    sources = self.cocoscrapers.scrapeMovie(data)
                else:
                    # Try generic scrape method
                    if hasattr(self.cocoscrapers, 'scrape'):
                        sources = self.cocoscrapers.scrape(data, 'movie')
            else:
                # Use cocoscrapers episode scraping  
                if hasattr(self.cocoscrapers, 'scrape_episode'):
                    sources = self.cocoscrapers.scrape_episode(data)
                elif hasattr(self.cocoscrapers, 'scrapeEpisode'):
                    sources = self.cocoscrapers.scrapeEpisode(data)
                else:
                    # Try generic scrape method
                    if hasattr(self.cocoscrapers, 'scrape'):
                        sources = self.cocoscrapers.scrape(data, 'episode')
            
            # Ensure sources is a list
            if not isinstance(sources, list):
                sources = []
            
            self.sources = sources
            xbmc.log(f"MovieStream: Scraping completed, found {len(sources)} raw sources", xbmc.LOGINFO)
            
        except Exception as e:
            xbmc.log(f"MovieStream: Scraping thread error: {str(e)}", xbmc.LOGERROR)
            self.sources = []
    
    def _filter_sources(self, sources):
        """Filter and sort sources by quality and reliability"""
        if not sources:
            xbmc.log("MovieStream: No sources to filter", xbmc.LOGINFO)
            return []
        
        try:
            # Filter out invalid sources
            valid_sources = []
            
            for source in sources:
                if self._is_valid_source(source):
                    valid_sources.append(source)
            
            xbmc.log(f"MovieStream: {len(valid_sources)} valid sources after filtering", xbmc.LOGINFO)
            
            # Sort by quality and other factors
            sorted_sources = sorted(valid_sources, key=self._source_sort_key, reverse=True)
            
            # Limit number of sources
            max_sources = int(self.addon.getSetting('max_sources') or '25')
            return sorted_sources[:max_sources]
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error filtering sources: {str(e)}", xbmc.LOGERROR)
            return sources
    
    def _is_valid_source(self, source):
        """Check if a source is valid"""
        try:
            # Basic validation
            if not isinstance(source, dict):
                return False
                
            if not source.get('url') and not source.get('source'):
                return False
            
            # Get the URL from either 'url' or 'source' field
            url = source.get('url') or source.get('source', '')
            if not url or len(url) < 10:
                return False
            
            # Check quality filter
            quality_filter = self.addon.getSetting('quality_filter') or 'all'
            if quality_filter != 'all':
                source_quality = source.get('quality', '').lower()
                if quality_filter.lower() not in source_quality and source_quality != '':
                    return False
            
            return True
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error validating source: {str(e)}", xbmc.LOGERROR)
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
            else:
                score += 20  # Default score for unknown quality
            
            # Provider scoring
            provider = source.get('provider', '').lower()
            if any(premium in provider for premium in ['premium', 'debrid', 'cached']):
                score += 50
            
            # Direct link bonus
            if source.get('direct', False) or source.get('type') == 'direct':
                score += 30
            
            # Seeders bonus for torrents
            if 'seeders' in source:
                seeders = int(source.get('seeders', 0))
                score += min(seeders, 50)  # Cap at 50 bonus points
            
            return score
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error calculating source score: {str(e)}", xbmc.LOGERROR)
            return 0
    
    def show_source_selection(self, sources, title):
        """Show source selection dialog"""
        if not sources:
            xbmcgui.Dialog().notification('MovieStream', 'No sources found', xbmcgui.NOTIFICATION_WARNING)
            return None
        
        try:
            # Prepare source list for dialog
            source_labels = []
            
            for source in sources:
                provider = source.get('provider', 'Unknown')
                quality = source.get('quality', 'Unknown')
                size = source.get('size', '')
                
                # Format label
                label = f"[COLOR yellow]{provider}[/COLOR] - [COLOR lime]{quality}[/COLOR]"
                if size:
                    label += f" [COLOR white]({size})[/COLOR]"
                
                # Add additional info
                if source.get('seeders'):
                    label += f" [COLOR orange]S:{source['seeders']}[/COLOR]"
                
                if source.get('direct', False):
                    label += " [COLOR cyan][DIRECT][/COLOR]"
                
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
            if not source:
                return None
            
            # Get URL from source
            url = source.get('url') or source.get('source', '')
            if not url:
                xbmc.log("MovieStream: No URL found in source", xbmc.LOGWARNING)
                return None
            
            # Show resolving dialog
            progress = xbmcgui.DialogProgress()
            progress.create('MovieStream', 'Resolving source...')
            progress.update(0)
            
            try:
                resolved_url = url
                
                # If source needs resolving
                if not source.get('direct', False):
                    progress.update(50, 'Resolving URL...')
                    
                    # Try different resolve methods
                    if hasattr(self.cocoscrapers, 'resolve_url'):
                        resolved_url = self.cocoscrapers.resolve_url(url)
                    elif hasattr(self.cocoscrapers, 'resolve'):
                        resolved_url = self.cocoscrapers.resolve(url)
                    else:
                        # Try using resolveurl module directly
                        try:
                            import resolveurl
                            if resolveurl.HostedMediaFile(url).valid_url():
                                resolved_url = resolveurl.resolve(url)
                        except:
                            pass
                
                progress.update(100)
                progress.close()
                
                if resolved_url and resolved_url != url:
                    xbmc.log(f"MovieStream: Source resolved successfully", xbmc.LOGINFO)
                    return resolved_url
                elif resolved_url:
                    xbmc.log(f"MovieStream: Using direct URL", xbmc.LOGINFO)
                    return resolved_url
                else:
                    xbmc.log("MovieStream: Failed to resolve source", xbmc.LOGWARNING)
                    return None
                    
            except Exception as e:
                progress.close()
                xbmc.log(f"MovieStream: Error resolving source: {str(e)}", xbmc.LOGERROR)
                return url  # Return original URL as fallback
                
        except Exception as e:
            xbmc.log(f"MovieStream: General resolve error: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_scraper_stats(self):
        """Get statistics about available scrapers"""
        if not self.cocoscrapers_available:
            return {'available': False, 'total_scrapers': 0, 'enabled_scrapers': 0}
        
        try:
            # Try to get scraper count
            scraper_count = 0
            if hasattr(self.cocoscrapers, 'getScrapeModules'):
                modules = self.cocoscrapers.getScrapeModules()
                scraper_count = len(modules) if modules else 0
            elif hasattr(self.cocoscrapers, 'relevant_scrapers'):
                modules = self.cocoscrapers.relevant_scrapers()
                scraper_count = len(modules) if modules else 0
            
            return {
                'available': True,
                'total_scrapers': scraper_count,
                'enabled_scrapers': scraper_count
            }
        except Exception as e:
            xbmc.log(f"MovieStream: Error getting scraper stats: {str(e)}", xbmc.LOGERROR)
            return {'available': True, 'total_scrapers': 0, 'enabled_scrapers': 0}
