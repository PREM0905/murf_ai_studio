# STUDIO - Technical Documentation & Code Walkthrough

## Architecture Overview

STUDIO follows a **client-server architecture** with a Flask backend and JavaScript frontend, implementing a **modular design pattern** for scalability and maintainability.

```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐
│   Frontend      │ ◄─────────────────► │   Backend       │
│   (JavaScript)  │                     │   (Flask)       │
└─────────────────┘                     └─────────────────┘
         │                                       │
         ▼                                       ▼
┌─────────────────┐                     ┌─────────────────┐
│ Browser APIs    │                     │ External APIs   │
│ - MediaRecorder │                     │ - AssemblyAI    │
│ - Web Audio     │                     │ - Murf AI       │
│ - DOM           │                     │ - Gemini AI     │
└─────────────────┘                     │ - NewsAPI       │
                                        │ - YouTube Music │
                                        │ - Google Maps   │
                                        └─────────────────┘

## Latest Updates

### **Music System Enhancement**
- **YouTube Music Integration**: Priority music search for better results
- **Instant Player**: Custom HTML player with autoplay support
- **Multi-Platform Fallback**: YouTube Music → YouTube → Search results
- **Clean AI Responses**: No URLs spoken, only "Playing [song]. Opening player..."

### **Personal Assistant Features**
- **Creator Recognition**: Responds to questions about Yash (creator)
- **Designer Recognition**: Responds to questions about Aditya (designer)
- **STUDIO Introduction**: Comprehensive system overview on request
- **Enhanced Help**: Updated feature list including all capabilities
```

---

## Backend Code Walkthrough

### 1. Main Server (`core/app.py`)

**Purpose**: Central Flask server handling all HTTP endpoints and routing

```python
# Lines 1-13: Import Dependencies
from flask import Flask, request, jsonify
from flask_cors import CORS  # Enable cross-origin requests
from dotenv import load_dotenv  # Environment variable management
```

**Why Used**: 
- Flask: Lightweight, easy to deploy, perfect for API services
- CORS: Allows frontend (different port) to communicate with backend
- dotenv: Secure API key management without hardcoding

```python
# Lines 14-20: Application Setup
app = Flask(__name__)
CORS(app)  # Enable all origins for development
# The server loads environment variables from `backend/config/.env` at startup
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env'))
```

**Scalability Consideration**: In production, restrict CORS to specific domains

```python
# Lines 22-24: FFmpeg Configuration
FFMPEG = r"C:\Program Files\Softdeluxe\Free Download Manager\ffmpeg.exe"
```

**Why Used**: FFmpeg converts WebM (browser format) to WAV (AssemblyAI format)
**Scalability**: Use Docker containers with FFmpeg pre-installed

### 2. ASR Endpoint (`/asr`)

**Purpose**: Handle voice input processing pipeline

```python
# Lines 26-35: Audio File Reception
if "audio" not in request.files:
    return jsonify({"ok": False, "error": "No audio file received"}), 400
```

**Pipeline Flow**:
1. **Receive WebM** → Browser's MediaRecorder output
2. **Convert to WAV** → AssemblyAI requirement
3. **Transcribe** → Speech-to-text
4. **Process** → Generate AI response
5. **Synthesize** → Text-to-speech
6. **Return** → JSON response with audio

**Scalability Improvements**:
- Add audio compression before upload
- Implement streaming transcription
- Use WebSocket for real-time processing
- Add audio caching mechanism

### 3. Text Endpoint (`/text`)

**Purpose**: Handle text input with optional TTS

```python
# Lines 125-140: Response Type Handling
if isinstance(reply_result, dict) and reply_result.get("type") == "navigation":
    # Navigation response with redirect URL
elif isinstance(reply_result, dict) and reply_result.get("type") == "search":
    # Search response with Gemini AI
elif isinstance(reply_result, dict) and reply_result.get("type") == "shutdown":
    # Shutdown command
```

**Design Pattern**: **Strategy Pattern** - Different response types handled uniformly
**Scalability**: Easy to add new response types (calendar, email, etc.)

