# Dishcovery

A restaurant review and article analysis tool that uses AI to identify popular dishes from customer reviews and professional articles.

## Features

- Collects restaurant reviews and basic information
- Gathers professional review articles
- Uses Google's Gemini AI to analyze both sources
- Identifies top recommended dishes with supporting evidence
- Saves data in structured JSON format

## Requirements

- Python 3.8+
- Google Gemini API key
- SERP API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dishcovery.git
cd dishcovery
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```
GOOGLE_GEMINI_API_KEY=your_gemini_api_key
SERP_API_KEY=your_serp_api_key
```

## Usage

Run the main script:
```bash
python src/main.py
```

## Project Structure

```
dishcovery/
├── src/
│   ├── main.py
│   └── data_collectors/
│       ├── restaurant_collector.py
│       └── article_collector.py
├── restaurant_data/
├── restaurant_articles/
├── requirements.txt
├── .env
└── README.md
```

## License

MIT License