import httpx
from app.config import settings

class GoogleMapsService:
    """Google Maps API integration for geocoding and directions"""
    
    @staticmethod
    async def geocode_address(address: str) -> dict:
        """Convert address to latitude/longitude"""
        if not settings.GOOGLE_MAPS_API_KEY:
            return None
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params={
                        "address": address,
                        "key": settings.GOOGLE_MAPS_API_KEY
                    }
                )
                data = response.json()
                
                if data.get("status") == "OK" and data.get("results"):
                    location = data["results"][0]["geometry"]["location"]
                    return {
                        "latitude": location["lat"],
                        "longitude": location["lng"],
                        "formatted_address": data["results"][0]["formatted_address"]
                    }
            except Exception as e:
                print(f"Geocoding error: {e}")
        
        return None
    
    @staticmethod
    async def get_distance(origin_lat: float, origin_lng: float, 
                          dest_lat: float, dest_lng: float) -> dict:
        """Calculate distance and duration between two points"""
        if not settings.GOOGLE_MAPS_API_KEY:
            return None
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://maps.googleapis.com/maps/api/distancematrix/json",
                    params={
                        "origins": f"{origin_lat},{origin_lng}",
                        "destinations": f"{dest_lat},{dest_lng}",
                        "key": settings.GOOGLE_MAPS_API_KEY
                    }
                )
                data = response.json()
                
                if data.get("status") == "OK" and data.get("rows"):
                    element = data["rows"][0]["elements"][0]
                    if element.get("status") == "OK":
                        return {
                            "distance_meters": element["distance"]["value"],
                            "distance_text": element["distance"]["text"],
                            "duration_seconds": element["duration"]["value"],
                            "duration_text": element["duration"]["text"]
                        }
            except Exception as e:
                print(f"Distance calculation error: {e}")
        
        return None