### 4. Wake Word Endpoint (`/wake-word`)

**Purpose**: Continuous wake word detection

Notes:
- The `detect_wake_word` function now returns a tuple `(detected, job_id)` where `detected` is `True|False|None` and `job_id` is present when the backend queued an async cloud transcription job.
- When `WAKE_WORD_ASYNC=1` the endpoint may return a `job_id` that you can poll with `GET /transcription/<job_id>` to retrieve the final transcript and detection result.

```python
# Example response shapes from `/wake-word`:
# 1) Immediate Vosk detection:
#    {"ok": true, "wake_word_detected": true}
# 2) No detection, async cloud transcription queued:
#    {"ok": true, "wake_word_detected": null, "job_id": "..."}
# 3) Throttled / not detected:
#    {"ok": true, "wake_word_detected": false}
```

**Why Separate Endpoint**: 
- Lighter processing for continuous listening
- Different error handling requirements
- Optimized for speed over accuracy

**Polling Async Results**:
Use `GET /transcription/<job_id>` to check status. Returns:
```json
{"ok": true, "job": {"status":"pending|done|error", "result": <text|null>, "error": <msg|null>}}
```

---

## Core Logic (`simple_assistant.py`)

### 1. Import Structure

```python
# Lines 1-8: Modular Imports
from gemini_search import search_with_gemini, is_search_query
from youtube_search import get_first_youtube_video
```

**Design Pattern**: **Dependency Injection** - External services injected as modules
**Scalability**: Easy to swap AI providers or add new services

### 2. Processing Pipeline

```python
# Lines 55-70: Priority-Based Processing
def generate_reply(user_text):
    # 1. Personal questions (highest priority)
    # 2. Shutdown commands
    # 3. Music requests
    # 4. Greetings
    # 5. Weather/News/Navigation
    # 6. AI Search (fallback)
```

**Why This Order**:
- Personal responses create connection
- Shutdown prevents accidental triggers
- Music/greetings are common requests
- Functional features (weather/news)
- AI search as intelligent fallback

**Scalability**: Add priority scoring system for dynamic ordering

### 3. Response Types

```python
# Structured Response Pattern
return {
    "type": "navigation",  # Response category
    "message": "...",      # User-facing text
    "redirect_url": "...", # Action data
    "destination": "..."   # Metadata
}
```

**Benefits**:
- Consistent API contract
- Easy frontend handling
- Extensible for new features

---

## Frontend Architecture (`dual_script.js`)

### 1. Class-Based Design

```javascript
// Lines 1-15: STUDIOAssistant Class
class STUDIOAssistant {
    constructor() {
        this.isRecording = false;
        this.wakeWordActive = false;
        this.microphoneStream = null;
    }
}
```

**Design Pattern**: **Singleton Pattern** - One assistant instance
**Benefits**: State management, method organization, easy testing

### 2. Microphone Management

```javascript
// Lines 18-28: Single Permission Request
async requestMicrophonePermission() {
    this.microphoneStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.microphoneGranted = true;
}
```

**Why Single Request**: 
- Better UX (no repeated prompts)
- Shared stream for all recording functions
- Consistent audio quality

**Scalability**: Add audio device selection, quality settings

### 3. Wake Word Loop

```javascript
// Lines 250-270: Continuous Listening
this.wakeWordInterval = setInterval(() => {
    if (this.wakeWordRecorder && this.wakeWordRecorder.state === 'recording') {
        this.wakeWordRecorder.stop();
        setTimeout(() => {
            if (this.wakeWordActive) {
                this.wakeWordRecorder.start();
            }
        }, 100);
    }
}, 2000);
```

**Design**: **Observer Pattern** - Continuous monitoring with callbacks
**Optimization**: 2-second chunks balance responsiveness vs. processing load

---

## External Service Integrations

### 1. Speech Recognition (`asr_api.py`)

```python
# AssemblyAI Integration
def transcribe_file_assemblyai(audio_file_path):
    # Upload → Poll → Retrieve pattern
```

**Why AssemblyAI**: High accuracy, good API, reasonable pricing
**Alternatives**: Google Speech-to-Text, Azure Speech, Whisper API

