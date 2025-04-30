import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "."))  # or '..' if needed


from flask import Flask, request, jsonify
from flask_cors import CORS
from data_collectors.restaurant_collector import RestaurantCollector
from data_collectors.article_collector import get_review_articles
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def analyze_with_gemini(input_to_LLM: str) -> str:
    """Use Gemini to analyze reviews and articles to extract popular dishes"""
    model = genai.GenerativeModel('gemini-2.0-flash')    
    
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

    response = model.generate_content(prompt)
    return response.text

@app.route('/api/restaurant', methods=['POST'])
def get_restaurant_info():
    """Endpoint to get restaurant recommended dishes"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'address' not in data or 'location' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        restaurant_name = data['name']
        address = data['address']
        location = data['location']
        
        # Collect restaurant reviews and information
        collector = RestaurantCollector()
        restaurant_data = collector.find_restaurant(restaurant_name, address)
        
        # Collect review articles
        articles = get_review_articles(restaurant_name, location)
        
        # Process articles
        article_contents = ""
        if articles:
            for article in articles:
                article_contents += article['content']
        
        # Prepare input for Gemini analysis
        input_to_LLM = f"""
        Restaurant Name: {restaurant_name}
        Restaurant Reviews: {restaurant_data['reviews']}
        Restaurant Articles: {article_contents}
        """
        
        # Get recommended dishes analysis
        recommended_dishes = analyze_with_gemini(input_to_LLM)
        
        # Return both recommended dishes and place_id
        return jsonify({
            'recommended_dishes': recommended_dishes,
            'place_id': restaurant_data['place_id']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    # app.run(debug=True, port=5000) 
    app.run(host="0.0.0.0", port=10000)