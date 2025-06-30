# Installation Guide for MovieStream Kodi Addon

## Prerequisites

- **Kodi 21** or later
- **Internet connection** for metadata fetching
- **Python 3.x** (included with Kodi 21)

## Quick Installation

### Step 1: Download the Addon

1. Download all files from this repository as a ZIP file
2. Or clone the repository: `git clone [repository-url]`

### Step 2: Install in Kodi

1. **Open Kodi**
2. **Navigate to Add-ons**:
   - Main menu → Add-ons
3. **Install from ZIP**:
   - Click the package installer icon (box icon)
   - Select "Install from zip file"
   - Browse to your downloaded ZIP file
   - Select the ZIP file and confirm installation

### Step 3: First Run

1. **Find the addon**:
   - Go to Add-ons → Video add-ons
   - Look for "MovieStream"
2. **Launch the addon**:
   - Click on MovieStream to open
   - You should see the main menu with categories

## Configuration

### Basic Settings

1. **Access Settings**:
   - Right-click on MovieStream addon
   - Select "Settings" or "Configure"

2. **Key Settings**:
   - **TMDB API Key**: Pre-configured (you can use your own)
   - **GitHub Repository URL**: Set to your GitHub raw URL
   - **Enable GitHub Sync**: Turn on for custom content
   - **Video Quality**: Set preferred quality
   - **Subtitle Language**: Choose your language

### GitHub Integration Setup

1. **Create a GitHub Repository**:
   ```
   https://github.com/yourusername/moviestream-database
   ```

2. **Upload Sample JSON Files**:
   - Copy files from `sample_json_files/` directory
   - Upload to your GitHub repository
   - Ensure files are in the root directory

3. **Configure Addon**:
   - Set GitHub Repository URL to:
   ```
   https://raw.githubusercontent.com/yourusername/moviestream-database/main/
   ```

## Testing the Installation

### Test TMDB Integration

1. **Open MovieStream**
2. **Click "Movies"**
3. **Verify**:
   - Movies load with posters
   - Metadata displays correctly
   - You can browse through pages

### Test Video Playback

1. **Select any movie**
2. **Click to play**
3. **Verify**:
   - Video starts playing
   - Subtitles appear if available
   - Playback controls work

### Test GitHub Integration

1. **Click "GitHub Collection"**
2. **Verify**:
   - Your custom content appears
   - Movies from your JSON files load
   - Custom metadata displays

## Troubleshooting

### Common Issues

#### 1. Addon Won't Install
- **Check Kodi Version**: Must be Kodi 21+
- **Check ZIP File**: Ensure all files are included
- **Check Dependencies**: Addon should install automatically

#### 2. No Movies Loading
- **Check Internet**: Verify connection
- **Check TMDB API**: May need your own API key
- **Check Kodi Logs**: Look for error messages

#### 3. GitHub Content Not Loading
- **Check URL**: Verify GitHub repository URL
- **Check JSON Files**: Validate JSON syntax
- **Check File Permissions**: Ensure files are public

#### 4. Videos Won't Play
- **Check Video URLs**: Test in web browser
- **Check Network**: Verify internet connection
- **Check Video Format**: Ensure Kodi supports format

### Getting Help

1. **Check Kodi Logs**:
   - Settings → System → Logging
   - Enable debug logging
   - Check log file for errors

2. **Test Components**:
   - Test TMDB API separately
   - Test video URLs in browser
   - Validate JSON files online

## File Structure

After installation, your addon should have this structure:

```
plugin.video.moviestream/
├── addon.xml
├── main.py
├── icon.png
├── fanart.jpg
├── resources/
│   ├── settings.xml
│   ├── language/
│   │   └── resource.language.en_gb/
│   │       └── strings.po
│   └── lib/
│       ├── __init__.py
│       ├── tmdb_client.py
│       ├── github_client.py
│       └── video_player.py
└── sample_json_files/
    ├── movies.json
    ├── tvshows.json
    ├── featured.json
    ├── genres/
    │   ├── action.json
    │   └── animation.json
    └── README.md
```

## Next Steps

1. **Customize Your Database**:
   - Edit the JSON files in your GitHub repository
   - Add your own movie/TV show data
   - Test changes in the addon

2. **Advanced Configuration**:
   - Set up multiple video sources
   - Configure subtitle providers
   - Customize the interface

3. **Maintain Your Database**:
   - Regularly update JSON files
   - Add new content as needed
   - Monitor for broken links

## Support

- **Documentation**: Check README.md for detailed info
- **Sample Files**: Use sample_json_files/ as templates
- **Community**: Join Kodi forums for help

---

**Happy streaming!** 🎬