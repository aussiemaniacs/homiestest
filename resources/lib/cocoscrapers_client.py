#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cocoscrapers Integration for MovieStream Kodi Addon
Fixed version with proper TMDB integration and scraping
"""

import xbmc
import xbmcaddon
import xbmcgui
import json
import threading
import time

class CocoScrapersClient:
    """Client for Cocoscrapers integration with proper scraping"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.cocoscrapers_available = False
        self.sources = []
        
        # Try multiple import methods for Cocoscrapers
        try:
            # Method 1: Direct import
            import cocoscrapers
            self.cocoscrapers = cocoscrapers
            self.cocoscrapers_available = True
            xbmc.log("MovieStream: Cocoscrapers loaded via direct import", xbmc.LOGINFO)
        except ImportError:
            try:
                # Method 2: Module path import
                from script.module.cocoscrapers.lib import cocoscrapers
                self.cocoscrapers = cocoscrapers
                self.cocoscrapers_available = True
                xbmc.log("MovieStream: Cocoscrapers loaded via module path", xbmc.LOGINFO)
            except ImportError:
                try:
                    # Method 3: Alternative import
                    import script.module.cocoscrapers.lib.cocoscrapers as cocoscrapers
                    self.cocoscrapers = cocoscrapers
                    self.cocoscrapers_available = True
                    xbmc.log("MovieStream: Cocoscrapers loaded via alternative import", xbmc.LOGINFO)
                except ImportError:
                    xbmc.log("MovieStream: Cocoscrapers module not found - install script.module.cocoscrapers", xbmc.LOGWARNING)
                    self.cocoscrapers_available = False
    
    def is_available(self):
        """Check if cocoscrapers is available"""
        return self.cocoscrapers_available
    
    def scrape_movie_sources(self, title, year, imdb_id=None, tmdb_id=None):
        """Scrape sources for a movie with proper data formatting"""
        if not self.cocoscrapers_available:
            xbmc.log("MovieStream: Cocoscrapers not available for movie scraping", xbmc.LOGWARNING)
            return []
        
        try:
            # Clean and prepare movie data for cocoscrapers
            movie_data = {
                'title': str(title).strip(),
                'originaltitle': str(title).strip(),
                'year': str(year).strip() if year else '',
                'imdb': str(imdb_id).strip() if imdb_id else '',
                'tmdb': str(tmdb_id).strip() if tmdb_id else '',
                'mediatype': 'movie'
            }
            
            # Remove empty values
            movie_data = {k: v for k, v in movie_data.items() if v}
            
            xbmc.log(f"MovieStream: Starting movie scraping for: {title} ({year})", xbmc.LOGINFO)
            xbmc.log(f"MovieStream: Movie data: {json.dumps(movie_data)}", xbmc.LOGDEBUG)
            
            # Start scraping with progress dialog
            sources = self._scrape_with_progress(movie_data, 'movie')
            
            # Filter and sort sources
            filtered_sources = self._filter_sources(sources)
            
            xbmc.log(f"MovieStream: Scraping completed. Found {len(filtered_sources)} sources for {title}", xbmc.LOGINFO)
            return filtered_sources
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error scraping movie sources for {title}: {str(e)}", xbmc.LOGERROR)
            return []
    
    def scrape_episode_sources(self, title, year, season, episode, imdb_id=None, tmdb_id=None, tvdb_id=None):
        """Scrape sources for a TV episode with proper data formatting"""
        if not self.cocoscrapers_available:
            xbmc.log("MovieStream: Cocoscrapers not available for episode scraping", xbmc.LOGWARNING)
            return []
        
        try:
            # Clean and prepare episode data for cocoscrapers
            episode_data = {
                'tvshowtitle': str(title).strip(),
                'title': str(title).strip(),
                'originaltitle': str(title).strip(),
                'year': str(year).strip() if year else '',
                'season': str(season).strip(),
                'episode': str(episode).strip(),
                'imdb': str(imdb_id).strip() if imdb_id else '',
                'tmdb': str(tmdb_id).strip() if tmdb_id else '',
                'tvdb': str(tvdb_id).strip() if tvdb_id else '',
                'mediatype': 'episode'
            }
            
            # Remove empty values
            episode_data = {k: v for k, v in episode_data.items() if v}
            
            xbmc.log(f"MovieStream: Starting episode scraping for: {title} S{season}E{episode}", xbmc.LOGINFO)
            xbmc.log(f"MovieStream: Episode data: {json.dumps(episode_data)}", xbmc.LOGDEBUG)
            
            # Start scraping with progress dialog
            sources = self._scrape_with_progress(episode_data, 'episode')
            
            # Filter and sort sources
            filtered_sources = self._filter_sources(sources)
            
            xbmc.log(f"MovieStream: Episode scraping completed. Found {len(filtered_sources)} sources for {title} S{season}E{episode}", xbmc.LOGINFO)
            return filtered_sources
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error scraping episode sources for {title}: {str(e)}", xbmc.LOGERROR)
            return []
    
    def _scrape_with_progress(self, data, content_type):
        """Scrape sources with progress dialog"""
        
        # Initialize progress dialog
        progress = xbmcgui.DialogProgress()
        progress.create('MovieStream - Finding Sources', 'Initializing scrapers...')
        progress.update(0)
        
        sources = []
        self.sources = []  # Reset sources list
        
        try:
            # Get scraping timeout from settings
            timeout = int(self.addon.getSetting('scraper_timeout') or '30')
            
            # Thread for scraping
            scrape_thread = threading.Thread(
                target=self._perform_scraping,
                args=(data, content_type)
            )
            scrape_thread.daemon = True
            scrape_thread.start()
            
            # Progress monitoring with better feedback
            start_time = time.time()
            last_count = 0
            
            while scrape_thread.is_alive():
                if progress.iscanceled():
                    xbmc.log("MovieStream: Scraping cancelled by user", xbmc.LOGINFO)
                    break
                
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    xbmc.log(f"MovieStream: Scraping timeout after {timeout} seconds", xbmc.LOGINFO)
                    break
                
                # Update progress with more details
                current_count = len(self.sources)
                percent = min(int((elapsed / timeout) * 100), 95)
                
                if current_count != last_count:
                    progress.update(percent, f'Found {current_count} sources...')
                    last_count = current_count
                else:
                    progress.update(percent, f'Searching... ({int(elapsed)}s)')
                
                xbmc.sleep(500)
            
            # Wait a moment for thread to finish
            progress.update(100, 'Finalizing results...')
            time.sleep(0.5)
            
            sources = self.sources.copy()
            
        except Exception as e:
            xbmc.log(f"MovieStream: Scraping progress error: {str(e)}", xbmc.LOGERROR)
        
        finally:
            progress.close()
        
        return sources
    
    def _perform_scraping(self, data, content_type):
        """Perform the actual scraping in a separate thread"""
        try:
            sources = []
            
            xbmc.log(f"MovieStream: Starting {content_type} scraping thread", xbmc.LOGDEBUG)
            
            if content_type == 'movie':
                # Try different Cocoscrapers movie methods
                if hasattr(self.cocoscrapers, 'scrape_movie'):
                    xbmc.log("MovieStream: Using cocoscrapers.scrape_movie", xbmc.LOGDEBUG)
                    sources = self.cocoscrapers.scrape_movie(data)
                elif hasattr(self.cocoscrapers, 'scrapeMovie'):
                    xbmc.log("MovieStream: Using cocoscrapers.scrapeMovie", xbmc.LOGDEBUG)
                    sources = self.cocoscrapers.scrapeMovie(data)
                elif hasattr(self.cocoscrapers, 'getSources'):
                    xbmc.log("MovieStream: Using cocoscrapers.getSources for movie", xbmc.LOGDEBUG)
                    sources = self.cocoscrapers.getSources(data, [], [], [], [])
                else:
                    xbmc.log("MovieStream: No suitable movie scraping method found", xbmc.LOGWARNING)
                    
            elif content_type == 'episode':
                # Try different Cocoscrapers episode methods
                if hasattr(self.cocoscrapers, 'scrape_episode'):
                    xbmc.log("MovieStream: Using cocoscrapers.scrape_episode", xbmc.LOGDEBUG)
                    sources = self.cocoscrapers.scrape_episode(data)
                elif hasattr(self.cocoscrapers, 'scrapeEpisode'):
                    xbmc.log("MovieStream: Using cocoscrapers.scrapeEpisode", xbmc.LOGDEBUG)
                    sources = self.cocoscrapers.scrapeEpisode(data)
                elif hasattr(self.cocoscrapers, 'getSources'):
                    xbmc.log("MovieStream: Using cocoscrapers.getSources for episode", xbmc.LOGDEBUG)
                    sources = self.cocoscrapers.getSources(data, [], [], [], [])
                else:
                    xbmc.log("MovieStream: No suitable episode scraping method found", xbmc.LOGWARNING)
            
            # Ensure sources is a list
            if not isinstance(sources, list):
                sources = []
            
            # Update sources progressively
            for source in sources:
                if isinstance(source, dict):
                    self.sources.append(source)
            
            xbmc.log(f"MovieStream: Scraping thread completed with {len(self.sources)} sources", xbmc.LOGINFO)
            
        except Exception as e:
            xbmc.log(f"MovieStream: Scraping thread error: {str(e)}", xbmc.LOGERROR)
            self.sources = []
    
    def _filter_sources(self, sources):
        """Filter and sort sources by quality and reliability"""
        if not sources:
            xbmc.log("MovieStream: No sources to filter", xbmc.LOGINFO)
            return []
        
        try:
            xbmc.log(f"MovieStream: Filtering {len(sources)} sources", xbmc.LOGDEBUG)
            
            # Filter out invalid sources
            valid_sources = []
            
            for i, source in enumerate(sources):
                try:
                    if self._is_valid_source(source):
                        valid_sources.append(source)
                    else:
                        xbmc.log(f"MovieStream: Filtered out invalid source {i}: {source.get('provider', 'Unknown')}", xbmc.LOGDEBUG)
                except Exception as e:
                    xbmc.log(f"MovieStream: Error validating source {i}: {str(e)}", xbmc.LOGWARNING)
            
            xbmc.log(f"MovieStream: {len(valid_sources)} valid sources after filtering", xbmc.LOGINFO)
            
            if not valid_sources:
                return []
            
            # Sort by quality and other factors
            try:
                sorted_sources = sorted(valid_sources, key=self._source_sort_key, reverse=True)
            except Exception as e:
                xbmc.log(f"MovieStream: Error sorting sources: {str(e)}", xbmc.LOGWARNING)
                sorted_sources = valid_sources
            
            # Limit number of sources
            max_sources = int(self.addon.getSetting('max_sources') or '20')
            final_sources = sorted_sources[:max_sources]
            
            xbmc.log(f"MovieStream: Returning {len(final_sources)} sources (limit: {max_sources})", xbmc.LOGINFO)
            return final_sources
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error filtering sources: {str(e)}", xbmc.LOGERROR)
            return sources[:20]  # Return first 20 as fallback
    
    def _is_valid_source(self, source):
        """Check if a source is valid"""
        try:
            # Basic validation
            if not isinstance(source, dict):
                return False
                
            # Must have a URL
            url = source.get('url') or source.get('source') or source.get('link')
            if not url or len(str(url).strip()) < 10:
                return False
            
            # Must have provider info
            provider = source.get('provider') or source.get('source')
            if not provider:
                return False
            
            # Check quality filter
            quality_filter = self.addon.getSetting('quality_filter') or 'all'
            if quality_filter != 'all':
                source_quality = str(source.get('quality', '')).lower()
                if quality_filter.lower() not in source_quality and source_quality:
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
            quality = str(source.get('quality', '')).lower()
            if '4k' in quality or '2160p' in quality:
                score += 1000
            elif '1080p' in quality:
                score += 800
            elif '720p' in quality:
                score += 600
            elif '480p' in quality:
                score += 400
            else:
                score += 200  # Default score for unknown quality
            
            # Provider scoring (prefer known good providers)
            provider = str(source.get('provider', '')).lower()
            if any(premium in provider for premium in ['premium', 'debrid', 'cached']):
                score += 500
            if any(good in provider for good in ['stream', 'direct', 'hd']):
                score += 300
            
            # Direct link bonus
            if source.get('direct', False) or source.get('type') == 'direct':
                score += 200
            
            # Seeders bonus for torrents
            try:
                seeders = int(source.get('seeders', 0))
                score += min(seeders, 100)  # Cap at 100 bonus points
            except:
                pass
            
            # Size bonus (prefer reasonable file sizes)
            try:
                size_str = str(source.get('size', ''))
                if 'gb' in size_str.lower():
                    # Prefer 1-5GB files
                    size_num = float(''.join(filter(str.isdigit, size_str.split('gb')[0])))
                    if 1 <= size_num <= 5:
                        score += 100
                    elif 0.5 <= size_num <= 8:
                        score += 50
            except:
                pass
            
            return score
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error calculating source score: {str(e)}", xbmc.LOGERROR)
            return 0
    
    def show_source_selection(self, sources, title):
        """Show source selection dialog with enhanced display"""
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
                
                # Format label with colors
                label = f"[COLOR yellow]{provider}[/COLOR]"
                
                if quality != 'Unknown':
                    if '1080p' in quality:
                        label += f" - [COLOR lime]{quality}[/COLOR]"
                    elif '720p' in quality:
                        label += f" - [COLOR orange]{quality}[/COLOR]"
                    else:
                        label += f" - [COLOR white]{quality}[/COLOR]"
                
                if size:
                    label += f" [COLOR cyan]({size})[/COLOR]"
                
                # Add additional info
                if source.get('seeders'):
                    label += f" [COLOR orange]Seeds:{source['seeders']}[/COLOR]"
                
                if source.get('direct', False):
                    label += " [COLOR springgreen][DIRECT][/COLOR]"
                
                if any(premium in provider.lower() for premium in ['premium', 'debrid', 'cached']):
                    label += " [COLOR gold][PREMIUM][/COLOR]"
                
                source_labels.append(label)
            
            # Show selection dialog
            dialog = xbmcgui.Dialog()
            selected = dialog.select(f'Select source for: {title}', source_labels)
            
            if selected >= 0:
                selected_source = sources[selected]
                xbmc.log(f"MovieStream: User selected source: {selected_source.get('provider', 'Unknown')}", xbmc.LOGINFO)
                return selected_source
            else:
                xbmc.log("MovieStream: User cancelled source selection", xbmc.LOGINFO)
            
        except Exception as e:
            xbmc.log(f"MovieStream: Error showing source selection: {str(e)}", xbmc.LOGERROR)
        
        return None
    
    def resolve_source(self, source):
        """Resolve a source to get playable URL with multiple methods"""
        try:
            if not source:
                return None
            
            # Get URL from source
            url = source.get('url') or source.get('source') or source.get('link')
            if not url:
                xbmc.log("MovieStream: No URL found in source", xbmc.LOGWARNING)
                return None
            
            provider = source.get('provider', 'Unknown')
            xbmc.log(f"MovieStream: Resolving source from {provider}: {str(url)[:100]}...", xbmc.LOGINFO)
            
            # Show resolving dialog
            progress = xbmcgui.DialogProgress()
            progress.create('MovieStream', f'Resolving {provider} source...')
            progress.update(0)
            
            try:
                resolved_url = url
                
                # If source needs resolving (not direct)
                if not source.get('direct', False):
                    progress.update(33, 'Resolving URL...')
                    
                    # Try different resolve methods
                    resolved = False
                    
                    # Method 1: Cocoscrapers resolve
                    if hasattr(self.cocoscrapers, 'resolve_url'):
                        try:
                            resolved_url = self.cocoscrapers.resolve_url(url)
                            if resolved_url and resolved_url != url:
                                resolved = True
                                xbmc.log("MovieStream: Resolved with cocoscrapers.resolve_url", xbmc.LOGDEBUG)
                        except Exception as e:
                            xbmc.log(f"MovieStream: cocoscrapers.resolve_url failed: {str(e)}", xbmc.LOGDEBUG)
                    
                    # Method 2: Cocoscrapers resolve (alternative)
                    if not resolved and hasattr(self.cocoscrapers, 'resolve'):
                        try:
                            progress.update(66, 'Trying alternative resolution...')
                            resolved_url = self.cocoscrapers.resolve(url)
                            if resolved_url and resolved_url != url:
                                resolved = True
                                xbmc.log("MovieStream: Resolved with cocoscrapers.resolve", xbmc.LOGDEBUG)
                        except Exception as e:
                            xbmc.log(f"MovieStream: cocoscrapers.resolve failed: {str(e)}", xbmc.LOGDEBUG)
                    
                    # Method 3: Try resolveurl module directly
                    if not resolved:
                        try:
                            progress.update(80, 'Trying resolveurl module...')
                            import resolveurl
                            if resolveurl.HostedMediaFile(url).valid_url():
                                resolved_url = resolveurl.resolve(url)
                                if resolved_url and resolved_url != url:
                                    resolved = True
                                    xbmc.log("MovieStream: Resolved with resolveurl module", xbmc.LOGDEBUG)
                        except Exception as e:
                            xbmc.log(f"MovieStream: resolveurl failed: {str(e)}", xbmc.LOGDEBUG)
                
                progress.update(100, 'Complete!')
                progress.close()
                
                if resolved_url:
                    if resolved_url != url:
                        xbmc.log(f"MovieStream: Source resolved successfully from {provider}", xbmc.LOGINFO)
                    else:
                        xbmc.log(f"MovieStream: Using direct URL from {provider}", xbmc.LOGINFO)
                    return resolved_url
                else:
                    xbmc.log(f"MovieStream: Failed to resolve source from {provider}", xbmc.LOGWARNING)
                    return None
                    
            except Exception as e:
                progress.close()
                xbmc.log(f"MovieStream: Error resolving source from {provider}: {str(e)}", xbmc.LOGERROR)
                return url  # Return original URL as fallback
                
        except Exception as e:
            xbmc.log(f"MovieStream: General resolve error: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_scraper_stats(self):
        """Get statistics about available scrapers"""
        if not self.cocoscrapers_available:
            return {'available': False, 'total_scrapers': 0, 'enabled_scrapers': 0}
        
        try:
            # Try to get scraper count from various methods
            scraper_count = 0
            
            if hasattr(self.cocoscrapers, 'getScrapeModules'):
                try:
                    modules = self.cocoscrapers.getScrapeModules()
                    scraper_count = len(modules) if modules else 0
                except:
                    pass
            
            if scraper_count == 0 and hasattr(self.cocoscrapers, 'relevant_scrapers'):
                try:
                    modules = self.cocoscrapers.relevant_scrapers()
                    scraper_count = len(modules) if modules else 0
                except:
                    pass
            
            # If still no count, assume it's working if module loaded
            if scraper_count == 0:
                scraper_count = 1  # At least the module is available
            
            return {
                'available': True,
                'total_scrapers': scraper_count,
                'enabled_scrapers': scraper_count
            }
        except Exception as e:
            xbmc.log(f"MovieStream: Error getting scraper stats: {str(e)}", xbmc.LOGERROR)
            return {'available': True, 'total_scrapers': 0, 'enabled_scrapers': 0}
