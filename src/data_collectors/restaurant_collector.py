import requests
import os
from dotenv import load_dotenv
from typing import Dict, Optional, List
from datetime import datetime

load_dotenv()

class RestaurantCollector:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        self.details_url = "https://maps.googleapis.com/maps/api/place/details/json"

    def find_restaurant(self, name: str, address: Optional[str] = None) -> Dict:
        """
        Find a restaurant using the Google Places API
        """
        # Construct the input string
        input_str = name
        if address:
            input_str += f" {address}"

        # Required fields for initial search
        fields = "place_id,name,formatted_address,geometry,rating,user_ratings_total,types"
        
        params = {
            "input": input_str,
            "inputtype": "textquery",
            "fields": fields,
            "key": self.api_key
        }

        response = requests.get(self.base_url, params=params)
        data = response.json()

        if data.get("status") != "OK" or not data.get("candidates"):
            raise Exception(f"Failed to find restaurant: {data.get('status')}")

        # Get the first candidate
        candidate = data["candidates"][0]
        
        # Get additional details using place_id
        return self.get_place_details(candidate["place_id"])

    def get_place_details(self, place_id: str) -> Dict:
        """
        Get detailed information about a place using its place_id
        """
        fields = [
            "name",
            "formatted_address",
            "geometry",
            "rating",
            "user_ratings_total",
            "reviews",
            "types",
            "price_level",
            "website",
            "formatted_phone_number",
            "opening_hours"
        ]

        # First get the most relevant reviews
        params = {
            "place_id": place_id,
            "fields": ",".join(fields),
            "key": self.api_key
        }

        response = requests.get(self.details_url, params=params)
        data = response.json()

        if data.get("status") != "OK":
            raise Exception(f"Failed to get place details: {data.get('status')}")

        result = data["result"]
        
        # Get newest reviews
        newest_reviews = self._get_newest_reviews(place_id)
        
        # Combine and deduplicate reviews
        all_reviews = self._combine_reviews(
            result.get("reviews", []),
            newest_reviews
        )
        
        # Transform the data
        restaurant_data = {
            "place_id": place_id,
            "name": result.get("name"),
            "address": result.get("formatted_address"),
            "latitude": result["geometry"]["location"]["lat"],
            "longitude": result["geometry"]["location"]["lng"],
            "rating": result.get("rating"),
            "total_ratings": result.get("user_ratings_total"),
            "price_level": result.get("price_level"),
            "types": result.get("types", []),
            "website": result.get("website"),
            "phone": result.get("formatted_phone_number"),
            "opening_hours": result.get("opening_hours", {}).get("weekday_text", []),
            "reviews": self._process_reviews(all_reviews),
            "fetched_at": datetime.utcnow().isoformat()
        }

        return restaurant_data

    def _get_newest_reviews(self, place_id: str) -> List[Dict]:
        """Get newest reviews from the API"""
        params = {
            "place_id": place_id,
            "fields": "reviews",
            "reviews_sort": "newest",
            "key": self.api_key
        }

        response = requests.get(self.details_url, params=params)
        data = response.json()

        if data.get("status") != "OK":
            return []

        return data.get("result", {}).get("reviews", [])

    def _combine_reviews(self, relevant_reviews: List[Dict], newest_reviews: List[Dict]) -> List[Dict]:
        """Combine and deduplicate reviews based on author and time"""
        combined = {}
        
        # Add relevant reviews
        for review in relevant_reviews:
            key = (review.get("author_name"), review.get("time"))
            combined[key] = review
            
        # Add newest reviews
        for review in newest_reviews:
            key = (review.get("author_name"), review.get("time"))
            combined[key] = review
            
        return list(combined.values())

    def _process_reviews(self, reviews: list) -> list:
        """Process and clean review data"""
        processed_reviews = []
        for review in reviews:
            processed_reviews.append({
                "author": review.get("author_name"),
                "rating": review.get("rating"),
                "text": review.get("text"),
                "time": review.get("time"),
                "relative_time": review.get("relative_time_description")
            })
        return processed_reviews

    # def _process_photos(self, photos: list) -> list:
    #     """Process photo references"""
    #     processed_photos = []
    #     for photo in photos:
    #         processed_photos.append({
    #             "photo_reference": photo.get("photo_reference"),
    #             "width": photo.get("width"),
    #             "height": photo.get("height")
    #         })
    #     return processed_photos 