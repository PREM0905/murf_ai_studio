import os
import requests

# ==========================================================
# 1) GOOGLE → GET DRIVING DIRECTIONS (PRIMARY)
# ==========================================================
def get_directions(origin: str, destination: str):
    """
    Get worldwide driving directions using Google Maps Directions API.
    Falls back to MapBox if Google fails.
    """
    google_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if google_key:
        try:
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                "origin": origin,
                "destination": destination,
                "key": google_key,
                "mode": "driving"
            }

            resp = requests.get(url, params=params).json()

            if resp.get("status") == "OK":
                leg = resp["routes"][0]["legs"][0]

                steps = []
                for s in leg["steps"][:8]:
                    text = s["html_instructions"]
                    text = text.replace("<b>", "").replace("</b>", "")
                    text = text.replace("<div>", "").replace("</div>", "")
                    steps.append(text)

                return {
                    "service": "Google Maps",
                    "origin": origin,
                    "destination": destination,
                    "distance": leg["distance"]["text"],
                    "duration": leg["duration"]["text"],
                    "steps": steps,
                    "maps_url": f"https://www.google.com/maps/dir/{origin}/{destination}"
                }
        except:
            pass

    # Fallback → MapBox
    return get_directions_mapbox(origin, destination)


# ==========================================================
# 2) MAPBOX → DRIVING ROUTE (FALLBACK)
# ==========================================================
def get_directions_mapbox(origin: str, destination: str):
    """
    Backup navigation provider using MapBox Directions API.
    """
    mapbox_key = os.getenv("MAPBOX_API_KEY")
    if not mapbox_key:
        return {"error": "No Google or Mapbox API key configured."}

    try:
        # Geocode addresses → coordinates
        geo_url = "https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
        
        def geocode(place):
            r = requests.get(
                geo_url.format(query=place),
                params={"access_token": mapbox_key}
            ).json()
            coords = r["features"][0]["center"]
            return f"{coords[0]},{coords[1]}"

        origin_coords = geocode(origin)
        destination_coords = geocode(destination)

        # Directions
        url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{origin_coords};{destination_coords}"
        params = {
            "access_token": mapbox_key,
            "geometries": "geojson",
            "steps": "true"
        }

        resp = requests.get(url, params=params).json()

        if "routes" in resp:
            route = resp["routes"][0]
            duration_min = route["duration"] / 60
            distance_km = route["distance"] / 1000

            return {
                "service": "MapBox",
                "origin": origin,
                "destination": destination,
                "distance_km": round(distance_km, 1),
                "duration_min": round(duration_min, 1),
                "maps_url": f"https://www.google.com/maps/dir/{origin}/{destination}"
            }

    except Exception as e:
        return {"error": f"Mapbox failed: {str(e)}"}

    return {"error": "Could not compute route from any provider."}


# ==========================================================
# 3) NEARBY SEARCH (GOOGLE)
# ==========================================================
def find_nearby(location: str, place_type: str = "restaurant"):
    google_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not google_key:
        return {"error": "Missing GOOGLE_MAPS_API_KEY"}

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{place_type} near {location}",
        "key": google_key
    }

    resp = requests.get(url, params=params).json()

    results = []
    for place in resp.get("results", [])[:5]:
        results.append({
            "name": place["name"],
            "rating": place.get("rating", "N/A"),
            "address": place.get("formatted_address", "N/A")
        })

    return {
        "location": location,
        "place_type": place_type,
        "results": results,
        "maps_url": f"https://www.google.com/maps/search/{place_type}+near+{location}"
    }


# ==========================================================
# 4) SEARCH LOCATION
# ==========================================================
def search_location(query: str):
    google_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not google_key:
        return {"error": "Missing GOOGLE_MAPS_API_KEY"}

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": google_key}

    resp = requests.get(url, params=params).json()

    if not resp.get("results"):
        return {"error": f"No results for '{query}'"}

    best = resp["results"][0]

    return {
        "query": query,
        "name": best["name"],
        "address": best.get("formatted_address", "N/A"),
        "rating": best.get("rating", "N/A"),
        "maps_url": f"https://www.google.com/maps/place/{best['name'].replace(' ', '+')}"
    }
