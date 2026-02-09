#!/usr/bin/env python3
"""
Warren Nolan Data Scraper

Scrapes warrennolan.com for NET rankings, RPI, SOS, bracket projections.

Usage:
    python3 warren_nolan.py net --top 25
    python3 warren_nolan.py bracket-projection
    python3 warren_nolan.py nitty-gritty --team "Duke"
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

class WarrenNolanScraper:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.base_url = "https://www.warrennolan.com"
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
    
    def get_net_rankings(self, top: int = None) -> List[Dict]:
        try:
            url = f"{self.base_url}/basketball/2024/net"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            rankings = []
            
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]
                for i, row in enumerate(rows):
                    if top and i >= top:
                        break
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 6:
                        rankings.append({
                            'net_rank': cells[0].get_text(strip=True),
                            'team': cells[1].get_text(strip=True),
                            'record': cells[2].get_text(strip=True),
                            'quadrant_1': cells[3].get_text(strip=True),
                            'quadrant_2': cells[4].get_text(strip=True),
                            'sos': cells[5].get_text(strip=True)
                        })
            
            return rankings
        except Exception as e:
            self.log(f"Error: {str(e)}")
            return []

def main():
    parser = argparse.ArgumentParser(description='Warren Nolan Data Scraper')
    parser.add_argument('command', choices=['net', 'bracket-projection', 'nitty-gritty'])
    parser.add_argument('--top', type=int, help='Limit results')
    parser.add_argument('--team', help='Team name')
    parser.add_argument('--pretty', action='store_true')
    parser.add_argument('--csv', action='store_true')
    parser.add_argument('--debug', action='store_true')
    
    args = parser.parse_args()
    scraper = WarrenNolanScraper(debug=args.debug)
    
    try:
        if args.command == 'net':
            result = scraper.get_net_rankings(args.top)
        else:
            result = {'error': 'Command not implemented yet'}
        
        print(scraper.format_output(result, args.pretty, args.csv))
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()