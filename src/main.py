import os
from dotenv import load_dotenv
from data_collectors.restaurant_collector import RestaurantCollector
from data_collectors.article_collector import get_review_articles
import json

import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def analyze_with_gemini(input_to_LLM: str) -> str:
    """Use Gemini to analyze reviews and articles to extract popular dishes"""
    
    # Create the model
    model = genai.GenerativeModel('gemini-2.0-flash')    
    
    # Updated prompt to focus on dishes and their unique qualities
    prompt = f"""
    You are a culinary expert analyzing restaurant dishes. Your task is to identify the top 3 most recommended dishes and highlight what makes them special.

    Important Guidelines:
    1. Focus on the unique qualities and ingredients of each dish
    2. Highlight what makes each dish stand out
    3. Mention any special preparation methods or techniques
    4. Note any signature ingredients or flavor combinations
    5. Keep descriptions concise and focused on the dish itself

    For each dish:
    1. Name the dish
    2. Describe what makes it special:
       - Key ingredients and their quality
       - Unique preparation methods
       - Signature flavors or combinations
       - What sets it apart from similar dishes
    3. Include one brief quote that best captures the essence of the dish
    4. Note any specific details about how it's served or presented

    Format your response as follows (NO MARKDOWN FORMATTING):
    
    Top 3 Most Recommended Dishes:
    
    1. [Dish Name]
    What makes it special: [description focusing on ingredients, preparation, and unique qualities]
    Key Quote: "[one brief, impactful quote that captures the essence]"
    
    [Repeat for dishes 2 and 3]

    Important Formatting Rules:
    - Do not use any markdown formatting (no **, *, etc.)
    - Do not use bullet points
    - Use plain text only
    - Keep the format consistent across all dishes
    - Focus on the dish itself, not the reviews or articles
    - Keep descriptions concise and focused

    Input to analyze:
    {input_to_LLM}
    """

    # Generate response
    response = model.generate_content(prompt)
    return response.text

def collect_restaurant_reviews(restaurant_name: str, address: str) -> dict:
    """Collect restaurant reviews and basic information"""
    collector = RestaurantCollector()
    return collector.find_restaurant(restaurant_name, address)

def collect_restaurant_articles(restaurant_name: str, location: str) -> list:
    """Collect restaurant review articles"""
    return get_review_articles(restaurant_name, location)

def print_restaurant_info(restaurant_data):
    """Pretty print restaurant information"""
    print("\nRestaurant Information:")
    print(f"Name: {restaurant_data['name']}")
    print(f"Address: {restaurant_data['address']}")
    print(f"Rating: {restaurant_data.get('rating', 'N/A')}")
    
    # Print opening hours
    if restaurant_data.get('opening_hours'):
        print("\nOpening Hours:")
        for hours in restaurant_data['opening_hours']:
            print(hours)
    
    #Print website      
    if restaurant_data.get('website'):
        print(f"\nWebsite: {restaurant_data['website']}")
    
    #Print phone    
    if restaurant_data.get('phone'):
        print(f"Phone: {restaurant_data['phone']}")

def save_restaurant_data(restaurant_data):
    """
    Save restaurant data to a JSON file with a sanitized filename.
    Returns the filename that was used.
    """
    # Create a data directory if it doesn't exist
    data_dir = "restaurant_data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Sanitize the restaurant name for the filename
    # Remove special characters and spaces, convert to lowercase
    restaurant_name = restaurant_data['name']
    sanitized_name = "".join(c.lower() for c in restaurant_name if c.isalnum() or c.isspace())
    sanitized_name = sanitized_name.replace(" ", "_")
    
    # Add timestamp to ensure uniqueness
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{data_dir}/{sanitized_name}_{timestamp}.json"
    
    # Add metadata
    restaurant_data['metadata'] = {
        'collection_date': datetime.now().isoformat(),
        'original_name': restaurant_name,
        'file_version': '1.0'
    }
    
    # Save the data
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(restaurant_data, f, indent=2, ensure_ascii=False)
    
    return filename

def main():
    print("Welcome to Dishcovery - Restaurant Review Analyzer!")
    print("Please enter the restaurant details:")
    
    # Get user input
    restaurant_name = input("Restaurant Name: ")
    address = input("Address: ")
    location = input("Location (City, State): ")
    
    restaurant = {
        "name": restaurant_name,
        "address": address,
        "location": location
    }
    
    try:
        print(f"\nProcessing: {restaurant['name']}")
        print(f"Address: {restaurant['address']}")
        
        # Step 1: Collect restaurant reviews and basic information
        print("\nCollecting restaurant reviews and information...")
        restaurant_data = collect_restaurant_reviews(restaurant['name'], restaurant['address'])
        
        # Step 2: Collect review articles
        print("\nCollecting review articles...")
        articles = collect_restaurant_articles(restaurant['name'], restaurant['location'])
        
        # Add articles to restaurant data
        if len(articles) <= 0:
            print("No articles found for this restaurant")
        else:
            article_contents = ""
            for article in articles:
                article_contents += (article['content'])
        
        restaurant_data['articles'] = article_contents
        
        input_to_LLM = f"""
        Restaurant Name: {restaurant['name']}
        Restaurant Reviews: {restaurant_data['reviews']}
        Restaurant Articles: {article_contents}
        """
        
        # Add recommended dishes analysis
        restaurant_data['recommended_dishes'] = analyze_with_gemini(input_to_LLM)
        
        print("\nRecommended Dishes Analysis:")
        print(restaurant_data['recommended_dishes'])

        # Save to individual JSON file
        saved_filename = save_restaurant_data(restaurant_data)
        print(f"\nData has been saved to {saved_filename}")
        
    except Exception as e:
        print(f"Error processing {restaurant['name']}: {str(e)}")

if __name__ == "__main__":
    main() 