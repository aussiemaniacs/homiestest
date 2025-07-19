# MovieStream Pro 2.0 - Complete Installation & Setup Guide

## 🎯 **What You're Getting**

**MovieStream Pro 2.0** is the ultimate Kodi streaming addon featuring:

### ✨ **Core Features**
- 🎬 **Movies**: TMDB integration with 20,000+ movies
- 📺 **TV Shows**: Full season/episode support with auto-next
- 🔍 **Search**: Advanced search across all content
- ⭐ **Watchlist**: Personal watchlist management
- ❤️ **Favorites**: Favorite movies and shows
- 📖 **History**: Watch history with resume points
- 📊 **Statistics**: Detailed usage statistics

### 🚀 **Advanced Features**
- 🎭 **Cocoscrapers**: Automatic source scraping from 50+ sites
- 💎 **Debrid Services**: Real-Debrid, Premiumize, All-Debrid support
- 📋 **GitHub Database**: Custom editable movie/TV databases
- 🎬 **Multiple Sources**: Automatic fallback between sources
- 📝 **Subtitles**: 10 language support with auto-download
- 🎮 **Context Menus**: Right-click actions throughout

## 📋 **Requirements**

### **Essential**
- ✅ Kodi 21 (or newer)
- ✅ Internet connection

### **Optional (for full features)**
- 🎭 Cocoscrapers addon (`script.module.cocoscrapers`)
- 💎 Debrid service account (Real-Debrid, Premiumize, etc.)
- 📁 GitHub repository for custom databases

## 🛠️ **Installation Steps**

### **Step 1: Download Required Files**

Upload these files to your GitHub repository (`https://github.com/aussiemaniacs/homiestest`):

#### **Root Files**
```
addon.xml              # Main addon configuration
main.py               # Complete addon logic (750+ lines)
icon.png              # Addon icon (256x256)
fanart.jpg            # Addon fanart (1920x1080)
```

#### **Resources Folder**
```
resources/
├── settings.xml                           # Addon settings
├── language/
│   └── resource.language.en_gb/
│       └── strings.po                    # Language strings
└── lib/
    ├── __init__.py                       # Package init
    ├── cocoscrapers_client.py           # Cocoscrapers integration
    ├── debrid_client.py                 # Debrid services
    ├── tvshow_client.py                 # TV show management
    └── watchlist_manager.py             # Watchlist/favorites
```

#### **Sample Database**
```
movies.json           # Sample movies database
tvshows.json         # Sample TV shows database  
featured.json        # Featured content
```

### **Step 2: GitHub Repository Setup**

1. **Go to**: https://github.com/aussiemaniacs/homiestest
2. **Upload files** using GitHub web interface or git commands
3. **Verify structure** matches the layout above

### **Step 3: Basic Kodi Installation**

1. **Download ZIP**: https://github.com/aussiemaniacs/homiestest/archive/refs/heads/main.zip
2. **Rename folder**: Extract and rename to `plugin.video.moviestream`
3. **Install in Kodi**:
   - Method A: Copy folder to `[Kodi]/addons/plugin.video.moviestream/`
   - Method B: Create ZIP and install via Kodi → Add-ons → Install from ZIP

### **Step 4: Enhanced Installation (Full Features)**

#### **Install Cocoscrapers**
```
1. Find script.module.cocoscrapers addon
2. Install in Kodi via repository or ZIP
3. Restart Kodi
4. MovieStream will detect it automatically
```

#### **Setup Debrid Services (Optional)**
```
Real-Debrid:
1. Sign up at real-debrid.com
2. Get API key from account settings
3. Enter in MovieStream → Settings → Debrid Services

Premiumize:
1. Sign up at premiumize.me
2. Get API key from account
3. Enter in addon settings

All-Debrid:
1. Sign up at alldebrid.com
2. Get API key from account
3. Enter in addon settings
```

## ⚙️ **Configuration**

### **First Launch Setup**

1. **Open MovieStream** from Video Add-ons
2. **Go to Settings**:
   - TMDB API Key: Pre-configured
   - GitHub URL: `https://raw.githubusercontent.com/aussiemaniacs/homiestest/main/`
   - Enable features as needed

### **Recommended Settings**

```
🎬 Playback Settings:
├── Video Quality: 1080p
├── Auto-play Best Source: OFF (choose sources)
├── Buffer Size: 20MB
└── Auto Next Episode: ON

🎭 Cocoscrapers Settings:
├── Enable Cocoscrapers: ON
├── Maximum Sources: 25
├── Scraper Timeout: 40 seconds
└── Quality Filter: All

⭐ Watchlist Settings:
├── Enable Watchlist: ON
├── Auto-remove Watched: OFF
└── Mark Watched at: 90%
```

## 🎮 **How to Use**

