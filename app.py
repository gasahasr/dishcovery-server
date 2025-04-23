from flask import Flask, render_template, request, jsonify
from src.main import collect_restaurant_reviews, collect_restaurant_articles, analyze_with_gemini
import os
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import bcrypt
import jwt
from functools import wraps

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MongoDB connection
uri = "mongodb+srv://dishcovery:dishcovery@dishcovery.mdkrho7.mongodb.net/?retryWrites=true&w=majority&appName=dishcovery"
client = MongoClient(uri, server_api=ServerApi('1'), tlsAllowInvalidCertificates=True)
db = client['dishcovery']

# Collections
users = db['users']
restaurants = db['restaurants']
favorites = db['favorites']
reviews = db['reviews']

# User Schema
user_schema = {
    'email': str,
    'password': str,
    'name': str,
    'created_at': datetime,
    'preferences': {
        'notification_radius': float,
        'active_time_windows': list,
        'max_daily_notifications': int,
        'preferred_cuisines': list,
        'blacklisted_restaurants': list
    }
}

def save_search_data(search_data):
    """
    Save search data to a JSON file
    """
    # Create searches directory if it doesn't exist
    searches_dir = "searches"
    os.makedirs(searches_dir, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{searches_dir}/search_{timestamp}.json"
    
    # Add metadata
    search_data['timestamp'] = datetime.now().isoformat()
    
    # Save the data
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(search_data, f, indent=2, ensure_ascii=False)
    
    return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        
        # Save the search data
        search_data = {
            'name': data['name'],
            'address': data['address'],
            'location': data['location'],
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string
        }
        save_search_data(search_data)
        
        # Collect restaurant reviews and basic information
        restaurant_data = collect_restaurant_reviews(data['name'], data['address'])
        
        # Collect review articles
        articles = collect_restaurant_articles(data['name'], data['location'])
        
        # Add articles to restaurant data
        article_contents = ""
        if len(articles) == 0:
            print("DEBUG: No articles found")
        else:
            for article in articles:
                article_contents += article['content']
        
        restaurant_data['articles'] = article_contents
        
        # Prepare input for Gemini
        input_to_LLM = f"""
        Restaurant Name: {data['name']}
        Restaurant Reviews: {restaurant_data['reviews']}
        Restaurant Articles: {article_contents}
        """
        
        # Analyze with Gemini
        restaurant_data['recommended_dishes'] = analyze_with_gemini(input_to_LLM)
        
        return jsonify(restaurant_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return jsonify({'message': 'Invalid token!'}), 401
        except:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Authentication routes
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if users.find_one({'email': data['email']}):
        return jsonify({'message': 'User already exists!'}), 400
    
    # Hash password
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    # Create user
    user = {
        'email': data['email'],
        'password': hashed_password,
        'name': data['name'],
        'created_at': datetime.utcnow(),
        'preferences': {
            'notification_radius': 1000,  # Default 1km
            'active_time_windows': [],
            'max_daily_notifications': 5,
            'preferred_cuisines': [],
            'blacklisted_restaurants': []
        }
    }
    
    users.insert_one(user)
    return jsonify({'message': 'User created successfully!'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = users.find_one({'email': data['email']})
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    
    if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        return jsonify({'message': 'Invalid password!'}), 401
    
    # Generate token
    token = jwt.encode({
        'user_id': str(user['_id']),
        'exp': datetime.utcnow() + timedelta(days=1)
    }, app.config['SECRET_KEY'])
    
    return jsonify({
        'token': token,
        'user': {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user['name']
        }
    })

# Protected route example
@app.route('/user/preferences', methods=['GET'])
@token_required
def get_preferences(current_user):
    return jsonify(current_user['preferences'])

if __name__ == '__main__':
    app.run(debug=True) 