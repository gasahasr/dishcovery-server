import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_article_text(url: str) -> Optional[Dict[str, str]]:
    """
    Fetches and parses article text from a given URL.
    
    Args:
        url (str): The URL of the article to scrape
        
    Returns:
        Optional[Dict[str, str]]: Dictionary containing 'title' and 'content',
                                 or None if extraction fails
    """
    # Set up proper headers to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }
    
    try:
        # Make the request with a timeout
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract title - try different common title tags
        title = None
        title_tags = soup.find_all(['h1', 'title'])
        for tag in title_tags:
            if tag.text.strip():
                title = tag.text.strip()
                break
        
        # Extract main content - focus on article and main content areas
        content_tags = soup.find_all(['article', 'main', 'div'], class_=['content', 'article-content', 'post-content'])
        
        if not content_tags:
            # Fallback to all paragraphs if no specific content area is found
            paragraphs = soup.find_all('p')
        else:
            # Get paragraphs within the main content area
            paragraphs = content_tags[0].find_all('p')
        
        # Filter out empty paragraphs and join the text
        content = "\n\n".join([
            p.text.strip() 
            for p in paragraphs 
            if p.text.strip() and len(p.text.strip()) > 20  # Minimum length to filter out short snippets
        ])
        
        if not title or not content:
            logging.warning(f"Could not extract complete content from {url}")
            return None
            
        return {
            "title": title,
            "content": content,
            "url": url
        }
        
    except requests.RequestException as e:
        logging.error(f"Error fetching article from {url}: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error parsing article from {url}: {str(e)}")
        return None

def get_review_articles(restaurant_name: str, location: str) -> List[Dict[str, str]]:
    """
    Fetches review articles for a restaurant using SERP API and extracts their content.
    
    Args:
        restaurant_name (str): Name of the restaurant
        location (str): Location of the restaurant (city, state)
        
    Returns:
        List[Dict[str, str]]: List of dictionaries containing article data
    """
    # Get SERP API key from environment variables
    serp_api_key = os.getenv('SERP_API_KEY')
    if not serp_api_key:
        raise ValueError("SERP API key not found in environment variables")

    # Construct the search query
    search_query = f"{restaurant_name} {location} restaurant review"
    
    # SERP API endpoint
    serp_url = "https://serpapi.com/search"
    
    # Parameters for the SERP API call
    params = {
        "api_key": serp_api_key,
        "q": search_query,
        "num": 10,  # Number of results to return
        "tbm": "nws",  # Search news articles
        "tbs": "qdr:y"  # Results from the past year
    }
    
    try:
        # Make the API call to SERP
        response = requests.get(serp_url, params=params)
        response.raise_for_status()
        search_results = response.json()
        
        # Process each search result
        articles = []
        
        for result in search_results.get('news_results', []):
            article_url = result.get('link')
            if not article_url:
                continue
                
            # Get the full article text using existing function
            article_content = get_article_text(article_url)
            
            if article_content:
                # Add metadata from SERP results
                article_content.update({
                    'source': result.get('source', 'Unknown'),
                    'published_date': result.get('date', 'Unknown'),
                    'snippet': result.get('snippet', ''),
                    'restaurant_name': restaurant_name,
                    'location': location
                })
                
                articles.append(article_content)
        
        return articles
    
    except requests.RequestException as e:
        logging.error(f"Error making SERP API request: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error processing search results: {str(e)}")
        return []

def save_articles_to_json(articles: List[Dict[str, str]], restaurant_name: str):
    """
    Saves the collected articles to a JSON file.
    
    Args:
        articles (List[Dict[str, str]]): List of article data
        restaurant_name (str): Name of the restaurant for filename
    """
    import json
    from datetime import datetime
    
    # Create directory if it doesn't exist
    os.makedirs('restaurant_articles', exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    sanitized_name = "".join(c.lower() for c in restaurant_name if c.isalnum() or c.isspace()).replace(' ', '_')
    filename = f"restaurant_articles/{sanitized_name}_articles_{timestamp}.json"
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'restaurant_name': restaurant_name,
            'collection_date': datetime.now().isoformat(),
            'articles': articles
        }, f, indent=2, ensure_ascii=False)
    
    return filename

# Example usage
if __name__ == "__main__":
    # Test both article collection and content extraction
    test_cases = [
        {
            "restaurant": "Din Tai Fung",
            "location": "Los Angeles, CA"
        },
    ]
    
    for test_case in test_cases:
        print(f"\nFetching articles for {test_case['restaurant']} in {test_case['location']}")
        
        articles = get_review_articles(test_case['restaurant'], test_case['location'])
        
        if articles:
            print(f"Found {len(articles)} articles")
            filename = save_articles_to_json(articles, test_case['restaurant'])
            print(f"Articles saved to {filename}")
            
            # Print preview of first article
            if articles:
                print("\nPreview of first article:")
                print(f"Title: {articles[0]['title']}")
                print(f"Source: {articles[0]['source']}")
                print(f"Published: {articles[0]['published_date']}")
                print(f"Content preview: {articles[0]['content'][:200]}...")
        else:
            print("No articles found or error occurred")