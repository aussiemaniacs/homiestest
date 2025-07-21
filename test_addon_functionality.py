#!/usr/bin/env python3
"""
Test script for MovieStream Pro addon
Tests the basic functionality and client initialization
"""

import sys
import os

# Add the plugin directory to Python path
addon_path = "/app/plugin.video.moviestream"
sys.path.insert(0, addon_path)
sys.path.insert(0, os.path.join(addon_path, "resources/lib"))

# Mock Kodi modules for testing
class MockXBMC:
    LOGINFO = 1
    LOGERROR = 4
    LOGWARNING = 2
    
    @staticmethod
    def log(message, level=1):
        level_name = {1: "INFO", 2: "WARNING", 4: "ERROR"}.get(level, "DEBUG")
        print(f"[{level_name}] {message}")

class MockXBMCAddon:
    def __init__(self):
        pass
    
    def getAddonInfo(self, info_type):
        info_map = {
            'id': 'plugin.video.moviestream',
            'name': 'MovieStream Pro',
            'version': '2.0.0',
            'path': addon_path,
            'profile': addon_path,
            'author': 'Test'
        }
        return info_map.get(info_type, '')
    
    def getSetting(self, setting_id):
        # Return some test settings
        if setting_id == 'tmdb_api_key':
            return 'd0f489a129429db6f2dd4751e5dbeb82'
        elif setting_id == 'github_repo_url':
            return 'https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/'
        return ''
    
    def getSettingBool(self, setting_id):
        return True
    
    def openSettings(self):
        print("Settings opened")

# Create a mock module with Addon class
class MockXBMCAddonModule:
    def Addon(self):
        return MockXBMCAddon()

class MockXBMCPlugin:
    @staticmethod
    def setPluginCategory(handle, category):
        print(f"Category: {category}")
    
    @staticmethod
    def setContent(handle, content):
        print(f"Content: {content}")
    
    @staticmethod
    def addDirectoryItem(handle, url, list_item, is_folder):
        print(f"Added item: {list_item.getLabel()}")
    
    @staticmethod
    def endOfDirectory(handle):
        print("Directory ended")
    
    @staticmethod
    def setResolvedUrl(handle, success, list_item):
        print(f"Resolved URL: {list_item.getPath()}")

class MockXBMCGUI:
    NOTIFICATION_INFO = 1
    NOTIFICATION_ERROR = 4
    NOTIFICATION_WARNING = 2
    
    class ListItem:
        def __init__(self, label='', path=''):
            self.label = label
            self.path = path
            self.art = {}
            self.info = {}
            self.properties = {}
        
        def getLabel(self):
            return self.label
        
        def getPath(self):
            return self.path
        
        def setArt(self, art_dict):
            self.art.update(art_dict)
        
        def setInfo(self, info_type, info_dict):
            self.info[info_type] = info_dict
        
        def setProperty(self, key, value):
            self.properties[key] = value
        
        def addContextMenuItems(self, items):
            print(f"Context menu items added: {len(items)}")
    
    class Dialog:
        @staticmethod
        def notification(title, message, icon=1, time=5000):
            print(f"Notification: {title} - {message}")
        
        @staticmethod
        def ok(title, message):
            print(f"OK Dialog: {title} - {message}")
            return True
        
        @staticmethod
        def textviewer(title, text):
            print(f"Text Viewer: {title}")
            print(text[:200] + "..." if len(text) > 200 else text)

class MockXBMCVFS:
    pass

# Mock the Kodi modules
sys.modules['xbmc'] = MockXBMC()
sys.modules['xbmcaddon'] = MockXBMCAddon
sys.modules['xbmcplugin'] = MockXBMCPlugin()
sys.modules['xbmcgui'] = MockXBMCGUI()
sys.modules['xbmcvfs'] = MockXBMCVFS()

# Mock sys.argv for the addon
sys.argv = ['plugin://plugin.video.moviestream/', '1', '']

def test_addon_import():
    """Test if the addon can be imported without errors"""
    print("=== Testing Addon Import ===")
    try:
        # Change to addon directory
        os.chdir(addon_path)
        
        # Import the main module
        import main
        print("✅ Main module imported successfully")
        return main
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return None

def test_basic_functionality(main_module):
    """Test basic addon functionality"""
    print("\n=== Testing Basic Functionality ===")
    
    try:
        # Test list_categories
        print("Testing list_categories...")
        main_module.list_categories()
        print("✅ list_categories works")
    except Exception as e:
        print(f"❌ list_categories failed: {str(e)}")
    
    try:
        # Test list_movies
        print("\nTesting list_movies...")
        main_module.list_movies(page=1, category='popular')
        print("✅ list_movies works")
    except Exception as e:
        print(f"❌ list_movies failed: {str(e)}")
    
    try:
        # Test debug_info
        print("\nTesting debug_info...")
        main_module.debug_info()
        print("✅ debug_info works")
    except Exception as e:
        print(f"❌ debug_info failed: {str(e)}")

def test_tmdb_connection():
    """Test TMDB API connection"""
    print("\n=== Testing TMDB Connection ===")
    try:
        import requests
        api_key = 'd0f489a129429db6f2dd4751e5dbeb82'
        url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page=1'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ TMDB connection successful - {len(data.get('results', []))} movies found")
        else:
            print(f"❌ TMDB connection failed - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ TMDB connection error: {str(e)}")

def main():
    print("MovieStream Pro Addon Test")
    print("=" * 50)
    
    # Test import
    main_module = test_addon_import()
    if not main_module:
        return
    
    # Test basic functionality
    test_basic_functionality(main_module)
    
    # Test TMDB connection
    test_tmdb_connection()
    
    print("\n" + "=" * 50)
    print("Test completed")

if __name__ == '__main__':
    main()