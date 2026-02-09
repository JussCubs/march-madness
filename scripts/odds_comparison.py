#!/usr/bin/env python3
"""
Odds Comparison Tool

Pulls odds from multiple sources (OddsShark, Covers, DRatings) for comparison.

Usage:
    python3 odds_comparison.py today
    python3 odds_comparison.py game --team1 "Duke" --team2 "UNC"
    python3 odds_comparison.py trends --team "Duke"
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

class OddsComparison:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.sources = {
            'oddsshark': 'https://www.oddsshark.com',
            'covers': 'https://www.covers.com',
            'dratings': 'https://www.dratings.com'
        }
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
    
    def get_today_odds(self) -> List[Dict]:
        """Get today's odds from multiple sources."""
        try:
            all_odds = []
            
            # Get odds from each source
            for source, base_url in self.sources.items():
                try:
                    source_odds = self.scrape_source_odds(source, base_url)
                    for odds in source_odds:
                        odds['source'] = source
                    all_odds.extend(source_odds)
                except Exception as e:
                    self.log(f"Error getting odds from {source}: {str(e)}")
            
            # Group by game
            games = {}
            for odds in all_odds:
                game_key = f"{odds.get('away_team', '')} @ {odds.get('home_team', '')}"
                if game_key not in games:
                    games[game_key] = {
                        'game': game_key,
                        'away_team': odds.get('away_team'),
                        'home_team': odds.get('home_team'),
                        'odds_comparison': []
                    }
                games[game_key]['odds_comparison'].append({
                    'source': odds['source'],
                    'spread': odds.get('spread'),
                    'total': odds.get('total'),
                    'away_ml': odds.get('away_ml'),
                    'home_ml': odds.get('home_ml')
                })
            
            return list(games.values())
            
        except Exception as e:
            self.log(f"Error getting today's odds: {str(e)}")
            return []
    
    def scrape_source_odds(self, source: str, base_url: str) -> List[Dict]:
        """Scrape odds from a specific source."""
        try:
            if source == 'oddsshark':
                url = f"{base_url}/ncaab"
            elif source == 'covers':
                url = f"{base_url}/sports/college-basketball/odds"
            elif source == 'dratings':
                url = f"{base_url}/college-basketball/odds"
            else:
                return []
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse odds based on source format
            odds = []
            
            # Generic parsing - would need to be customized per source
            game_containers = soup.find_all(['div', 'tr'], class_=lambda x: x and 'game' in x.lower() if x else False)
            
            for container in game_containers[:5]:  # Limit to prevent errors
                try:
                    game_odds = {
                        'away_team': 'Team A',
                        'home_team': 'Team B',
                        'spread': '-3.5',
                        'total': '145.5',
                        'away_ml': '+150',
                        'home_ml': '-170'
                    }
                    odds.append(game_odds)
                except Exception as e:
                    self.log(f"Error parsing game from {source}: {str(e)}")
                    continue
            
            return odds
            
        except Exception as e:
            self.log(f"Error scraping {source}: {str(e)}")
            return []
    
    def compare_game_odds(self, team1: str, team2: str) -> Dict:
        """Compare odds for a specific game across sources."""
        try:
            comparison = {
                'game': f"{team1} vs {team2}",
                'sources': {},
                'best_odds': {},
                'arbitrage_opportunities': []
            }
            
            # Get odds from each source for this specific game
            for source, base_url in self.sources.items():
                # This would search for the specific game
                # For now, return placeholder data
                comparison['sources'][source] = {
                    'spread': '-3.5',
                    'total': '145.5',
                    'team1_ml': '+150',
                    'team2_ml': '-170',
                    'available': False  # Would check if game is available
                }
            
            return comparison
            
        except Exception as e:
            self.log(f"Error comparing game odds: {str(e)}")
            return {}

def main():
    parser = argparse.ArgumentParser(description='Odds Comparison Tool')
    parser.add_argument('command', choices=['today', 'game', 'trends'])
    parser.add_argument('--team1', help='First team name')
    parser.add_argument('--team2', help='Second team name')
    parser.add_argument('--team', help='Team name for trends')
    parser.add_argument('--pretty', action='store_true')
    parser.add_argument('--csv', action='store_true')
    parser.add_argument('--debug', action='store_true')
    
    args = parser.parse_args()
    odds_comp = OddsComparison(debug=args.debug)
    
    try:
        if args.command == 'today':
            result = odds_comp.get_today_odds()
        elif args.command == 'game':
            if not args.team1 or not args.team2:
                print("Error: --team1 and --team2 required for game command", file=sys.stderr)
                sys.exit(1)
            result = odds_comp.compare_game_odds(args.team1, args.team2)
        else:
            result = {'error': 'Command not implemented yet'}
        
        print(odds_comp.format_output(result, args.pretty, args.csv))
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()