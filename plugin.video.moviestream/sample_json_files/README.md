# MovieStream Database

This repository contains JSON files for the MovieStream Kodi addon.

## Quick Start

1. Fork this repository
2. Edit the JSON files to add your content
3. Update your addon settings with your GitHub repository URL
4. The MovieStream addon will automatically fetch your content

## File Structure

### Main Collections
- `movies.json` - Main movie collection
- `tvshows.json` - Main TV show collection  
- `featured.json` - Featured content and hero section

### Genre Collections
- `genres/action.json` - Action movies
- `genres/animation.json` - Animation movies
- `genres/comedy.json` - Comedy movies
- `genres/drama.json` - Drama movies
- `genres/horror.json` - Horror movies
- `genres/romance.json` - Romance movies
- `genres/thriller.json` - Thriller movies

### Year Collections (Optional)
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

## Supported Video Sources

You can use various types of video URLs:
- **Direct file URLs**: MP4, MKV, AVI, etc.
- **CDN URLs**: Amazon S3, Google Cloud, etc.
- **Streaming URLs**: HLS, DASH streams
- **Custom providers**: Your own video hosting

## Image URLs

- **Posters**: Recommended size 500x750px
- **Backdrops**: Recommended size 1280x720px
- Use HTTPS URLs when possible
- TMDB images work great: `https://image.tmdb.org/t/p/w500/[poster_path]`

## Subtitle Support

- **Format**: SRT files recommended
- **Languages**: Use ISO 639-1 codes (en, es, fr, etc.)
- **Hosting**: Any publicly accessible URL

## Testing Your JSON

Before committing changes:

1. **Validate JSON syntax**: Use https://jsonlint.com/
2. **Test URLs**: Ensure all video/image URLs are accessible
3. **Check encoding**: Use UTF-8 encoding for special characters

## GitHub Integration

1. Host this repository on GitHub
2. Use raw URLs in your addon settings:
   ```
   https://raw.githubusercontent.com/yourusername/moviestream-db/main/
   ```
3. The addon will fetch updates automatically

## Tips

- **Start small**: Begin with a few movies to test
- **Use TMDB**: Copy metadata from The Movie Database
- **Organize by genre**: Use genre-specific files for better browsing
- **Keep it updated**: Regular updates keep your content fresh
- **Backup**: Keep local copies of your JSON files

## Example URLs

Replace `yourusername` and `moviestream-db` with your GitHub details:

- Movies: `https://raw.githubusercontent.com/yourusername/moviestream-db/main/movies.json`
- TV Shows: `https://raw.githubusercontent.com/yourusername/moviestream-db/main/tvshows.json`
- Featured: `https://raw.githubusercontent.com/yourusername/moviestream-db/main/featured.json`

## Need Help?

- Check the sample files for examples
- Validate your JSON syntax
- Test video URLs in a browser first
- Start with the basic movies.json structure

Happy streaming! 🎬