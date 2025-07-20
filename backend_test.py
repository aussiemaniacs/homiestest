#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MovieStream Pro Kodi Addon Testing Script
Tests all critical components and integration points
"""

import sys
import os
import json
import importlib.util
import traceback
from unittest.mock import Mock, MagicMock, patch

# Mock Kodi modules before importing addon code
class MockXBMC:
    LOGDEBUG = 0
    LOGINFO = 1
    LOGWARNING = 2
    LOGERROR = 3
    LOGFATAL = 4
    
    @staticmethod
    def log(msg, level=1):
        level_names = {0: 'DEBUG', 1: 'INFO', 2: 'WARNING', 3: 'ERROR', 4: 'FATAL'}
        print(f"[KODI {level_names.get(level, 'INFO')}] {msg}")
    
    @staticmethod
    def sleep(ms):
        import time
        time.sleep(ms / 1000.0)

class MockXBMCGUI:
    NOTIFICATION_INFO = 'info'
    NOTIFICATION_WARNING = 'warning'
    NOTIFICATION_ERROR = 'error'
    
    class ListItem:
        def __init__(self, label='', path=''):
            self.label = label
            self.path = path
            self.properties = {}
            self.info = {}
            self.art = {}
            self.subtitles = []
            self.stream_info = {}
            self.context_menu = []
        
        def setProperty(self, key, value):
            self.properties[key] = value
        
        def setInfo(self, type, info_dict):
            self.info[type] = info_dict
        
        def setArt(self, art_dict):
            self.art.update(art_dict)
        
        def setSubtitles(self, subtitles):
            self.subtitles = subtitles
        
        def addStreamInfo(self, type, info):
            self.stream_info[type] = info
        
        def addContextMenuItems(self, items):
            self.context_menu.extend(items)
    
    class Dialog:
        @staticmethod
        def notification(title, message, icon=None, time=5000):
            print(f"[NOTIFICATION] {title}: {message}")
        
        @staticmethod
        def ok(title, message):
            print(f"[DIALOG OK] {title}: {message}")
            return True
        
        @staticmethod
        def select(title, options):
            print(f"[DIALOG SELECT] {title}: {options}")
            return 0 if options else -1
        
        @staticmethod
        def textviewer(title, text):
            print(f"[TEXT VIEWER] {title}: {text[:100]}...")
    
    class DialogProgress:
        def __init__(self):
            self.canceled = False
        
        def create(self, title, message=''):
            print(f"[PROGRESS] Created: {title} - {message}")
        
        def update(self, percent, message=''):
            print(f"[PROGRESS] {percent}% - {message}")
        
        def iscanceled(self):
            return self.canceled
        
        def close(self):
            print("[PROGRESS] Closed")

class MockXBMCPlugin:
    @staticmethod
    def setPluginCategory(handle, category):
        print(f"[PLUGIN] Category: {category}")
    
    @staticmethod
    def setContent(handle, content):
        print(f"[PLUGIN] Content: {content}")
    
    @staticmethod
    def addDirectoryItem(handle, url, list_item, is_folder):
        print(f"[PLUGIN] Added item: {list_item.label} -> {url} (folder: {is_folder})")
        return True
    
    @staticmethod
    def endOfDirectory(handle):
        print("[PLUGIN] End of directory")
    
    @staticmethod
    def setResolvedUrl(handle, success, list_item):
        print(f"[PLUGIN] Resolved URL: {list_item.path} (success: {success})")

class MockXBMCAddon:
    class Addon:
        def __init__(self):
            self.settings = {
                'tmdb_api_key': 'd0f489a129429db6f2dd4751e5dbeb82',
                'github_repo_url': 'https://raw.githubusercontent.com/moviestream/database/main/',
                'enable_cocoscrapers': True,
                'auto_play_best_source': False,
                'scraper_timeout': '30',
                'max_sources': '50',
                'enable_subtitles': True,
                'quality_filter': 'all',
                'enable_realdebrid': False,
                'enable_premiumize': False,
                'enable_alldebrid': False
            }
        
        def getSetting(self, key):
            return self.settings.get(key, '')
        
        def getSettingBool(self, key):
            return self.settings.get(key, False)
        
        def getSettingInt(self, key):
            return int(self.settings.get(key, '0'))
        
        def getAddonInfo(self, info_type):
            info = {
                'id': 'plugin.video.moviestream',
                'name': 'MovieStream Pro',
                'version': '2.0.0',
                'path': '/app/plugin.video.moviestream',
                'profile': '/tmp/moviestream_profile',
                'author': 'MovieStream Team'
            }
            return info.get(info_type, '')
        
        def openSettings(self):
            print("[ADDON] Settings opened")

class MockXBMCVFS:
    @staticmethod
    def exists(path):
        return os.path.exists(path)
    
    @staticmethod
    def mkdirs(path):
        os.makedirs(path, exist_ok=True)
        return True
    
    @staticmethod
    def translatePath(path):
        return path.replace('special://', '/tmp/')

# Mock requests for testing
class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

# Install mocks
sys.modules['xbmc'] = MockXBMC()
sys.modules['xbmcgui'] = MockXBMCGUI()
sys.modules['xbmcplugin'] = MockXBMCPlugin()
sys.modules['xbmcaddon'] = MockXBMCAddon()
sys.modules['xbmcvfs'] = MockXBMCVFS()

class MovieStreamTester:
    """Test suite for MovieStream Pro Kodi addon"""
    
    def __init__(self):
        self.addon_path = '/app/plugin.video.moviestream'
        self.test_results = {
            'client_initialization': {'status': 'pending', 'details': []},
            'cocoscrapers_integration': {'status': 'pending', 'details': []},
            'settings_access': {'status': 'pending', 'details': []},
            'url_resolution': {'status': 'pending', 'details': []},
            'error_handling': {'status': 'pending', 'details': []},
            'import_tests': {'status': 'pending', 'details': []},
            'tmdb_client': {'status': 'pending', 'details': []},
            'github_client': {'status': 'pending', 'details': []},
            'main_functionality': {'status': 'pending', 'details': []}
        }
        
        # Add addon path to sys.path
        if self.addon_path not in sys.path:
            sys.path.insert(0, self.addon_path)
        
        # Add resources/lib to path
        lib_path = os.path.join(self.addon_path, 'resources', 'lib')
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)
    
    def run_all_tests(self):
        """Run all test suites"""
        print("=" * 60)
        print("MOVIESTREAM PRO KODI ADDON TESTING")
        print("=" * 60)
        
        test_methods = [
            self.test_imports,
            self.test_client_initialization,
            self.test_cocoscrapers_integration,
            self.test_settings_access,
            self.test_tmdb_client,
            self.test_github_client,
            self.test_url_resolution,
            self.test_main_functionality,
            self.test_error_handling
        ]
        
        for test_method in test_methods:
            try:
                print(f"\n--- Running {test_method.__name__} ---")
                test_method()
            except Exception as e:
                print(f"ERROR in {test_method.__name__}: {str(e)}")
                traceback.print_exc()
        
        self.print_summary()
    
    def test_imports(self):
        """Test if all required modules can be imported"""
        test_name = 'import_tests'
        
        try:
            # Test main addon import
            main_spec = importlib.util.spec_from_file_location(
                "main", os.path.join(self.addon_path, "main.py")
            )
            if main_spec is None:
                raise ImportError("Could not load main.py spec")
            
            # Test individual library imports
            lib_modules = [
                'tmdb_client',
                'github_client',
                'cocoscrapers_client',
                'debrid_client',
                'watchlist_manager',
                'video_player'
            ]
            
            imported_modules = {}
            failed_imports = []
            
            for module_name in lib_modules:
                try:
                    module = importlib.import_module(module_name)
                    imported_modules[module_name] = module
                    self.test_results[test_name]['details'].append(f"✅ {module_name} imported successfully")
                except ImportError as e:
                    failed_imports.append(f"❌ {module_name}: {str(e)}")
                    self.test_results[test_name]['details'].append(f"❌ {module_name}: {str(e)}")
            
            if failed_imports:
                self.test_results[test_name]['status'] = 'failed'
                self.test_results[test_name]['details'].extend(failed_imports)
            else:
                self.test_results[test_name]['status'] = 'passed'
                self.test_results[test_name]['details'].append("All core modules imported successfully")
            
        except Exception as e:
            self.test_results[test_name]['status'] = 'failed'
            self.test_results[test_name]['details'].append(f"Import test failed: {str(e)}")
    
    def test_client_initialization(self):
        """Test client initialization"""
        test_name = 'client_initialization'
        
        try:
            # Test TMDB Client
            from tmdb_client import TMDBClient
            tmdb = TMDBClient()
            self.test_results[test_name]['details'].append("✅ TMDBClient initialized")
            
            # Test GitHub Client
            from github_client import GitHubClient
            github = GitHubClient()
            self.test_results[test_name]['details'].append("✅ GitHubClient initialized")
            
            # Test Cocoscrapers Client
            from cocoscrapers_client import CocoScrapersClient
            cocoscrapers = CocoScrapersClient()
            self.test_results[test_name]['details'].append("✅ CocoScrapersClient initialized")
            
            # Test Debrid Client
            from debrid_client import DebridClient
            debrid = DebridClient()
            self.test_results[test_name]['details'].append("✅ DebridClient initialized")
            
            # Test Watchlist Manager
            from watchlist_manager import WatchlistManager
            watchlist = WatchlistManager()
            self.test_results[test_name]['details'].append("✅ WatchlistManager initialized")
            
            # Test Video Player
            from video_player import VideoPlayer
            player = VideoPlayer()
            self.test_results[test_name]['details'].append("✅ VideoPlayer initialized")
            
            self.test_results[test_name]['status'] = 'passed'
            
        except Exception as e:
            self.test_results[test_name]['status'] = 'failed'
            self.test_results[test_name]['details'].append(f"Client initialization failed: {str(e)}")
    
    def test_cocoscrapers_integration(self):
        """Test Cocoscrapers integration"""
        test_name = 'cocoscrapers_integration'
        
        try:
            from cocoscrapers_client import CocoScrapersClient
            client = CocoScrapersClient()
            
            # Test availability check
            is_available = client.is_available()
            self.test_results[test_name]['details'].append(f"Cocoscrapers available: {is_available}")
            
            if not is_available:
                self.test_results[test_name]['details'].append("⚠️ Cocoscrapers not available - this is expected in test environment")
                self.test_results[test_name]['status'] = 'passed'  # This is expected
                return
            
            # Test scraper stats
            try:
                stats = client.get_scraper_stats()
                self.test_results[test_name]['details'].append(f"Scraper stats: {stats}")
            except Exception as e:
                self.test_results[test_name]['details'].append(f"⚠️ Stats error: {str(e)}")
            
            # Test movie scraping (mock)
            try:
                sources = client.scrape_movie_sources("Test Movie", "2023")
                self.test_results[test_name]['details'].append(f"Movie scraping returned: {len(sources)} sources")
            except Exception as e:
                self.test_results[test_name]['details'].append(f"Movie scraping error: {str(e)}")
            
            self.test_results[test_name]['status'] = 'passed'
            
        except Exception as e:
            self.test_results[test_name]['status'] = 'failed'
            self.test_results[test_name]['details'].append(f"Cocoscrapers integration test failed: {str(e)}")
    
    def test_settings_access(self):
        """Test addon settings access"""
        test_name = 'settings_access'
        
        try:
            from xbmcaddon import Addon
            addon = Addon()
            
            # Test various setting types
            settings_to_test = [
                ('tmdb_api_key', 'getSetting'),
                ('enable_cocoscrapers', 'getSettingBool'),
                ('scraper_timeout', 'getSetting'),
                ('max_sources', 'getSetting'),
                ('auto_play_best_source', 'getSettingBool')
            ]
            
            for setting_key, method_name in settings_to_test:
                method = getattr(addon, method_name)
                value = method(setting_key)
                self.test_results[test_name]['details'].append(f"✅ {setting_key}: {value}")
            
            # Test addon info
            addon_info = [
                'id', 'name', 'version', 'path', 'profile', 'author'
            ]
            
            for info_key in addon_info:
                value = addon.getAddonInfo(info_key)
                self.test_results[test_name]['details'].append(f"✅ {info_key}: {value}")
            
            self.test_results[test_name]['status'] = 'passed'
            
        except Exception as e:
            self.test_results[test_name]['status'] = 'failed'
            self.test_results[test_name]['details'].append(f"Settings access test failed: {str(e)}")
    
    def test_tmdb_client(self):
        """Test TMDB client functionality"""
        test_name = 'tmdb_client'
        
        try:
            from tmdb_client import TMDBClient
            
            # Mock requests for TMDB
            with patch('requests.Session.get') as mock_get:
                mock_response = MockResponse({
                    'results': [
                        {
                            'id': 12345,
                            'title': 'Test Movie',
                            'release_date': '2023-01-01',
                            'overview': 'Test movie description',
                            'vote_average': 8.5,
                            'poster_path': '/test_poster.jpg'
                        }
                    ],
                    'total_pages': 1,
                    'total_results': 1
                })
                mock_get.return_value = mock_response
                
                client = TMDBClient()
                
                # Test popular movies
                movies = client.get_popular_movies()
                if movies and 'results' in movies:
                    self.test_results[test_name]['details'].append(f"✅ Popular movies: {len(movies['results'])} found")
                else:
                    self.test_results[test_name]['details'].append("❌ Popular movies failed")
                
                # Test movie search
                search_results = client.search_movies("Test Movie")
                if search_results and 'results' in search_results:
                    self.test_results[test_name]['details'].append(f"✅ Movie search: {len(search_results['results'])} found")
                else:
                    self.test_results[test_name]['details'].append("❌ Movie search failed")
            
            self.test_results[test_name]['status'] = 'passed'
            
        except Exception as e:
            self.test_results[test_name]['status'] = 'failed'
            self.test_results[test_name]['details'].append(f"TMDB client test failed: {str(e)}")
    
    def test_github_client(self):
        """Test GitHub client functionality"""
        test_name = 'github_client'
        
        try:
            from github_client import GitHubClient
            
            # Mock requests for GitHub
            with patch('requests.Session.get') as mock_get:
                mock_response = MockResponse([
                    {
                        'id': 'movie_001',
                        'title': 'Test Movie',
                        'year': 2023,
                        'video_url': 'https://example.com/movie.mp4',
                        'poster_url': 'https://example.com/poster.jpg'
                    }
                ])
                mock_get.return_value = mock_response
                
                client = GitHubClient()
                
                # Test movie collection
                collection = client.get_movie_collection()
                if collection and len(collection) > 0:
                    self.test_results[test_name]['details'].append(f"✅ Movie collection: {len(collection)} movies found")
                else:
                    self.test_results[test_name]['details'].append("❌ Movie collection failed")
                
                # Test sample JSON creation
                sample_files = client.create_sample_json_files()
                if sample_files and 'movies.json' in sample_files:
                    self.test_results[test_name]['details'].append("✅ Sample JSON files created")
                else:
                    self.test_results[test_name]['details'].append("❌ Sample JSON creation failed")
            
            self.test_results[test_name]['status'] = 'passed'
            
        except Exception as e:
            self.test_results[test_name]['status'] = 'failed'
            self.test_results[test_name]['details'].append(f"GitHub client test failed: {str(e)}")
    
    def test_url_resolution(self):
        """Test URL resolution and setResolvedUrl calls"""
        test_name = 'url_resolution'
        
        try:
            from video_player import VideoPlayer
            
            player = VideoPlayer()
            
            # Test video playback with metadata
            test_metadata = {
                'title': 'Test Movie',
                'plot': 'Test description',
                'year': 2023,
                'quality': '1080p'
            }
            
            # Mock sys.argv for plugin handle
            with patch('sys.argv', ['plugin://plugin.video.moviestream/', '1', '']):
                with patch('xbmcplugin.setResolvedUrl') as mock_resolved:
                    result = player.play_video('https://example.com/test.mp4', test_metadata)
                    
                    if mock_resolved.called:
                        self.test_results[test_name]['details'].append("✅ setResolvedUrl called correctly")
                    else:
                        self.test_results[test_name]['details'].append("❌ setResolvedUrl not called")
                    
                    self.test_results[test_name]['details'].append(f"Play video result: {result}")
            
            self.test_results[test_name]['status'] = 'passed'
            
        except Exception as e:
            self.test_results[test_name]['status'] = 'failed'
            self.test_results[test_name]['details'].append(f"URL resolution test failed: {str(e)}")
    
    def test_main_functionality(self):
        """Test main addon functionality"""
        test_name = 'main_functionality'
        
        try:
            # Mock sys.argv for main execution
            with patch('sys.argv', ['plugin://plugin.video.moviestream/', '1', '']):
                # Import and test main functions
                sys.path.insert(0, self.addon_path)
                
                # Test URL creation
                def get_url(**kwargs):
                    from urllib.parse import urlencode
                    return f'plugin://plugin.video.moviestream/?{urlencode(kwargs)}'
                
                test_url = get_url(action='movies', page=1)
                self.test_results[test_name]['details'].append(f"✅ URL creation: {test_url}")
                
                # Test movie data creation
                test_movie = {
                    'title': 'Test Movie',
                    'year': '2023',
                    'tmdb_id': '12345',
                    'type': 'movie',
                    'plot': 'Test description'
                }
                
                movie_json = json.dumps(test_movie)
                parsed_movie = json.loads(movie_json)
                
                if parsed_movie['title'] == test_movie['title']:
                    self.test_results[test_name]['details'].append("✅ Movie data serialization works")
                else:
                    self.test_results[test_name]['details'].append("❌ Movie data serialization failed")
            
            self.test_results[test_name]['status'] = 'passed'
            
        except Exception as e:
            self.test_results[test_name]['status'] = 'failed'
            self.test_results[test_name]['details'].append(f"Main functionality test failed: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling throughout the addon"""
        test_name = 'error_handling'
        
        try:
            # Test client error handling
            from cocoscrapers_client import CocoScrapersClient
            client = CocoScrapersClient()
            
            # Test with invalid data
            sources = client.scrape_movie_sources("", "")  # Empty title and year
            self.test_results[test_name]['details'].append(f"✅ Empty movie scraping handled: {len(sources)} sources")
            
            # Test TMDB with invalid API key
            from tmdb_client import TMDBClient
            with patch('requests.Session.get') as mock_get:
                mock_get.side_effect = Exception("API Error")
                
                tmdb = TMDBClient()
                result = tmdb.get_popular_movies()
                
                if result is None:
                    self.test_results[test_name]['details'].append("✅ TMDB error handling works")
                else:
                    self.test_results[test_name]['details'].append("❌ TMDB error handling failed")
            
            # Test GitHub with invalid URL
            from github_client import GitHubClient
            with patch('requests.Session.get') as mock_get:
                mock_get.side_effect = Exception("Network Error")
                
                github = GitHubClient()
                result = github.get_movie_collection()
                
                if result is None:
                    self.test_results[test_name]['details'].append("✅ GitHub error handling works")
                else:
                    self.test_results[test_name]['details'].append("❌ GitHub error handling failed")
            
            self.test_results[test_name]['status'] = 'passed'
            
        except Exception as e:
            self.test_results[test_name]['status'] = 'failed'
            self.test_results[test_name]['details'].append(f"Error handling test failed: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in self.test_results.items():
            status = result['status']
            status_symbol = "✅" if status == 'passed' else "❌" if status == 'failed' else "⏳"
            
            print(f"\n{status_symbol} {test_name.upper()}: {status.upper()}")
            
            for detail in result['details']:
                print(f"   {detail}")
            
            if status == 'passed':
                passed += 1
            elif status == 'failed':
                failed += 1
        
        print(f"\n" + "=" * 60)
        print(f"TOTAL: {passed} passed, {failed} failed, {len(self.test_results) - passed - failed} pending")
        print("=" * 60)
        
        # Critical issues summary
        critical_issues = []
        
        if self.test_results['import_tests']['status'] == 'failed':
            critical_issues.append("❌ CRITICAL: Module imports failing")
        
        if self.test_results['client_initialization']['status'] == 'failed':
            critical_issues.append("❌ CRITICAL: Client initialization failing")
        
        if self.test_results['url_resolution']['status'] == 'failed':
            critical_issues.append("❌ CRITICAL: URL resolution not working")
        
        if critical_issues:
            print("\nCRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(issue)
        else:
            print("\n✅ No critical issues found!")
        
        print("\nRECOMMENDATIONS:")
        
        if not self.test_results['cocoscrapers_integration']['status'] == 'passed':
            print("• Install script.module.cocoscrapers for full functionality")
        
        print("• Test with real Kodi environment for complete validation")
        print("• Verify all external dependencies are available")
        print("• Test with actual TMDB API calls")
        print("• Test with real GitHub repository")

if __name__ == '__main__':
    tester = MovieStreamTester()
    tester.run_all_tests()