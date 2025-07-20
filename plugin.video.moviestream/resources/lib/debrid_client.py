#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Debrid Services Client for MovieStream Kodi Addon
Handles Real-Debrid, Premiumize, and All-Debrid integration
"""

import xbmc
import xbmcaddon
import xbmcgui
import requests
import json
import base64
import time

class DebridClient:
    """Client for debrid services integration"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.session = requests.Session()
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': 'MovieStream Pro 2.0.0'
        })
        
        # Initialize debrid services
        self.realdebrid = RealDebridAPI(self.session, self.addon)
        self.premiumize = PremiumizeAPI(self.session, self.addon)
        self.alldebrid = AllDebridAPI(self.session, self.addon)
    
    def is_available(self):
        """Check if any debrid service is available"""
        return (self.realdebrid.is_enabled() or 
                self.premiumize.is_enabled() or 
                self.alldebrid.is_enabled())
    
    def get_available_services(self):
        """Get list of available debrid services"""
        services = []
        
        if self.realdebrid.is_enabled():
            services.append('realdebrid')
        if self.premiumize.is_enabled():
            services.append('premiumize')
        if self.alldebrid.is_enabled():
            services.append('alldebrid')
        
        return services
    
    def filter_debrid_sources(self, sources):
        """Filter sources and add debrid links"""
        if not sources or not self.is_available():
            return sources
        
        enhanced_sources = []
        
        for source in sources:
            # Add original source
            enhanced_sources.append(source)
            
            # Check for debrid cached links
            source_url = source.get('url', '')
            
            if self._is_supported_hoster(source_url):
                debrid_links = self._get_debrid_links(source_url)
                
                for debrid_link in debrid_links:
                    # Create enhanced source
                    debrid_source = source.copy()
                    debrid_source.update(debrid_link)
                    debrid_source['debrid'] = True
                    debrid_source['quality'] = debrid_link.get('quality', source.get('quality', ''))
                    enhanced_sources.append(debrid_source)
        
        # Sort with debrid sources first
        enhanced_sources.sort(key=lambda x: (
            x.get('debrid', False),  # Debrid first
            self._quality_score(x.get('quality', '')),  # Then by quality
            x.get('provider', '').lower()  # Then by provider
        ), reverse=True)
        
        return enhanced_sources
    
    def _is_supported_hoster(self, url):
        """Check if URL is from supported hoster"""
        supported_hosters = [
            'rapidgator.net', 'uploaded.net', '1fichier.com',
            'nitroflare.com', 'turbobit.net', 'k2s.cc',
            'filesfly.io', 'filejoker.net', 'katfile.com'
        ]
        
        for hoster in supported_hosters:
            if hoster in url.lower():
                return True
        
        return False
    
    def _get_debrid_links(self, url):
        """Get debrid links for a URL"""
        debrid_links = []
        
        # Try each enabled service
        priority = self.addon.getSetting('debrid_priority') or 'realdebrid'
        
        services = [priority]  # Try priority first
        for service in ['realdebrid', 'premiumize', 'alldebrid']:
            if service != priority:
                services.append(service)
        
        for service in services:
            if service == 'realdebrid' and self.realdebrid.is_enabled():
                link = self.realdebrid.unrestrict_link(url)
                if link:
                    debrid_links.append({
                        'url': link,
                        'provider': 'Real-Debrid',
                        'service': 'realdebrid'
                    })
                    break  # Use first working service
            
            elif service == 'premiumize' and self.premiumize.is_enabled():
                link = self.premiumize.unrestrict_link(url)
                if link:
                    debrid_links.append({
                        'url': link,
                        'provider': 'Premiumize',
                        'service': 'premiumize'
                    })
                    break
            
            elif service == 'alldebrid' and self.alldebrid.is_enabled():
                link = self.alldebrid.unrestrict_link(url)
                if link:
                    debrid_links.append({
                        'url': link,
                        'provider': 'All-Debrid',
                        'service': 'alldebrid'
                    })
                    break
        
        return debrid_links
    
    def _quality_score(self, quality):
        """Get quality score for sorting"""
        quality_lower = quality.lower()
        
        if '4k' in quality_lower or '2160p' in quality_lower:
            return 400
        elif '1080p' in quality_lower:
            return 300
        elif '720p' in quality_lower:
            return 200
        elif '480p' in quality_lower:
            return 100
        else:
            return 50
    
    def check_account_status(self):
        """Check status of all enabled debrid accounts"""
        status = {}
        
        if self.realdebrid.is_enabled():
            status['realdebrid'] = self.realdebrid.get_account_info()
        
        if self.premiumize.is_enabled():
            status['premiumize'] = self.premiumize.get_account_info()
        
        if self.alldebrid.is_enabled():
            status['alldebrid'] = self.alldebrid.get_account_info()
        
        return status


