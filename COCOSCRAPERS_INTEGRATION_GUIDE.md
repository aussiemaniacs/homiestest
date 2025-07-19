# MovieStream + Cocoscrapers Integration - How It Works

## 🎯 **User Experience**

1. **Browse Movies**: User sees TMDB movies with posters
2. **Select Movie**: Click on any movie
3. **Source Scraping**: Cocoscrapers searches multiple sites for streams
4. **Progress Dialog**: Shows "Searching for sources..." with progress
5. **Source Selection**: User chooses from found sources (or auto-play best)
6. **Video Playback**: Stream plays in Kodi player

## 🔧 **Technical Flow**

### **Movie Selection**
```python
# User clicks movie → calls play_movie_cocoscrapers()
play_movie_cocoscrapers(title="Avengers", year="2019", tmdb_id="123")
```

### **Source Scraping**
```python
# CocoScrapersClient scrapes multiple sites
sources = cocoscrapers_client.scrape_movie_sources(
    title="Avengers", 
    year="2019",
    tmdb_id="123"
)

# Returns list of sources:
[
    {
        "provider": "StreamSite1",
        "url": "https://stream1.com/movie123",
        "quality": "1080p",
        "size": "2.1GB",
        "info": ["direct"]
    },
    {
        "provider": "StreamSite2", 
        "url": "https://stream2.com/watch/456",
        "quality": "720p",
        "size": "1.4GB",
        "info": ["cached"]
    }
]
```

### **Source Resolution**
```python
# Selected source is resolved to direct playable URL
resolved_url = cocoscrapers_client.resolve_source(selected_source)

# Returns direct stream URL:
"https://directstream.com/video.mp4?token=xyz123"
```

### **Playback**
```python
# Kodi plays the resolved URL
list_item = xbmcgui.ListItem(path=resolved_url)
xbmcplugin.setResolvedUrl(plugin_handle, True, list_item)
```

## ✨ **Features Added**

### **1. Smart Source Selection**
- Auto-rank sources by quality (4K > 1080p > 720p > 480p)
- Filter by preferred quality
- Show provider info and file sizes
- Direct link preference

### **2. Progress Dialogs**
- "Searching for sources..." during scraping
- "Resolving source..." during URL resolution
- User can cancel anytime

### **3. Fallback System**
- If Cocoscrapers not installed → Use direct links/samples
- If no sources found → Play sample video
- If resolution fails → Try next source

### **4. Context Menus**
- Right-click movies for options:
  - "Play with Cocoscrapers"
  - "Play Direct Link"

### **5. Settings**
- Auto-play best source (true/false)
- Maximum sources to show (5-50)
- Quality filter (All/480p/720p/1080p/4K)
- Scraper timeout (10-60 seconds)

## 🎮 **User Controls**

### **Source Selection Dialog**
```
Select source for: Avengers (2019)

[1] PremiumStream - 1080p (2.1GB) [direct, cached]
[2] StreamHub - 720p (1.4GB) [direct] 
[3] VideoSite - 720p [stream]
[4] MovieHost - 480p [cam]

Cancel
```

### **Settings Options**
```
Cocoscrapers Settings:
├── Auto-play Best Source: [OFF]
├── Maximum Sources: [20]  
├── Quality Filter: [All]
├── Enable Debrid Services: [OFF]
└── Scraper Timeout: [30 sec]
```

## 🔄 **Error Handling**

1. **Cocoscrapers Not Available**:
   - Show status message
   - Fall back to direct links
   - Guide user to install module

2. **No Sources Found**:
   - Show notification
   - Play sample video as fallback

3. **Resolution Failure**:
   - Try next best source
   - Show error if all fail
   - Fall back to samples

## 🎯 **Benefits**

### **For Users**
- **More Content**: Access to streaming sources beyond direct links
- **Better Quality**: Choose preferred video quality
- **Reliable Playback**: Multiple fallback options
- **User Control**: Select sources or auto-play

### **For Developers**
- **Modular Design**: Easy to enable/disable Cocoscrapers
- **Extensible**: Can add more scraping modules
- **Robust**: Handles failures gracefully
- **Configurable**: Many user settings