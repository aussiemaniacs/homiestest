#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Debrid Services Client for MovieStream Kodi Addon
Supports Real-Debrid, Premiumize, and All-Debrid
"""

import xbmc
import xbmcaddon
import requests
import json

class DebridClient:
    """Client for Debrid services integration"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.real_debrid_api = None
        self.premiumize_api = None
        self.alldebrid_api = None
        
        # Initialize APIs if keys are available
        self._initialize_apis()
    
    def _initialize_apis(self):
        """Initialize debrid service APIs"""
        # Real-Debrid
        rd_key = self.addon.getSetting('real_debrid_api_key')
        if rd_key:
            self.real_debrid_api = RealDebridAPI(rd_key)
        
        # Premiumize
        pm_key = self.addon.getSetting('premiumize_api_key') 
        if pm_key:
            self.premiumize_api = PremiumizeAPI(pm_key)
        
        # All-Debrid
        ad_key = self.addon.getSetting('alldebrid_api_key')
        if ad_key:
            self.alldebrid_api = AllDebridAPI(ad_key)
    
    def is_available(self):
        """Check if any debrid service is available"""
        return bool(self.real_debrid_api or self.premiumize_api or self.alldebrid_api)
    
    def filter_debrid_sources(self, sources):
        """Filter sources to show only debrid-supported links"""
        if not sources:
            return []
        
        debrid_sources = []
        
        for source in sources:
            url = source.get('url', '') if isinstance(source, dict) else str(source)
            
            # Check if URL is supported by any debrid service
            if self._is_debrid_supported(url):
                debrid_sources.append(source)
        
        return debrid_sources
    
    def _is_debrid_supported(self, url):
        """Check if URL is supported by available debrid services"""
        # Common debrid-supported domains
        supported_domains = [
            'rapidgator.net', 'uploaded.net', 'nitroflare.com',
            'turbobit.net', 'filefactory.com', '1fichier.com',
            'uptobox.com', 'mediafire.com', 'mega.nz'
        ]
        
        return any(domain in url.lower() for domain in supported_domains)
    
    def resolve_debrid_link(self, url):
        """Resolve a link using available debrid services"""
        if self.real_debrid_api:
            resolved = self.real_debrid_api.resolve_link(url)
            if resolved:
                return resolved
        
        if self.premiumize_api:
            resolved = self.premiumize_api.resolve_link(url) 
            if resolved:
                return resolved
        
        if self.alldebrid_api:
            resolved = self.alldebrid_api.resolve_link(url)
            if resolved:
                return resolved
        
        return None
    
    def check_account_status(self):
        """Check status of all configured debrid accounts"""
        status = {}
        
        if self.real_debrid_api:
            status['real_debrid'] = self.real_debrid_api.get_account_info()
        
        if self.premiumize_api:
            status['premiumize'] = self.premiumize_api.get_account_info()
        
        if self.alldebrid_api:
            status['alldebrid'] = self.alldebrid_api.get_account_info()
        
        return status

class RealDebridAPI:
    """Real-Debrid API client"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.real-debrid.com/rest/1.0'
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def resolve_link(self, url):
        """Resolve a link with Real-Debrid"""
        try:
            # Check if link is supported
            check_url = f'{self.base_url}/unrestrict/check'
            response = self.session.post(check_url, data={'link': url})
            
            if response.status_code == 200:
                # Unrestrict the link
                unrestrict_url = f'{self.base_url}/unrestrict/link'
                response = self.session.post(unrestrict_url, data={'link': url})
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('download')
            
        except Exception as e:
            xbmc.log(f"MovieStream: Real-Debrid error: {str(e)}", xbmc.LOGERROR)
        
        return None
    
    def get_account_info(self):
        """Get Real-Debrid account information"""
        try:
            response = self.session.get(f'{self.base_url}/user')
            if response.status_code == 200:
                data = response.json()
                return {
                    'service': 'Real-Debrid',
                    'username': data.get('username'),
                    'premium': data.get('type') == 'premium',
                    'expiry': data.get('expiration')
                }
        except:
            pass
        
        return None

class PremiumizeAPI:
    """Premiumize API client"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://www.premiumize.me/api'
    
    def resolve_link(self, url):
        """Resolve a link with Premiumize"""
        try:
            resolve_url = f'{self.base_url}/transfer/directdl'
            data = {'apikey': self.api_key, 'src': url}
            
            response = requests.post(resolve_url, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return result.get('location')
            
        except Exception as e:
            xbmc.log(f"MovieStream: Premiumize error: {str(e)}", xbmc.LOGERROR)
        
        return None
    
    def get_account_info(self):
        """Get Premiumize account information"""
        try:
            response = requests.get(f'{self.base_url}/account/info?apikey={self.api_key}')
            if response.status_code == 200:
                data = response.json()
                return {
                    'service': 'Premiumize',
                    'username': data.get('customer_id'),
                    'premium': data.get('premium_until', 0) > 0,
                    'points': data.get('space_left')
                }
        except:
            pass
        
        return None

class AllDebridAPI:
    """All-Debrid API client"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.alldebrid.com/v4'
    
    def resolve_link(self, url):
        """Resolve a link with All-Debrid"""
        try:
            resolve_url = f'{self.base_url}/link/unlock'
            data = {'agent': 'MovieStream', 'apikey': self.api_key, 'link': url}
            
            response = requests.post(resolve_url, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return result.get('data', {}).get('link')
            
        except Exception as e:
            xbmc.log(f"MovieStream: All-Debrid error: {str(e)}", xbmc.LOGERROR)
        
        return None
    
    def get_account_info(self):
        """Get All-Debrid account information"""
        try:
            response = requests.get(f'{self.base_url}/user?agent=MovieStream&apikey={self.api_key}')
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('data', {}).get('user', {})
                return {
                    'service': 'All-Debrid', 
                    'username': user_data.get('username'),
                    'premium': user_data.get('isPremium', False),
                    'remaining_days': user_data.get('premiumUntil')
                }
        except:
            pass
        
        return None