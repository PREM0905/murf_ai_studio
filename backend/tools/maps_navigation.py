def navigate_to(destination: str):
    """Simple navigation tool with error handling"""
    try:
        return {
            "destination": destination,
            "steps": [
                "Opening Google Maps...",
                f"Finding best route to {destination}...",
                "Navigation ready!"
            ]
        }
    except Exception as e:
        return {"error": f"Navigation error: {str(e)}"}