### **Main Menu Navigation**
```
🎬 Movies
├── Popular Movies          # TMDB popular movies
├── Top Rated Movies        # Highest rated
├── Now Playing            # Currently in theaters
├── Upcoming Movies        # Coming soon
└── Search Movies          # Search TMDB

📺 TV Shows  
├── Popular TV Shows       # TMDB popular shows
├── Top Rated TV Shows     # Highest rated
├── Airing Today          # Airing today
└── Search TV Shows       # Search shows

⭐ My Lists
├── Watchlist (50)        # Your watchlist
├── Favorites (25)        # Favorite content
├── Watch History (100)   # Recently watched
└── Resume (10)           # Resume points

📁 GitHub Collection       # Your custom database
⚙️ Tools                   # Addon tools & stats
🔧 Settings               # Addon configuration
```

### **Playing Content**

1. **Browse** any category (Movies, TV Shows, etc.)
2. **Click** on any item
3. **Cocoscrapers** automatically finds sources
4. **Choose source** from the list (or auto-play best)
5. **Watch** with full metadata and subtitles

### **Managing Lists**

```
Add to Watchlist:
- Right-click any item → "Add to Watchlist"

Add to Favorites:
- Right-click any item → "Add to Favorites"

Resume Playback:
- Addon automatically saves resume points
- Next time you play, it asks to resume
```

## 🎯 **Advanced Features**

### **Source Selection**
- 🔍 **Automatic**: Finds 10-30 sources per movie/episode
- 🏆 **Quality Ranking**: 4K > 1080p > 720p > 480p
- 💎 **Debrid Priority**: Premium sources listed first
- ⚡ **Fast Resolution**: Sources resolve in 2-5 seconds

### **TV Show Features**
- 📺 **Full Seasons**: Browse complete seasons
- 📝 **Episode Info**: Full metadata for each episode
- ⏭️ **Auto Next**: Automatically play next episode
- 🔄 **Resume**: Resume from where you stopped

### **Watchlist & Favorites**
- ⭐ **Personal Lists**: Manage your own content lists
- 📊 **Statistics**: Track your viewing habits
- 🔄 **Auto-Sync**: Sync with cloud services (optional)
- 📖 **History**: Complete watch history

### **GitHub Integration**
- 📁 **Custom Database**: Create your own movie/TV databases
- ✏️ **Easy Editing**: Edit JSON files via GitHub web interface
- 🔄 **Auto-Update**: Addon updates when you edit files
- 🌐 **Shareable**: Share your databases with others

## 🛠️ **Customization**

### **Adding Your Own Content**

1. **Edit movies.json** on GitHub:
```json
{
  "id": "my_movie_001",
  "title": "My Custom Movie",
  "year": 2024,
  "video_url": "https://myserver.com/movie.mp4",
  "poster_url": "https://myserver.com/poster.jpg",
  "plot": "Description of my movie..."
}
```

2. **Edit tvshows.json** for TV shows
3. **Save changes** - addon updates automatically

### **Video Sources**

Support for multiple source types:
- **Direct URLs**: MP4, MKV, AVI files
- **Streaming**: HLS, DASH streams  
- **CDN**: Amazon S3, Google Cloud, etc.
- **Custom**: Your own video servers

## 🔧 **Troubleshooting**

### **Common Issues**

#### **No Sources Found**
```
Solutions:
1. Install script.module.cocoscrapers
2. Check internet connection
3. Try different movie/show
4. Check Kodi logs for errors
```

#### **Playback Fails**
```
Solutions:
1. Increase buffer size in settings
2. Try different source from list
3. Check video URL accessibility
4. Update Kodi to latest version
```

#### **Addon Won't Load**
```
Solutions:
1. Check all files are present
2. Verify folder name: plugin.video.moviestream
3. Restart Kodi completely
4. Check Kodi logs for Python errors
```

### **Getting Logs**

```
Kodi Log Locations:
- Android: /storage/emulated/0/Android/data/org.xbmc.kodi/cache/kodi.log
- Windows: %APPDATA%\Kodi\kodi.log
- Linux: ~/.kodi/temp/kodi.log
- Mac: ~/Library/Logs/kodi.log
```

## 📊 **Performance Tips**

### **Optimization Settings**
```
For Best Performance:
├── Buffer Size: 20-50MB (higher for 4K)
├── Cache Metadata: ON
├── Maximum Sources: 15-25
├── Scraper Timeout: 30-60 seconds
└── Auto-play Best Source: ON (faster)
```

### **Network Optimization**
- 🌐 Use wired connection for 4K content
- 📡 Ensure stable internet (10+ Mbps for 1080p)
- 🔄 Enable source caching for faster loading

## 🎉 **You're Ready!**

Your **MovieStream Pro 2.0** addon now includes:

✅ **20,000+ Movies** from TMDB  
✅ **10,000+ TV Shows** with full episodes  
✅ **Automatic Source Finding** via Cocoscrapers  
✅ **Premium Debrid Support** for high-quality streams  
✅ **Personal Watchlist & Favorites**  
✅ **Custom GitHub Databases**  
✅ **Professional Kodi Interface**  

**Start watching immediately with sample content, then customize with your own sources!**

---

## 🆘 **Support & Updates**

- 📖 **Documentation**: Check README.md for details
- 🐛 **Issues**: Report on GitHub repository
- 🔄 **Updates**: Pull latest from GitHub repository
- 💬 **Community**: Join Kodi forums for help

**Enjoy your premium streaming experience!** 🎬✨