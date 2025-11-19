# backend/free_translation.py

import requests
import json

def translate_with_mymemory(text, target_lang="es", source_lang="en"):
    """Free translation using MyMemory API - No API key needed"""
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {
            'q': text,
            'langpair': f"{source_lang}|{target_lang}"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['responseStatus'] == 200:
            translated = data['responseData']['translatedText']
            return f"Translation: {translated}"
        else:
            return "Sorry, I couldn't translate that right now."
    except Exception as e:
        return "I'm having trouble with translation right now."

def translate_with_libretranslate(text, target_lang="es", source_lang="en"):
    """Free translation using LibreTranslate - No API key needed"""
    try:
        url = "https://libretranslate.de/translate"
        data = {
            'q': text,
            'source': source_lang,
            'target': target_lang,
            'format': 'text'
        }
        
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        
        if 'translatedText' in result:
            return f"Translation: {result['translatedText']}"
        else:
            return "Sorry, I couldn't translate that right now."
    except Exception as e:
        return "I'm having trouble with translation right now."

def detect_language(text):
    """Detect language using free service"""
    try:
        url = "https://ws.detectlanguage.com/0.2/detect"
        data = {'q': text}
        
        response = requests.post(url, data=data, timeout=5)
        result = response.json()
        
        if result['data']['detections']:
            return result['data']['detections'][0]['language']
        return 'en'
    except:
        return 'en'

def translate_text_free(text, target_lang="es"):
    """Main translation function using free services"""
    # Language code mapping
    lang_map = {
        'spanish': 'es', 'french': 'fr', 'german': 'de', 'italian': 'it',
        'portuguese': 'pt', 'russian': 'ru', 'chinese': 'zh', 'japanese': 'ja',
        'korean': 'ko', 'arabic': 'ar', 'hindi': 'hi', 'dutch': 'nl'
    }
    
    # Convert language name to code
    if target_lang.lower() in lang_map:
        target_lang = lang_map[target_lang.lower()]
    
    # Try MyMemory first (more reliable)
    result = translate_with_mymemory(text, target_lang)
    if "Translation:" in result:
        return result
    
    # Fallback to LibreTranslate
    return translate_with_libretranslate(text, target_lang)