#!/usr/bin/env python3
"""
Haslametrics Scraper

Scrapes haslametrics.com for computer predictions and analytics.

Usage:
    python3 haslametrics.py predictions --date today
    python3 haslametrics.py ratings --top 25
"""

import argparse
import json
import sys
import traceback
from typing import Dict, List, Any

try:
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
except ImportError:
    print("Error: Install with: pip3 install requests beautifulsoup4 lxml pandas")
    sys.exit(1)

class HaslametricsScraper:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.base_url = "https://haslametrics.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def log(self, message: str):
        if self.debug:
            print(f"[DEBUG] {message}", file=sys.stderr)
    
    def format_output(self, data: Any, pretty: bool = False, csv: bool = False) -> str:
        if csv and isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            return pd.DataFrame(data).to_csv(index=False)
        return json.dumps(data, indent=2 if pretty else None, default=str)
    
    def get_predictions(self, date: str = 'today') -> List[Dict]:
        try:
            url = f"{self.base_url}/ncaab-predictions"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            predictions = []
            
            # Parse prediction data
            game_containers = soup.find_all('div', class_=lambda x: x and 'prediction' in x.lower() if x else False)
            
            for container in game_containers:
                try:
                    prediction = {
                        'date': date,
                        'game': container.get_text(strip=True)[:50],  # Truncated
                        'prediction': 'See haslametrics.com for full data'
                    }
                    predictions.append(prediction)
                except Exception as e:
                    self.log(f"Error parsing prediction: {str(e)}")
            
            return predictions
        except Exception as e:
            self.log(f"Error: {str(e)}")
            return []

def main():
    parser = argparse.ArgumentParser(description='Haslametrics Scraper')
    parser.add_argument('command', choices=['predictions', 'ratings'])
    parser.add_argument('--date', default='today')
    parser.add_argument('--top', type=int)
    parser.add_argument('--pretty', action='store_true')
    parser.add_argument('--csv', action='store_true')
    parser.add_argument('--debug', action='store_true')
    
    args = parser.parse_args()
    scraper = HaslametricsScraper(debug=args.debug)
    
    try:
        if args.command == 'predictions':
            result = scraper.get_predictions(args.date)
        else:
            result = {'error': 'Command not implemented yet'}
        
        print(scraper.format_output(result, args.pretty, args.csv))
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()