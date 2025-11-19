# STUDIO - Intelligent Voice & Text Assistant

A comprehensive AI assistant with voice recognition, text-to-speech, weather reports, news updates, navigation, music playback, AI-powered search, wake word detection, and enhanced conversational capabilities.

## Features

- **Voice Recognition**: Record audio and convert to text using AssemblyAI
- **Wake Word Detection**: Say "Studio" for hands-free activation
- **Text-to-Speech**: Convert responses to speech using Murf AI
- **Weather Reports**: Real-time weather using wttr.in service
- **News Updates**: Latest headlines via NewsAPI
- **Smart Navigation**: Google Maps integration with automatic redirect
- **Music Playback**: YouTube Music integration with instant player and autoplay
- **AI-Powered Search**: Gemini AI integration with auto-redirect to search results
- **Personal Assistant**: Recognizes creator and designer with personalized responses
- **Smart Shutdown**: Voice/text commands to close the application
- **Comprehensive Greetings**: Polite responses to all greeting types
- **Time & Date**: Current time and date information

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure API Keys
Create `.env` file in backend directory with your API keys:
```bash
ASSEMBLYAI_API_KEY=your_assemblyai_key
MURF_API_KEY=your_murf_key
OPENAI_API_KEY=your_openai_key
NEWS_API_KEY=your_newsapi_key
```

**Note**: Weather service uses free wttr.in API (no key required)

### 3. Start the Server
```bash
python app.py
```

### 4. Open Frontend
Open `frontend/index.html` in your browser or run:
```bash
cd frontend
start index.html
```

## API Endpoints

- `POST /asr` - Voice recognition and processing
- `POST /text` - Text input with optional TTS
- `POST /wake-word` - Wake word detection
- `POST /test` - Simple test endpoint

## Usage Examples

**Voice Mode**: Click microphone and speak
- "Weather in Mumbai" - Get current weather
- "Latest technology news" - Fetch news headlines
- "Navigate to Central Park" - Auto-opens Google Maps
- "Play Despacito" - Opens instant music player with autoplay
- "Tell me about AI" - AI-powered search with auto-redirect
- "What time is it?" - Current time
- "Good morning" - Polite greeting responses
- "Who is Yash?" - Personal assistant responses
- "Shutdown Studio" - Close application

**Text Mode**: Type messages
- "Weather in London" - Weather reports
- "News about sports" - Topic-specific news
- "Song Bohemian Rhapsody" - Instant music player with YouTube Music
- "What is quantum physics?" - Search & learn with Gemini AI
- "Route from Mumbai to Delhi" - Navigation with auto-redirect
- "Good night" - Comprehensive greeting responses
- "Bye bye Studio" - Smart shutdown

**Wake Word Mode**: Say "Studio" for hands-free activation
- "Studio, weather in Tokyo" - Voice-activated commands
- "Studio, play some music" - Hands-free music control
- "Studio, navigate to airport" - Voice navigation

## Testing

Test the assistant functionality:
```bash
python test_simple.py
```

Test individual components:
- Voice recognition via `/asr` endpoint
- Text processing via `/text` endpoint
- Basic functionality via `/test` endpoint

## Project Structure

```
STUDIO_IITB/
├── backend/
│   ├── app.py                 # Main Flask server
│   ├── simple_assistant.py    # Core assistant logic (active)
│   ├── simple_music.py        # YouTube Music integration
│   ├── ytmusic_search.py      # YouTube Music search
│   ├── gemini_search.py       # AI search integration
│   ├── asr_api.py             # Speech recognition
│   ├── murf_api.py            # Text-to-speech
│   ├── wake_word_detection.py # Wake word processing
│   ├── requirements.txt       # Dependencies
│   └── .env                   # API keys
├── frontend/
│   ├── index.html             # Main interface
│   ├── instant_player.html    # Music player with autoplay
│   ├── dual_script.js         # Frontend logic with navigation
│   └── dual_style.css         # Reactor-style UI
└── README.md
```

## Required API Keys

1. **AssemblyAI** - Speech recognition (https://www.assemblyai.com/)
2. **Murf AI** - Text-to-speech (https://murf.ai/)
3. **Gemini AI** - Search and learning assistant (https://makersuite.google.com/app/apikey)
4. **NewsAPI** - News headlines (https://newsapi.org/)
5. **YouTube API** - Music and video search (https://console.developers.google.com/)

**Free Services Used:**
- **wttr.in** - Weather data (no API key required)
- **Google Maps** - Navigation (opens in browser)
- **YouTube** - Music playback (opens in browser)

## Key Features Explained

### Wake Word Detection
- Always-listening mode activated by saying "Studio"
- Hands-free operation for complete voice control
- Automatic command recording after wake word detection
- Continuous listening loop for seamless interaction

### Music Integration
- YouTube Music priority search for better music results
- Instant music player with autoplay support
- Supports "Play [song]", "Song [name]", "Music by [artist]"
- Custom player interface with fallback options
- Clean AI responses without speaking URLs

### AI-Powered Search & Learning
- Gemini AI integration for intelligent responses
- Automatic redirect to detailed search results after 1-second delay
- Enhanced search URLs for educational content
- Supports "Tell me about", "What is", "How to" queries

### Smart Navigation
- Automatically detects navigation requests
- Opens Google Maps in new tab with 1-second delay
- Supports both single destinations and route planning
- Example: "Navigate to Times Square" → Auto-opens Maps

### Personal Assistant Features
- Recognizes creator (Yash) and designer (Aditya) with personalized responses
- Comprehensive greeting system with proper etiquette
- Smart shutdown commands that close the application
- Context-aware responses based on user relationships

### Weather Integration
- Uses free wttr.in service for reliable weather data
- Supports any city worldwide
- Clean, formatted weather information

## Troubleshooting

**Server not starting**: Check if all dependencies are installed
**API errors**: Verify API keys in `.env` file
**Voice not working**: Ensure microphone permissions in browser
**Wake word not responding**: Check microphone permissions and try saying "Studio" clearly
**No audio output**: Check TTS settings and audio permissions
**Navigation/Music not opening**: Check browser popup settings and allow popups
**Search not redirecting**: Check popup blocker settings
**Shutdown not working**: Try "Bye bye Studio" or "Shutdown Studio"

## License

MIT License - See LICENSE file for details