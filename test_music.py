from backend.multi_music_search import get_best_music_result

# Test the music search
song = "Despacito"
result = get_best_music_result(song)
print(f"Song: {song}")
print(f"Result: {result}")

if isinstance(result, dict):
    print(f"URL: {result['url']}")
    print(f"Primary Source: {result['primary_source']}")
    print(f"Song Title: {result['song_title']}")