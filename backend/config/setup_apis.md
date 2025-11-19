# API Keys Setup Guide

## Required APIs (Already Working)
✅ **AssemblyAI** - Speech-to-text
✅ **Murf** - Text-to-speech

## Optional APIs (For Enhanced Features)

### 1. OpenAI API (For General AI Conversation)
- Go to: https://platform.openai.com/api-keys
- Create account and get API key
- Add to .env: `OPENAI_API_KEY=your_key_here`
- **Enables**: General questions, explanations, creative tasks

### 2. News API (For Latest News)
- Go to: https://newsapi.org/register
- Free tier: 1000 requests/day
- Add to .env: `NEWS_API_KEY=your_key_here`
- **Enables**: "What's the latest news?"

### 3. Weather API (For Weather Updates)
- Go to: https://openweathermap.org/api
- Free tier: 1000 calls/day
- Add to .env: `WEATHER_API_KEY=your_key_here`
- **Enables**: "What's the weather in [city]?"

## Current Status
- ✅ Basic conversation (greetings, time, jokes, math)
- ✅ Voice input/output working
- ⚠️ Advanced features need API keys above