### 2. Text-to-Speech (`murf_api.py`)

```python
# Murf AI Integration
def synthesize_text_murf(text):
    # Direct synthesis with voice selection
```

**Why Murf**: Natural voices, good quality, simple API
**Alternatives**: Google TTS, Amazon Polly, ElevenLabs

### 3. AI Search (`gemini_search.py`)

```python
# Gemini AI Integration
def search_with_gemini(query):
    # Generate answer + create targeted search URL
```

**Why Gemini**: Free tier, good responses, Google integration
**Enhancement**: Add conversation memory, context awareness

### 4. Music Integration (`simple_music.py`)

```python
# YouTube Music Integration
def get_instant_music_url(song_query):
    # Try YouTube Music first, fallback to YouTube
    # Create instant player with autoplay
```

**Why YouTube Music**: Music-focused results, better autoplay support
**Features**: Instant player, clean responses, multi-platform fallback

### 4. Wake Word Detection (`wake_word_detection.py`)

```python
# Custom Wake Word Logic
def detect_wake_word(webm_path):
    # Convert → Transcribe → Pattern Match
```

**Current Approach**: Simple keyword matching
**Scalability**: 
- Add machine learning models (Porcupine, Snowboy)
- Implement voice biometrics
- Add custom wake word training

---

## Scalability Enhancements

### 1. Performance Optimizations

**Current Bottlenecks**:
- FFmpeg conversion (2-3 seconds)
- AssemblyAI transcription (3-5 seconds)
- Sequential processing

**Solutions**:
```python
# Async Processing
import asyncio
async def process_audio_async(audio_data):
    tasks = [
        transcribe_audio(audio_data),
        prepare_tts_synthesis(),
        cache_common_responses()
    ]
    results = await asyncio.gather(*tasks)
```

### 2. Caching Layer

```python
# Response Caching
from functools import lru_cache
@lru_cache(maxsize=100)
def get_weather_cached(city):
    return get_weather_simple(city)
```

### 3. Database Integration

```sql
-- User Preferences
CREATE TABLE user_preferences (
    user_id VARCHAR(50),
    wake_word VARCHAR(20),
    voice_model VARCHAR(20),
    response_speed ENUM('fast', 'detailed')
);

-- Conversation History
CREATE TABLE conversations (
    id INT AUTO_INCREMENT,
    user_input TEXT,
    assistant_response TEXT,
    timestamp DATETIME,
    response_time_ms INT
);
```

