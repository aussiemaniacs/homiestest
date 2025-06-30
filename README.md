# MovieStream Kodi 21 Addon

A comprehensive Kodi 21 addon that plays video links and gets metadata from TMDB, with GitHub integration for custom movie databases.

## Features

✅ **Video Playback**
- Support for multiple video formats (MP4, MKV, AVI, etc.)
- Direct video URL playback
- Streaming service integration
- Subtitle support with multiple languages

✅ **Metadata Integration**
- TMDB (The Movie Database) API integration
- Automatic metadata fetching
- High-quality artwork and posters
- Cast, crew, and plot information

✅ **GitHub Integration**
- Custom JSON movie databases
- Editable movie collections
- Automatic updates from GitHub
- Easy content management

✅ **Content Types**
- Movies with full metadata
- TV Shows with seasons and episodes
- Featured content collections
- Genre-based browsing
- Search functionality

✅ **Kodi 21 Compatibility**
- Native Kodi interface
- Proper categorization
- Search integration
- Settings management

## Installation

### Method 1: Manual Installation

1. **Download the addon**:
   - Download all files from this repository
   - Create a ZIP file containing all the addon files

2. **Install in Kodi**:
   - Open Kodi
   - Go to **Add-ons** → **Install from zip file**
   - Select the downloaded ZIP file
   - Wait for installation confirmation

3. **Configure the addon**:
   - Go to **Add-ons** → **My add-ons** → **Video add-ons**
   - Find "MovieStream" and click **Configure**
   - Set your GitHub repository URL (optional)
   - Adjust other settings as needed

### Method 2: Development Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/moviestream-addon.git
   cd moviestream-addon
   ```

2. **Copy to Kodi addons directory**:
   ```bash
   # Linux/Mac
   cp -r . ~/.kodi/addons/plugin.video.moviestream/
   
   # Windows
   copy . %APPDATA%\Kodi\addons\plugin.video.moviestream\
   ```

3. **Restart Kodi** and the addon should appear in Video Add-ons

## Configuration

### TMDB API Key
- The addon comes with a default TMDB API key
- For production use, get your own key at: https://www.themoviedb.org/settings/api
- Set it in the addon settings

### GitHub Repository
1. **Fork the sample database**:
   - Create a GitHub repository
   - Copy the sample JSON files from `sample_json_files/`
   - Upload them to your repository

2. **Configure the addon**:
   - Set GitHub Repository URL to: `https://raw.githubusercontent.com/yourusername/your-repo/main/`
   - Enable GitHub sync in settings

## JSON Database Structure

### Creating Your Movie Database

1. **Create a GitHub repository** for your movie database
2. **Add JSON files** following the provided schemas:

#### movies.json
```json
[
  {
    "id": "movie_001", 
    "title": "Your Movie Title",
    "year": 2023,
    "genre": "Action, Adventure", 
    "rating": 8.5,
    "plot": "Movie description...",
    "director": "Director Name",
    "cast": ["Actor 1", "Actor 2"],
    "runtime": 120,
    "poster_url": "https://image.tmdb.org/t/p/w500/poster.jpg",
    "backdrop_url": "https://image.tmdb.org/t/p/w1280/backdrop.jpg",
    "video_url": "https://your-server.com/movie.mp4",
    "trailer_url": "https://youtube.com/watch?v=trailer",
    "subtitles": [
      {"language": "en", "url": "https://your-server.com/subs_en.srt"}
    ],
    "quality": "1080p",
    "file_size": "2.5GB",
    "added_date": "2024-01-15",
    "tmdb_id": 12345
  }
]
```

## Usage

### Basic Navigation
1. **Open the addon** from Video Add-ons
2. **Browse categories**:
   - Movies (from TMDB)
   - TV Shows (from TMDB)
   - Search functionality
   - GitHub Collection (your custom content)

### Playing Content
- Click any movie/episode to play
- Subtitles are automatically loaded if available
- Use Kodi's standard playback controls

### Search
- Use "Search Movies" or "Search TV Shows"
- Enter your search term
- Browse results with full metadata

## Sample JSON Files

Check the `sample_json_files/` directory for:
- `movies.json` - Sample movie database
- `tvshows.json` - Sample TV show database  
- `featured.json` - Featured content
- `genres/` - Genre-specific collections
- `README.md` - Detailed JSON schema documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: This addon is for educational purposes. Ensure you have proper rights to any content you stream.