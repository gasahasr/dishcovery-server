import requests
import os
from dotenv import load_dotenv
from typing import Dict, Optional, List
from datetime import datetime
import logging

load_dotenv()

class RestaurantCollector:
    def __init__(self):
        self.api_key = os.getenv("SERP_API_KEY")
        if not self.api_key:
            raise ValueError("SERP API key not found in environment variables")
        self.base_url = "https://serpapi.com/search"

    def find_restaurant(self, name: str, address: Optional[str] = None) -> Dict:
        """
        Find a restaurant using the Yelp Reviews API
        """
        # First, get the Yelp place ID using Yelp Search API
        place_id = self._get_yelp_place_id(name, address)
        # print(f"Place ID: {place_id}")
        if not place_id:
            raise Exception("Failed to find restaurant on Yelp")
        
        # Get reviews using the place ID
        return self.get_place_details(place_id)

    def _get_yelp_place_id(self, name: str, address: Optional[str] = None) -> Optional[str]:
        """
        Get Yelp place ID using Yelp Search API
        """
        print(f"\nSearching for Yelp place ID for: {name} in {address}")
        
        # Construct the search query
        params = {
            "api_key": self.api_key,
            "engine": "yelp",
            "find_desc": name,
            "find_loc": address if address else "United States"
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract the first result's place ID from organic results
            if data.get("organic_results"):
                first_result = data["organic_results"][0]
                print(f"Found first result: {first_result.get('title')}")
                # Get the first place ID from the place_ids array
                if first_result.get("place_ids"):
                    place_id = first_result["place_ids"][0]
                    print(f"Extracted place ID: {place_id}")
                    return place_id
            
            print(f"No Yelp place ID found for {name} in {address}")
            return None

        except Exception as e:
            print(f"Error getting Yelp place ID: {str(e)}")
            return None

    def get_place_details(self, place_id: str) -> Dict:
        """
        Get detailed information about a place using its Yelp place_id
        """
        print(f"\nFetching details for place ID: {place_id}")
        
        # Parameters for Yelp Reviews API
        params = {
            "api_key": self.api_key,
            "engine": "yelp_reviews",
            "place_id": place_id,
            "sortby": "date_desc",  # Get newest reviews first
            "num": 49,  # Maximum number of reviews
            "hl": "en"  # English language
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data.get("reviews"):
                print("No reviews found in the response")
                raise Exception("No reviews found")

            print(f"Found {len(data.get('reviews', []))} reviews")
            print(f"Total results available: {data.get('search_information', {}).get('total_results', 0)}")
            
            # Transform the data
            restaurant_data = {
                "place_id": place_id,
                "name": data.get("search_information", {}).get("business", ""),
                "address": None,  # Not available in reviews API
                "rating": None,   # Not available in reviews API
                "total_ratings": data.get("search_information", {}).get("total_results", 0),
                "price_level": None,  # Not available in reviews API
                "website": None,  # Not available in reviews API
                "phone": None,    # Not available in reviews API
                "opening_hours": None,  # Not available in reviews API
                "reviews": self._process_reviews(data.get("reviews", [])),
                "fetched_at": datetime.utcnow().isoformat()
            }

            print(f"\nRestaurant Details:")
            print(f"Name: {restaurant_data['name']}")
            print(f"Total Reviews: {restaurant_data['total_ratings']}")
            print(f"Number of processed reviews: {len(restaurant_data['reviews'])}")

            return restaurant_data

        except Exception as e:
            print(f"Error getting place details: {str(e)}")
            raise

    def _process_reviews(self, reviews: list) -> list:
        """Process and clean review data"""
        print(f"\nProcessing {len(reviews)} reviews...")
        processed_reviews = []
        for review in reviews:
            # Extract user information
            user = review.get("user", {})
            
            # Extract comment information
            comment = review.get("comment", {})
            
            # Extract feedback information
            feedback = review.get("feedback", {})
            
            # Extract owner replies
            owner_replies = review.get("owner_replies", [])
            owner_reply = owner_replies[0] if owner_replies else None
            
            processed_review = {
                "author": user.get("name"),
                "user_id": user.get("user_id"),
                "user_location": user.get("address"),
                "user_reviews": user.get("reviews"),
                "user_photos": user.get("photos"),
                "rating": review.get("rating"),
                "text": comment.get("text"),
                "language": comment.get("language"),
                "date": review.get("date"),
                "position": review.get("position"),
                "feedback": {
                    "useful": feedback.get("useful", 0),
                    "funny": feedback.get("funny", 0),
                    "cool": feedback.get("cool", 0)
                },
                "owner_reply": {
                    "text": owner_reply.get("comment") if owner_reply else None,
                    "date": owner_reply.get("date") if owner_reply else None,
                    "owner_name": owner_reply.get("owner", {}).get("name") if owner_reply else None
                } if owner_reply else None,
                "photos": review.get("photos", []),
                "tags": review.get("tags", [])
            }
            
            processed_reviews.append(processed_review)
            print(f"Processed review from {processed_review['author']} - Rating: {processed_review['rating']}")
            if processed_review['owner_reply']:
                print(f"  - Has owner reply from {processed_review['owner_reply']['owner_name']}")
        
        print(f"Successfully processed {len(processed_reviews)} reviews")
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