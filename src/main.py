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
    
    # Updated prompt to consider both reviews and articles
    prompt = f"""
    You are a culinary expert analyzing restaurant reviews and articles. Your task is to identify the top 3 most recommended dishes from these sources.

    Important Guidelines:
    1. Consider both customer reviews and professional articles
    2. Give more weight to reviews with higher ratings (4 or 5 stars)
    3. Consider professional articles as expert opinions
    4. Look for consensus between multiple sources
    5. Note any specific preparation details or variations mentioned

    For each dish:
    1. Name the dish
    2. Explain why it's highly recommended, noting:
       - The ratings of supporting reviews
       - Whether it's mentioned in professional articles
       - Any consensus between sources
    3. Include 1-2 direct quotes from high-rated reviews that best describe the dish
    4. Include any relevant insights from professional articles
    5. Note any specific preparation details or variations mentioned

    Format your response as follows (NO MARKDOWN FORMATTING):
    
    Top 3 Most Recommended Dishes:
    
    1. [Dish Name]
    Description of why it's recommended: [description]
    Review Quote: "[exact quote]" (5-star review)
    Article Insight: "[relevant quote from article]"
    
    [Repeat for dishes 2 and 3]

    Important Formatting Rules:
    - Do not use any markdown formatting (no **, *, etc.)
    - Do not use bullet points
    - Use plain text only
    - Keep the format consistent across all dishes
    - Use exact quotes from both reviews and articles
    - Do not use the same quote for multiple dishes

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