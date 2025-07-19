# MovieStream Database - Sample JSON Files

This directory contains sample JSON files that demonstrate the structure and schema for the MovieStream Kodi addon. These files serve as templates for creating your own movie and TV show databases.

## File Structure

### Main Collection Files
- `movies.json` - Main movie collection
- `tvshows.json` - Main TV show collection  
- `featured.json` - Featured content and collections

### Genre-Specific Files
- `genres/action.json` - Action movies
- `genres/animation.json` - Animation movies
- `genres/comedy.json` - Comedy movies
- `genres/drama.json` - Drama movies
- `genres/horror.json` - Horror movies
- `genres/romance.json` - Romance movies
- `genres/thriller.json` - Thriller movies

## JSON Schema

### Movie Object Schema
```json
{
  "id": "unique_movie_id",
  "title": "Movie Title",
  "year": 2023,
  "genre": "Action, Adventure",
  "rating": 8.5,
  "plot": "Movie description",
  "director": "Director Name",
  "cast": ["Actor 1", "Actor 2", "Actor 3"],
  "runtime": 120,
  "poster_url": "https://image.tmdb.org/t/p/w500/poster.jpg",
  "backdrop_url": "https://image.tmdb.org/t/p/w1280/backdrop.jpg",
  "video_url": "https://example.com/movie.mp4",
  "m3u8_url": "https://example.com/stream.m3u8",
  "trailer_url": "https://youtube.com/watch?v=trailer",
  "subtitles": [
    {
      "language": "en",
      "url": "https://example.com/subtitles_en.srt"
    }
  ],
  "quality": "1080p",
  "file_size": "2.5GB",
  "added_date": "2024-01-15",
  "tmdb_id": 12345,
  "imdb_id": "tt1234567",
  "custom_sources": [
    {
      "name": "Alternative Source",
      "url": "https://example.com/alt_source.mp4",
      "quality": "720p"
    }
  ]
}

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
          "m3u8_url": "https://example.com/episode.m3u8",
          "subtitles": [
            {
              "language": "en",
              "url": "https://example.com/subtitles_en.srt"
            }
          ]
        }
      ]
    }
  ]
}

Example URLs
{
  "video_url": "https://example.com/movie.mp4",
  "m3u8_url": "https://example.com/stream/playlist.m3u8",
  "custom_sources": [
    {
      "name": "HLS Stream",
      "url": "https://example.com/hls/manifest.m3u8",
      "type": "hls"
    },
    {
      "name": "IPTV Channel",
      "url": "https://example.com/iptv/channel.m3u",
      "type": "m3u"
    }
  ]
}

The MovieStream addon supports various video formats and streaming protocols:

Direct Video Files
MP4, MKV, AVI, MOV, WMV, FLV, WEBM
Streaming Protocols
M3U8 (HLS): HTTP Live Streaming playlists
M3U: IPTV playlist files
DASH: Dynamic Adaptive Streaming
Direct HTTP streams

