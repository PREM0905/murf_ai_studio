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
From thTR4e project root run the backend server (PowerShell / Windows):
```powershell
python .\backend\core\app.py
```
The server loads environment variables from `backend/config/.env`.

### 4. Open Frontend
Open `frontend/index.html` in your browser or run:
```bash
cd frontend
start index.html
```

## API Endpoints

- `POST /asr` - Voice recognition and processing
- `POST /text` - Text input with optional TTS
- `POST /wake-word` - Wake word detection (may return `job_id` when async)
- `GET /transcription/<job_id>` - Query status/result for an async transcription submitted by `/wake-word`
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

## Technical Architecture

### Backend Components

**Flask Server (app.py)**
- Main application server handling HTTP requests
- Endpoints: `/asr`, `/text`, `/test`
- Audio processing and response generation
- TTS integration with optional audio output

**Assistant Logic (simple_assistant.py)**
- Core response generation engine
- Pattern matching for weather, news, navigation
- Direct API calls to wttr.in and NewsAPI
- Navigation object responses for frontend redirect

**Enhanced Assistant (assistant_logic.py)**
- OpenAI GPT-4o-mini integration with function calling
- Dynamic tool selection for weather and news
- Response caching for performance
- Math operations and entertainment features

**Speech Recognition (asr_api.py)**
- AssemblyAI integration for voice-to-text
- Audio file upload and processing
- Real-time transcription handling

**Text-to-Speech (murf_api.py)**
- Murf AI integration for speech synthesis
- Audio generation and streaming
- Voice customization options

### Frontend Components

**Main Interface (index.html)**
- Dual-mode UI: voice recording and text input
- Microphone controls and audio visualization
- TTS toggle and response display
- Reactor-style design with animations

**JavaScript Logic (dual_script.js)**
- Audio recording using MediaRecorder API
- Form submission handling for text input
- Navigation redirect processing with window.open()
- Response parsing and UI updates

**Styling (dual_style.css)**
- Reactor-themed interface design
- Responsive layout and animations
- Button states and visual feedback

### API Integration Details

**Weather Service (wttr.in)**
```python
url = f"https://wttr.in/{city}?format=%C+%t+%h+%w"
# Returns: condition, temperature, humidity, wind
```

**News Service (NewsAPI)**
```python
url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"
# Returns: articles with title, description, url
```

**Navigation Response Format**
```python
{
    "type": "navigation",
    "message": "Opening Google Maps...",
    "redirect_url": "https://www.google.com/maps/search/destination",
    "destination": "destination_name"
}
```

### Data Flow

1. **Voice Input**: Audio → AssemblyAI → Text → Assistant → Response
2. **Text Input**: Text → Assistant → Response → Optional TTS
3. **Navigation**: Request → Pattern Match → Navigation Object → Frontend Redirect
4. **Weather**: City Extract → wttr.in API → Formatted Response
5. **News**: Query Extract → NewsAPI → Article List → Summary

### Error Handling

- **API Failures**: Graceful degradation with fallback responses
- **Network Issues**: Offline assistant mode available
- **Audio Errors**: User feedback and retry mechanisms
- **Invalid Requests**: Clear error messages and suggestions

### Performance Optimizations

- **Response Caching**: LRU cache for frequent queries
- **Async Processing**: Non-blocking API calls
- **Minimal Dependencies**: Lightweight library selection
- **Frontend Optimization**: Efficient DOM manipulation

### Security Considerations

- **API Key Protection**: Environment variables only
- **Input Validation**: Sanitized user inputs
- **CORS Handling**: Proper cross-origin policies
- **Audio Privacy**: No persistent audio storage

## Development Guide

### Adding New Features

1. **Pattern Recognition**: Add keywords to `simple_assistant.py`
2. **API Integration**: Create new function in assistant logic
3. **Frontend Handling**: Update `dual_script.js` for special responses
4. **Testing**: Add test cases to `test_simple.py`

### Debugging

- **Server Logs**: Check console output for API errors
- **Network Tab**: Monitor API requests in browser
- **Audio Issues**: Verify microphone permissions
- **Response Format**: Validate JSON structure for navigation

### Deployment

- **Local**: Flask development server (port 5000)
- **Production**: WSGI server (Gunicorn recommended)
- **Environment**: Set API keys in production environment
- **Dependencies**: Install from requirements.txt

## License

MIT License - See LICENSE file for details