class RealDebridAPI:
    """Real-Debrid API client"""
    
    def __init__(self, session, addon):
        self.session = session
        self.addon = addon
        self.api_url = 'https://api.real-debrid.com/rest/1.0'
    
    def is_enabled(self):
        """Check if Real-Debrid is enabled and has API key"""
        return (self.addon.getSettingBool('enable_realdebrid') and 
                bool(self.addon.getSetting('realdebrid_api_key')))
    
    def _make_request(self, endpoint, method='GET', data=None):
        """Make API request to Real-Debrid"""
        if not self.is_enabled():
            return None
        
        api_key = self.addon.getSetting('realdebrid_api_key')
        headers = {'Authorization': f'Bearer {api_key}'}
        
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, headers=headers, data=data, timeout=10)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            xbmc.log(f"MovieStream Real-Debrid Error: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_account_info(self):
        """Get account information"""
        result = self._make_request('user')
        if result:
            return {
                'service': 'Real-Debrid',
                'username': result.get('username', 'Unknown'),
                'email': result.get('email', 'Unknown'),
                'premium': result.get('type', '') == 'premium',
                'expiration': result.get('expiration', 'Unknown'),
                'points': result.get('points', 0)
            }
        return None
    
    def unrestrict_link(self, url):
        """Unrestrict a premium link"""
        data = {'link': url}
        result = self._make_request('unrestrict/link', method='POST', data=data)
        
        if result and result.get('download'):
            return result['download']
        
        return None
    
    def check_link_availability(self, links):
        """Check if links are available for unrestricting"""
        if isinstance(links, str):
            links = [links]
        
        data = {'link': '\n'.join(links)}
        result = self._make_request('unrestrict/check', method='POST', data=data)
        
        return result if result else {}


class PremiumizeAPI:
    """Premiumize API client"""
    
    def __init__(self, session, addon):
        self.session = session
        self.addon = addon
        self.api_url = 'https://www.premiumize.me/api'
    
    def is_enabled(self):
        """Check if Premiumize is enabled and has API key"""
        return (self.addon.getSettingBool('enable_premiumize') and 
                bool(self.addon.getSetting('premiumize_api_key')))
    
    def _make_request(self, endpoint, method='GET', data=None):
        """Make API request to Premiumize"""
        if not self.is_enabled():
            return None
        
        api_key = self.addon.getSetting('premiumize_api_key')
        
        if data is None:
            data = {}
        data['apikey'] = api_key
        
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=data, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, data=data, timeout=10)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            xbmc.log(f"MovieStream Premiumize Error: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_account_info(self):
        """Get account information"""
        result = self._make_request('account/info')
        if result and result.get('status') == 'success':
            return {
                'service': 'Premiumize',
                'username': result.get('customer_id', 'Unknown'),
                'premium': result.get('premium_until', 0) > time.time(),
                'expiration': result.get('premium_until', 0),
                'space_used': result.get('space_used', 0),
                'limit_used': result.get('limit_used', 0)
            }
        return None
    
    def unrestrict_link(self, url):
        """Unrestrict a premium link"""
        data = {'src': url}
        result = self._make_request('transfer/directdl', method='POST', data=data)
        
        if result and result.get('status') == 'success':
            content = result.get('content', [])
            if content:
                return content[0].get('link')
        
        return None


class AllDebridAPI:
    """All-Debrid API client"""
    
    def __init__(self, session, addon):
        self.session = session
        self.addon = addon
        self.api_url = 'https://api.alldebrid.com/v4'
    
    def is_enabled(self):
        """Check if All-Debrid is enabled and has API key"""
        return (self.addon.getSettingBool('enable_alldebrid') and 
                bool(self.addon.getSetting('alldebrid_api_key')))
    
    def _make_request(self, endpoint, method='GET', data=None):
        """Make API request to All-Debrid"""
        if not self.is_enabled():
            return None
        
        api_key = self.addon.getSetting('alldebrid_api_key')
        
        if data is None:
            data = {}
        data['agent'] = 'MovieStream'
        data['apikey'] = api_key
        
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=data, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, data=data, timeout=10)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            xbmc.log(f"MovieStream All-Debrid Error: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_account_info(self):
        """Get account information"""
        result = self._make_request('user')
        if result and result.get('status') == 'success':
            data = result.get('data', {})
            return {
                'service': 'All-Debrid',
                'username': data.get('user', {}).get('username', 'Unknown'),
                'email': data.get('user', {}).get('email', 'Unknown'),
                'premium': data.get('user', {}).get('isPremium', False),
                'expiration': data.get('user', {}).get('premiumUntil', 'Unknown')
            }
        return None
    
    def unrestrict_link(self, url):
        """Unrestrict a premium link"""
        data = {'link': url}
        result = self._make_request('link/unlock', method='GET', data=data)
        
        if result and result.get('status') == 'success':
            data = result.get('data', {})
            return data.get('link')
        
        return None