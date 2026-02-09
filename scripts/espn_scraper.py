#!/usr/bin/env python3
"""
ESPN Scraper - Direct ESPN API Access

Scrapes ESPN college basketball data including BPI ratings, scores, standings.

Usage:
    python3 espn_scraper.py scores --date today
    python3 espn_scraper.py bpi --top 25
    python3 espn_scraper.py schedule --team "Duke"
"""

import argparse
import json
import sys
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
except ImportError:
    print("Error: Required packages not installed. Install with: pip3 install requests beautifulsoup4 lxml pandas")
    sys.exit(1)

class ESPNScraper:
    """Scraper for ESPN college basketball data and BPI ratings."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.base_url = "https://www.espn.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def log(self, message: str):
        if self.debug:
            print(f"[DEBUG] {message}", file=sys.stderr)
    
    def format_output(self, data: Any, pretty: bool = False, csv: bool = False) -> str:
        if csv and isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            df = pd.DataFrame(data)
            return df.to_csv(index=False)
        return json.dumps(data, indent=2 if pretty else None, default=str)
    
    def get_bpi_rankings(self, top: int = None) -> List[Dict]:
        """Get ESPN BPI rankings."""
        try:
            url = f"{self.base_url}/mens-college-basketball/bpi"
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
                    if len(cells) >= 4:
                        rankings.append({
                            'rank': i + 1,
                            'team': cells[1].get_text(strip=True),
                            'bpi': cells[2].get_text(strip=True),
                            'record': cells[3].get_text(strip=True)
                        })
            
            return rankings
        except Exception as e:
            self.log(f"Error getting BPI: {str(e)}")
            return []
    
    def get_scores(self, date: str = None) -> List[Dict]:
        """Get scores for a specific date."""
        try:
            if date == 'today' or date is None:
                url = f"{self.base_url}/mens-college-basketball/scoreboard"
            else:
                # Convert date format if needed
                url = f"{self.base_url}/mens-college-basketball/scoreboard/_/date/{date.replace('-', '')}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            games = []
            
            # Parse game containers
            game_containers = soup.find_all('div', class_=lambda x: x and 'game' in x.lower() if x else False)
            
            for container in game_containers:
                try:
                    game_data = {
                        'date': date or datetime.now().strftime('%Y-%m-%d'),
                        'away_team': None,
                        'home_team': None,
                        'away_score': None,
                        'home_score': None,
                        'status': None
                    }
                    
                    # Extract team and score info
                    teams = container.find_all(['span', 'div'], class_=lambda x: x and 'team' in x.lower() if x else False)
                    if len(teams) >= 2:
                        game_data['away_team'] = teams[0].get_text(strip=True)
                        game_data['home_team'] = teams[1].get_text(strip=True)
                    
                    scores = container.find_all(['span', 'div'], class_=lambda x: x and 'score' in x.lower() if x else False)
                    if len(scores) >= 2:
                        try:
                            game_data['away_score'] = int(scores[0].get_text(strip=True))
                            game_data['home_score'] = int(scores[1].get_text(strip=True))
                        except ValueError:
                            pass
                    
                    games.append(game_data)
                except Exception as e:
                    self.log(f"Error parsing game: {str(e)}")
                    continue
            
            return games
        except Exception as e:
            self.log(f"Error getting scores: {str(e)}")
            return []

def main():
    parser = argparse.ArgumentParser(description='ESPN College Basketball Scraper')
    parser.add_argument('command', choices=['bpi', 'scores', 'schedule'])
    parser.add_argument('--top', type=int, help='Limit to top N teams')
    parser.add_argument('--date', help='Date for scores (YYYY-MM-DD or "today")')
    parser.add_argument('--team', help='Team name for schedule')
    parser.add_argument('--pretty', action='store_true', help='Pretty print output')
    parser.add_argument('--csv', action='store_true', help='CSV format')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    args = parser.parse_args()
    scraper = ESPNScraper(debug=args.debug)
    
    try:
        if args.command == 'bpi':
            result = scraper.get_bpi_rankings(args.top)
        elif args.command == 'scores':
            result = scraper.get_scores(args.date)
        else:
            result = []
        
        print(scraper.format_output(result, args.pretty, args.csv))
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()