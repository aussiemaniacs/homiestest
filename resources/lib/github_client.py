#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import xbmc
import xbmcaddon
import json
import os
from urllib.parse import urljoin

class GitHubClient:
    """Client for GitHub integration to manage movie JSON files"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.base_url = self.addon.getSetting('github_repo_url') or 'https://raw.githubusercontent.com/moviestream/database/main/'
        self.session = requests.Session()
        
        # Set user agent
        self.session.headers.update({
            'User-Agent': 'MovieStream Kodi Addon 1.0.0'
        })
    
    def _make_request(self, url):
        """Make a request to GitHub"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            xbmc.log(f"MovieStream GitHub Error: {str(e)}", xbmc.LOGERROR)
            return None
        except json.JSONDecodeError as e:
            xbmc.log(f"MovieStream GitHub JSON Error: {str(e)}", xbmc.LOGERROR)
            return None
    
    def get_movie_collection(self):
        """Get the main movie collection from GitHub"""
        url = urljoin(self.base_url, 'movies.json')
        return self._make_request(url)
    
    def get_tv_collection(self):
        """Get the main TV collection from GitHub"""
        url = urljoin(self.base_url, 'tvshows.json')
        return self._make_request(url)
    
    def get_featured_collection(self):
        """Get featured content from GitHub"""
        url = urljoin(self.base_url, 'featured.json')
        return self._make_request(url)
    
    def get_genre_collection(self, genre):
        """Get movies by genre from GitHub"""
        url = urljoin(self.base_url, f'genres/{genre.lower()}.json')
        return self._make_request(url)
    
    def get_year_collection(self, year):
        """Get movies by year from GitHub"""
        url = urljoin(self.base_url, f'years/{year}.json')
        return self._make_request(url)
    
    def create_sample_json_files(self):
        """Create sample JSON file structures for GitHub"""
        
        # Sample movies.json structure
        sample_movies = [
            {
                "id": "movie_001",
                "title": "Sample Movie 1",
                "year": 2023,
                "genre": "Action, Adventure",
                "rating": 8.5,
                "plot": "An epic adventure movie with stunning visuals and great action sequences.",
                "director": "John Director",
                "cast": ["Actor One", "Actor Two", "Actor Three"],
                "runtime": 120,
                "poster_url": "https://image.tmdb.org/t/p/w500/sample_poster1.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/w1280/sample_backdrop1.jpg",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                "trailer_url": "https://www.youtube.com/watch?v=sample_trailer1",
                "subtitles": [
                    {"language": "en", "url": "https://example.com/subtitles/sample1_en.srt"},
                    {"language": "es", "url": "https://example.com/subtitles/sample1_es.srt"}
                ],
                "quality": "1080p",
                "file_size": "2.5GB",
                "added_date": "2024-01-15",
                "tmdb_id": 12345
            },
            {
                "id": "movie_002",
                "title": "Sample Movie 2",
                "year": 2023,
                "genre": "Comedy, Romance",
                "rating": 7.2,
                "plot": "A romantic comedy that will make you laugh and cry at the same time.",
                "director": "Jane Director",
                "cast": ["Actress One", "Actor Four", "Actress Two"],
                "runtime": 95,
                "poster_url": "https://image.tmdb.org/t/p/w500/sample_poster2.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/w1280/sample_backdrop2.jpg",
                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
                "trailer_url": "https://www.youtube.com/watch?v=sample_trailer2",
                "subtitles": [
                    {"language": "en", "url": "https://example.com/subtitles/sample2_en.srt"}
                ],
                "quality": "720p",
                "file_size": "1.8GB",
                "added_date": "2024-01-20",
                "tmdb_id": 67890
            }
        ]
        
        # Sample tvshows.json structure
        sample_tvshows = [
            {
                "id": "show_001",
                "title": "Sample TV Show 1",
                "first_air_date": "2023-03-15",
                "genre": "Drama, Thriller",
                "rating": 9.1,
                "plot": "A gripping drama series that keeps you on the edge of your seat.",
                "creator": "Show Creator",
                "cast": ["TV Actor One", "TV Actress One", "TV Actor Two"],
                "poster_url": "https://image.tmdb.org/t/p/w500/sample_show_poster1.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/w1280/sample_show_backdrop1.jpg",
                "tmdb_id": 54321,
                "seasons": [
                    {
                        "season_number": 1,
                        "episode_count": 10,
                        "episodes": [
                            {
                                "episode_number": 1,
                                "title": "Pilot",
                                "plot": "The series begins with an intriguing pilot episode.",
                                "runtime": 45,
                                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
                                "subtitles": [
                                    {"language": "en", "url": "https://example.com/subtitles/show1_s1e1_en.srt"}
                                ]
                            },
                            {
                                "episode_number": 2,
                                "title": "The Mystery Deepens",
                                "plot": "The plot thickens as new mysteries are revealed.",
                                "runtime": 43,
                                "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                                "subtitles": [
                                    {"language": "en", "url": "https://example.com/subtitles/show1_s1e2_en.srt"}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
        
        # Sample featured.json structure
        sample_featured = {
            "featured_movies": [
                {
                    "id": "movie_001",
                    "title": "Sample Movie 1",
                    "featured_reason": "Editor's Pick",
                    "featured_date": "2024-01-15"
                }
            ],
            "featured_shows": [
                {
                    "id": "show_001",
                    "title": "Sample TV Show 1",
                    "featured_reason": "Trending Now",
                    "featured_date": "2024-01-20"
                }
            ]
        }
        
        # Sample genre-specific file (action.json)
        sample_action = [
            {
                "id": "movie_001",
                "title": "Sample Movie 1",
                "year": 2023,
                "subgenres": ["Adventure", "Sci-Fi"],
                "action_rating": 9.0
            }
        ]
        
        return {
            "movies.json": sample_movies,
            "tvshows.json": sample_tvshows,
            "featured.json": sample_featured,
            "genres/action.json": sample_action,
            "README.md": self._create_readme_content()
        }
    
    def _create_readme_content(self):
        """Create README content for the GitHub repository"""
        return """# MovieStream Database

This repository contains JSON files for the MovieStream Kodi addon.

## File Structure

### Main Collections
- `movies.json` - Main movie collection
- `tvshows.json` - Main TV show collection  
- `featured.json` - Featured content

### Genre Collections
- `genres/action.json` - Action movies
- `genres/comedy.json` - Comedy movies
- `genres/drama.json` - Drama movies
- `genres/horror.json` - Horror movies
- `genres/romance.json` - Romance movies
- `genres/thriller.json` - Thriller movies

### Year Collections
- `years/2024.json` - Movies from 2024
- `years/2023.json` - Movies from 2023
- etc.

## JSON Schema

### Movie Object
```json
{
  "id": "unique_movie_id",
  "title": "Movie Title",
  "year": 2023,
  "genre": "Action, Adventure",
  "rating": 8.5,
  "plot": "Movie description",
  "director": "Director Name",
  "cast": ["Actor 1", "Actor 2"],
  "runtime": 120,
  "poster_url": "https://image.tmdb.org/t/p/w500/poster.jpg",
  "backdrop_url": "https://image.tmdb.org/t/p/w1280/backdrop.jpg",
  "video_url": "https://example.com/movie.mp4",
  "trailer_url": "https://youtube.com/watch?v=trailer",
  "subtitles": [
    {"language": "en", "url": "https://example.com/subs_en.srt"}
  ],
  "quality": "1080p",
  "file_size": "2.5GB",
  "added_date": "2024-01-15",
  "tmdb_id": 12345
}
```

### TV Show Object
```json
{
  "id": "unique_show_id",
  "title": "Show Title",
  "first_air_date": "2023-03-15",
  "genre": "Drama, Thriller",
  "rating": 9.1,
  "plot": "Show description",
  "creator": "Creator Name",
  "cast": ["Actor 1", "Actor 2"],
  "poster_url": "https://image.tmdb.org/t/p/w500/poster.jpg",
  "backdrop_url": "https://image.tmdb.org/t/p/w1280/backdrop.jpg",
  "tmdb_id": 54321,
  "seasons": [
    {
      "season_number": 1,
      "episode_count": 10,
      "episodes": [
        {
          "episode_number": 1,
          "title": "Episode Title",
          "plot": "Episode description",
          "runtime": 45,
          "video_url": "https://example.com/episode.mp4",
          "subtitles": [
            {"language": "en", "url": "https://example.com/subs_en.srt"}
          ]
        }
      ]
    }
  ]
}
```

## Usage

1. Edit the JSON files to add your content
2. Ensure all URLs are publicly accessible
3. The MovieStream addon will automatically fetch updates
4. Test your JSON files for valid syntax

## Video Sources

You can use various types of video URLs:
- Direct MP4/MKV file URLs
- Streaming service URLs
- CDN-hosted content
- Any publicly accessible video URL

## Important Notes

- All JSON files must be valid JSON syntax
- Video URLs must be publicly accessible
- Image URLs should use HTTPS when possible
- Subtitle files should be in SRT format
"""