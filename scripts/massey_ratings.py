#!/usr/bin/env python3
"""
Massey Ratings Scraper

Scrapes masseyratings.com for composite computer rankings.

Usage:
    python3 massey_ratings.py composite --top 25
    python3 massey_ratings.py compare --systems 5
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

class MasseyRatingsScraper:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.base_url = "https://masseyratings.com"
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
    
    def get_composite_ratings(self, top: int = None) -> List[Dict]:
        try:
            url = f"{self.base_url}/cb/ncaa-d1/ratings"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            ratings = []
            
            # Look for main ratings table
            table = soup.find('table', id='ratingstable')
            if not table:
                table = soup.find('table')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for i, row in enumerate(rows):
                    if top and i >= top:
                        break
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        ratings.append({
                            'rank': cells[0].get_text(strip=True),
                            'team': cells[1].get_text(strip=True),
                            'rating': cells[2].get_text(strip=True),
                            'record': cells[3].get_text(strip=True) if len(cells) > 3 else None
                        })
            
            return ratings
        except Exception as e:
            self.log(f"Error: {str(e)}")
            return []

def main():
    parser = argparse.ArgumentParser(description='Massey Ratings Scraper')
    parser.add_argument('command', choices=['composite', 'compare'])
    parser.add_argument('--top', type=int, help='Top N teams')
    parser.add_argument('--systems', type=int, help='Number of systems to compare')
    parser.add_argument('--pretty', action='store_true')
    parser.add_argument('--csv', action='store_true')
    parser.add_argument('--debug', action='store_true')
    
    args = parser.parse_args()
    scraper = MasseyRatingsScraper(debug=args.debug)
    
    try:
        if args.command == 'composite':
            result = scraper.get_composite_ratings(args.top)
        else:
            result = {'error': 'Command not implemented yet'}
        
        print(scraper.format_output(result, args.pretty, args.csv))
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()