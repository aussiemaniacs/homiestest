#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for MovieStream Kodi Addon
This script verifies the addon structure and dependencies
"""

import os
import json
import sys
from pathlib import Path

def test_addon_structure():
    """Test that all required files exist"""
    print("Testing addon structure...")
    
    required_files = [
        "addon.xml",
        "main.py", 
        "icon.png",
        "fanart.jpg",
        "resources/settings.xml",
        "resources/language/resource.language.en_gb/strings.po",
        "resources/lib/__init__.py",
        "resources/lib/tmdb_client.py",
        "resources/lib/github_client.py",
        "resources/lib/video_player.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print("\n✅ All required files present!")
    return True

def test_json_files():
    """Test that JSON files are valid"""
    print("\nTesting JSON files...")
    
    json_files = [
        "sample_json_files/movies.json",
        "sample_json_files/tvshows.json", 
        "sample_json_files/featured.json",
        "sample_json_files/genres/action.json",
        "sample_json_files/genres/animation.json"
    ]
    
    invalid_files = []
    
    for file_path in json_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"✓ {file_path}")
            except json.JSONDecodeError as e:
                print(f"❌ {file_path}: {str(e)}")
                invalid_files.append(file_path)
        else:
            print(f"⚠ {file_path}: File not found")
    
    if invalid_files:
        print(f"\n❌ Invalid JSON files:")
        for file_path in invalid_files:
            print(f"  - {file_path}")
        return False
    
    print("\n✅ All JSON files are valid!")
    return True

def test_python_syntax():
    """Test that Python files have valid syntax"""
    print("\nTesting Python syntax...")
    
    python_files = [
        "main.py",
        "resources/lib/tmdb_client.py",
        "resources/lib/github_client.py", 
        "resources/lib/video_player.py"
    ]
    
    syntax_errors = []
    
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), file_path, 'exec')
                print(f"✓ {file_path}")
            except SyntaxError as e:
                print(f"❌ {file_path}: {str(e)}")
                syntax_errors.append(file_path)
        else:
            print(f"⚠ {file_path}: File not found")
    
    if syntax_errors:
        print(f"\n❌ Python syntax errors:")
        for file_path in syntax_errors:
            print(f"  - {file_path}")
        return False
    
    print("\n✅ All Python files have valid syntax!")
    return True

def test_addon_xml():
    """Test addon.xml structure"""
    print("\nTesting addon.xml...")
    
    if not os.path.exists("addon.xml"):
        print("❌ addon.xml not found")
        return False
    
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse("addon.xml")
        root = tree.getroot()
        
        # Check required attributes
        if root.get('id') != 'plugin.video.moviestream':
            print("❌ Incorrect addon ID")
            return False
        
        if not root.get('version'):
            print("❌ Missing version attribute")
            return False
        
        print("✓ addon.xml structure valid")
        print(f"✓ Addon ID: {root.get('id')}")
        print(f"✓ Version: {root.get('version')}")
        
        return True
        
    except Exception as e:
        print(f"❌ addon.xml error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("MovieStream Kodi Addon - Structure Test")
    print("=" * 50)
    
    tests = [
        test_addon_structure,
        test_json_files,
        test_python_syntax,
        test_addon_xml
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Addon is ready for installation.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())