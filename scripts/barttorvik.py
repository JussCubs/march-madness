#!/usr/bin/env python3
"""
Barttorvik T-Rank Data Scraper

Scrapes barttorvik.com for T-Rank ratings, tempo-free analytics, game predictions,
and player metrics. Handles Cloudflare protection.

Usage:
    python3 barttorvik.py rankings --top 25
    python3 barttorvik.py team-stats --team "Duke"
    python3 barttorvik.py game-prediction --team1 "Duke" --team2 "UNC"
"""

import argparse
import json
import sys
import time
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
except ImportError as e:
    print(f"Error: Required package not installed. Install with: pip3 install requests beautifulsoup4 lxml pandas")
    sys.exit(1)

class BarttovikScraper:
    """Scraper for Barttorvik T-Rank college basketball data."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.base_url = "https://barttorvik.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def log(self, message: str):
        """Log debug messages if debug mode enabled."""
        if self.debug:
            print(f"[DEBUG] {message}", file=sys.stderr)
    
    def format_output(self, data: Any, pretty: bool = False, csv: bool = False) -> str:
        """Format output data as JSON, pretty JSON, or CSV."""
        if csv and isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict):
                df = pd.DataFrame(data)
                return df.to_csv(index=False)
        
        if pretty:
            return json.dumps(data, indent=2, default=str)
        else:
            return json.dumps(data, default=str)
    
    def get_with_retry(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Get URL with retry logic for Cloudflare protection."""
        for attempt in range(max_retries):
            try:
                self.log(f"Attempting to fetch {url} (attempt {attempt + 1})")
                
                response = self.session.get(url, timeout=30)
                
                # Check for Cloudflare challenge
                if "checking your browser" in response.text.lower() or response.status_code == 503:
                    self.log("Cloudflare challenge detected, waiting...")
                    time.sleep(5 * (attempt + 1))  # Exponential backoff
                    continue
                
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                self.log(f"Request failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
        
        return None
    
    def get_rankings(self, top: int = None, season: str = None) -> List[Dict]:
        """Get T-Rank team rankings."""
        try:
            if season is None:
                season = str(datetime.now().year)
            
            url = f"{self.base_url}/trank.php"
            if season:
                url += f"?year={season}"
            
            response = self.get_with_retry(url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the main rankings table
            table = soup.find('table', {'id': 'ratingsTable'})
            if not table:
                # Try alternative table selectors
                table = soup.find('table', {'class': 'tablesorter'})
                if not table:
                    self.log("Could not find rankings table")
                    return []
            
            rankings = []
            rows = table.find_all('tr')[1:]  # Skip header
            
            for i, row in enumerate(rows):
                if top and i >= top:
                    break
                    
                cells = row.find_all(['td', 'th'])
                if len(cells) < 8:  # Ensure enough columns
                    continue
                
                try:
                    rank_data = {
                        'rank': int(cells[0].get_text(strip=True)),
                        'team': cells[1].get_text(strip=True),
                        't_rank': float(cells[2].get_text(strip=True)) if cells[2].get_text(strip=True) != '-' else None,
                        'adj_oe': float(cells[3].get_text(strip=True)) if cells[3].get_text(strip=True) != '-' else None,
                        'adj_de': float(cells[4].get_text(strip=True)) if cells[4].get_text(strip=True) != '-' else None,
                        'adj_tempo': float(cells[5].get_text(strip=True)) if cells[5].get_text(strip=True) != '-' else None,
                        'record': cells[6].get_text(strip=True),
                        'conf_record': cells[7].get_text(strip=True) if len(cells) > 7 else None,
                        'season': season
                    }
                    rankings.append(rank_data)
                except (ValueError, IndexError) as e:
                    self.log(f"Error parsing row {i}: {str(e)}")
                    continue
            
            return rankings
            
        except Exception as e:
            self.log(f"Error getting rankings: {str(e)}")
            return []
    
    def get_team_stats(self, team: str, season: str = None) -> Dict:
        """Get detailed stats for a specific team."""
        try:
            if season is None:
                season = str(datetime.now().year)
            
            # First get team page URL
            url = f"{self.base_url}/team.php"
            params = {'team': team, 'year': season}
            
            response = self.get_with_retry(url, params=params)
            if not response:
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            team_data = {
                'team': team,
                'season': season,
                'stats': {}
            }
            
            # Look for stat tables
            tables = soup.find_all('table')
            
            for table in tables:
                # Try to identify what type of stats table this is
                headers = [th.get_text(strip=True) for th in table.find_all('th')]
                
                if any('rank' in h.lower() for h in headers):
                    # This looks like a rankings table
                    rows = table.find_all('tr')[1:]  # Skip header
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            stat_name = cells[0].get_text(strip=True)
                            stat_value = cells[1].get_text(strip=True)
                            team_data['stats'][stat_name] = stat_value
            
            return team_data
            
        except Exception as e:
            self.log(f"Error getting team stats: {str(e)}")
            return {}
    
    def get_game_prediction(self, team1: str, team2: str, neutral: bool = True) -> Dict:
        """Get game prediction between two teams."""
        try:
            # Note: This would require finding the specific prediction page format
            # For now, return a placeholder structure
            prediction = {
                'team1': team1,
                'team2': team2,
                'neutral_site': neutral,
                'prediction': {
                    'favorite': None,
                    'spread': None,
                    'total': None,
                    'win_probability': {
                        team1: None,
                        team2: None
                    }
                },
                'error': 'Game prediction functionality not yet implemented - need to analyze prediction page format'
            }
            
            return prediction
            
        except Exception as e:
            self.log(f"Error getting game prediction: {str(e)}")
            return {}
    
    def get_player_stats(self, team: str = None, season: str = None, top: int = None) -> List[Dict]:
        """Get player statistics."""
        try:
            if season is None:
                season = str(datetime.now().year)
            
            url = f"{self.base_url}/players.php"
            params = {'year': season}
            if team:
                params['team'] = team
            
            response = self.get_with_retry(url)
            if not response:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find player stats table
            table = soup.find('table', {'id': 'playersTable'})
            if not table:
                table = soup.find('table', {'class': 'tablesorter'})
                if not table:
                    self.log("Could not find player stats table")
                    return []
            
            players = []
            rows = table.find_all('tr')[1:]  # Skip header
            
            for i, row in enumerate(rows):
                if top and i >= top:
                    break
                    
                cells = row.find_all(['td', 'th'])
                if len(cells) < 5:
                    continue
                
                try:
                    player_data = {
                        'rank': i + 1,
                        'player': cells[0].get_text(strip=True),
                        'team': cells[1].get_text(strip=True),
                        'position': cells[2].get_text(strip=True) if len(cells) > 2 else None,
                        'rating': cells[3].get_text(strip=True) if len(cells) > 3 else None,
                        'season': season
                    }
                    
                    # Add additional stats if available
                    for j, cell in enumerate(cells[4:], 4):
                        player_data[f'stat_{j}'] = cell.get_text(strip=True)
                    
                    players.append(player_data)
                except (ValueError, IndexError) as e:
                    self.log(f"Error parsing player row {i}: {str(e)}")
                    continue
            
            return players
            
        except Exception as e:
            self.log(f"Error getting player stats: {str(e)}")
            return []

def main():
    parser = argparse.ArgumentParser(
        description='Barttorvik T-Rank Data Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s rankings --top 25
  %(prog)s rankings --season 2025
  %(prog)s team-stats --team "Duke"
  %(prog)s game-prediction --team1 "Duke" --team2 "UNC" --neutral
  %(prog)s player-stats --team "Duke" --top 10
        '''
    )
    
    parser.add_argument('command', choices=[
        'rankings', 'team-stats', 'game-prediction', 'player-stats'
    ], help='Command to execute')
    
    parser.add_argument('--top', type=int, help='Limit results to top N teams/players')
    parser.add_argument('--season', help='Season year (default: current)')
    parser.add_argument('--team', help='Team name')
    parser.add_argument('--team1', help='First team (for predictions)')
    parser.add_argument('--team2', help='Second team (for predictions)')
    parser.add_argument('--neutral', action='store_true', help='Neutral site game (for predictions)')
    
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    parser.add_argument('--csv', action='store_true', help='Output in CSV format')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    scraper = BarttovikScraper(debug=args.debug)
    result = None
    
    try:
        if args.command == 'rankings':
            result = scraper.get_rankings(args.top, args.season)
            
        elif args.command == 'team-stats':
            if not args.team:
                print("Error: --team is required for team-stats command", file=sys.stderr)
                sys.exit(1)
            result = scraper.get_team_stats(args.team, args.season)
            
        elif args.command == 'game-prediction':
            if not args.team1 or not args.team2:
                print("Error: --team1 and --team2 are required for game-prediction command", file=sys.stderr)
                sys.exit(1)
            result = scraper.get_game_prediction(args.team1, args.team2, args.neutral)
            
        elif args.command == 'player-stats':
            result = scraper.get_player_stats(args.team, args.season, args.top)
        
        # Output result
        if result is not None:
            print(scraper.format_output(result, args.pretty, args.csv))
        else:
            print("No data returned", file=sys.stderr)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("Operation cancelled", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        if args.debug:
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()