### 4. Microservices Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gateway       │    │   ASR Service   │    │  TTS Service    │
│   (Load Balancer│ ──►│   (AssemblyAI)  │    │  (Murf AI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Logic Service  │    │  Search Service │    │  Music Service  │
│  (Assistant)    │    │  (Gemini AI)    │    │  (YouTube API)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 5. Advanced Features to Add

**1. Multi-Language Support**
```python
# Language Detection
from langdetect import detect
def detect_language(text):
    return detect(text)

# Multi-language responses
RESPONSES = {
    'en': {'greeting': 'Hello!'},
    'es': {'greeting': '¡Hola!'},
    'fr': {'greeting': 'Bonjour!'}
}
```

**2. Context Awareness**
```python
# Conversation Context
class ConversationContext:
    def __init__(self):
        self.history = []
        self.current_topic = None
        self.user_preferences = {}
    
    def add_interaction(self, user_input, response):
        self.history.append({
            'input': user_input,
            'response': response,
            'timestamp': datetime.now()
        })
```

**3. Plugin System**
```python
# Plugin Architecture
class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name, plugin_class):
        self.plugins[name] = plugin_class()
    
    def execute_plugin(self, name, *args):
        return self.plugins[name].execute(*args)
```

**4. Real-time Features**
```javascript
// WebSocket Integration
const ws = new WebSocket('ws://localhost:5000/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'live_transcription') {
        updateTranscriptionDisplay(data.text);
    }
};
```

**5. Mobile App Integration**
```python
# REST API for Mobile
@app.route('/api/v1/voice', methods=['POST'])
def mobile_voice_endpoint():
    # Optimized for mobile constraints
    # Compressed audio handling
    # Reduced response payload
```

---

## Security Considerations

### 1. API Key Management
```python
# Environment-based configuration
import os
from cryptography.fernet import Fernet

class SecureConfig:
    def __init__(self):
        self.cipher = Fernet(os.environ.get('ENCRYPTION_KEY'))
    
    def get_api_key(self, service):
        encrypted_key = os.environ.get(f'{service}_API_KEY_ENCRYPTED')
        return self.cipher.decrypt(encrypted_key).decode()
```

### 2. Input Validation
```python
# Sanitize user input
import re
def sanitize_input(text):
    # Remove potential injection attempts
    cleaned = re.sub(r'[<>"\']', '', text)
    return cleaned[:500]  # Limit length
```

### 3. Rate Limiting
```python
from flask_limiter import Limiter
limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@app.route('/asr', methods=['POST'])
@limiter.limit("10 per minute")
def asr_handler():
    # Rate-limited endpoint
```

---

## Monitoring & Analytics

### 1. Performance Metrics
```python
import time
from functools import wraps

def measure_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Log performance metrics
        logger.info(f"{func.__name__} took {end_time - start_time:.2f}s")
        return result
    return wrapper
```

### 2. Usage Analytics
```python
# Track feature usage
class Analytics:
    def __init__(self):
        self.usage_stats = defaultdict(int)
    
    def track_feature(self, feature_name):
        self.usage_stats[feature_name] += 1
        
    def get_popular_features(self):
        return sorted(self.usage_stats.items(), 
                     key=lambda x: x[1], reverse=True)
```

---

## Deployment Strategies

### 1. Docker Containerization
```dockerfile
FROM python:3.9-slim
RUN apt-get update && apt-get install -y ffmpeg
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 5000
CMD ["python", "app.py"]
```

### 2. Cloud Deployment
```yaml
# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: studio-assistant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: studio-assistant
  template:
    spec:
      containers:
      - name: studio-assistant
        image: studio:latest
        ports:
        - containerPort: 5000
```

### 3. CI/CD Pipeline
```yaml
# GitHub Actions
name: Deploy STUDIO
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run tests
      run: python -m pytest tests/
    - name: Deploy to production
      run: ./deploy.sh
```

---

## Testing Strategy

### 1. Unit Tests
```python
# test_assistant.py
import unittest
from simple_assistant import generate_reply

class TestAssistant(unittest.TestCase):
    def test_weather_request(self):
        response = generate_reply("weather in Mumbai")
        self.assertIn("Weather", response)
    
    def test_music_request(self):
        response = generate_reply("play despacito")
        self.assertEqual(response["type"], "music")
```

### 2. Integration Tests
```python
# test_endpoints.py
def test_asr_endpoint():
    with open('test_audio.wav', 'rb') as f:
        response = client.post('/asr', 
                             files={'audio': f})
    assert response.status_code == 200
```

### 3. Performance Tests
```python
# test_performance.py
import time
def test_response_time():
    start = time.time()
    response = generate_reply("weather in Mumbai")
    end = time.time()
    assert (end - start) < 2.0  # Must respond within 2 seconds
```

---

## Future Roadmap

### Phase 1: Core Improvements (1-2 months)
- WebSocket implementation for real-time communication
- Response caching system
- Better error handling and recovery
- Mobile-responsive frontend

### Phase 2: Advanced Features (3-4 months)
- Multi-language support
- Conversation context and memory
- Custom wake word training
- Voice biometrics for user identification

### Phase 3: Enterprise Features (6+ months)
- Multi-user support with authentication
- Admin dashboard and analytics
- Plugin marketplace
- Enterprise security features

### Phase 4: AI Enhancements
- Local AI models (Whisper, LLaMA)
- Emotion detection in voice
- Predictive responses
- Learning from user interactions

---

This technical documentation provides a comprehensive understanding of STUDIO's architecture, implementation details, and scalability considerations. The modular design allows for easy enhancement and maintenance while the clear separation of concerns enables team collaboration and feature development.