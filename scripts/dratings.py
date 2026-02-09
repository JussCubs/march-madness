#!/usr/bin/env python3
"""
DRatings Predictions & Edge Finder

Scrapes dratings.com for computer predictions, power ratings, and betting analysis.
Compares model win probabilities vs implied odds to find betting edges.

Usage:
    python3 dratings.py predictions --date 2026-03-15
    python3 dratings.py today
    python3 dratings.py edge-finder --date today --min-edge 3.0
"""

import argparse
import json
import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

try:
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
except ImportError:
    print("Error: Required packages not installed. Install with: pip3 install requests beautifulsoup4 lxml pandas")
    sys.exit(1)

class DRatingsAnalyzer:
    """Scraper and analyzer for DRatings college basketball predictions."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.base_url = "https://www.dratings.com"
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
    
    def parse_date(self, date_str: str) -> str:
        """Parse date string and return in YYYY-MM-DD format."""
        if date_str.lower() == 'today':
            return datetime.now().strftime('%Y-%m-%d')
        elif date_str.lower() == 'tomorrow':
            return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            return date_str
    
    def odds_to_probability(self, odds: int) -> float:
        """Convert American odds to implied probability."""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    def probability_to_odds(self, prob: float) -> int:
        """Convert probability to American odds."""
        if prob > 0.5:
            return int(-prob / (1 - prob) * 100)
        else:
            return int((1 - prob) / prob * 100)
    
    def calculate_edge(self, model_prob: float, market_prob: float) -> float:
        """Calculate betting edge percentage."""
        if market_prob == 0:
            return 0
        return ((model_prob - market_prob) / market_prob) * 100
    
    def get_predictions(self, date: str = None) -> List[Dict]:
        """Get DRatings predictions for a specific date."""
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            else:
                date = self.parse_date(date)
            
            self.log(f"Getting DRatings predictions for {date}")
            
            # Try to find the college basketball predictions page
            url = f"{self.base_url}/college-basketball/predictions"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            predictions = []
            
            # Look for game prediction tables
            tables = soup.find_all('table')
            game_containers = soup.find_all(['div', 'tr'], class_=lambda x: x and 'game' in x.lower())
            
            # Try to parse predictions from various possible structures
            for container in game_containers:
                try:
                    game_data = self.parse_game_container(container, date)
                    if game_data:
                        predictions.append(game_data)
                except Exception as e:
                    self.log(f"Error parsing game container: {str(e)}")
                    continue
            
            # If no games found in containers, try table parsing
            if not predictions:
                for table in tables:
                    try:
                        table_predictions = self.parse_predictions_table(table, date)
                        predictions.extend(table_predictions)
                    except Exception as e:
                        self.log(f"Error parsing table: {str(e)}")
                        continue
            
            return predictions
            
        except Exception as e:
            self.log(f"Error getting predictions: {str(e)}")
            return []
    
    def parse_game_container(self, container, date: str) -> Optional[Dict]:
        """Parse individual game prediction container."""
        try:
            # Extract team names
            team_elements = container.find_all(['span', 'div'], class_=lambda x: x and 'team' in x.lower())
            if len(team_elements) < 2:
                return None
            
            away_team = team_elements[0].get_text(strip=True)
            home_team = team_elements[1].get_text(strip=True)
            
            # Extract prediction data
            prediction_elements = container.find_all(['span', 'div'], class_=lambda x: x and any(term in x.lower() for term in ['prob', 'spread', 'total']))
            
            game_data = {
                'date': date,
                'away_team': away_team,
                'home_team': home_team,
                'predictions': {
                    'model_win_prob_away': None,
                    'model_win_prob_home': None,
                    'predicted_spread': None,
                    'predicted_total': None
                },
                'market_data': {
                    'market_spread': None,
                    'market_total': None,
                    'away_ml_odds': None,
                    'home_ml_odds': None
                }
            }
            
            # Extract specific prediction values
            for elem in prediction_elements:
                text = elem.get_text(strip=True)
                # Add parsing logic based on DRatings format
                # This would need to be refined based on actual site structure
            
            return game_data
            
        except Exception as e:
            self.log(f"Error parsing game container: {str(e)}")
            return None
    
    def parse_predictions_table(self, table, date: str) -> List[Dict]:
        """Parse predictions from table format."""
        try:
            predictions = []
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 4:
                    continue
                
                try:
                    # Basic game data extraction
                    game_data = {
                        'date': date,
                        'away_team': cells[0].get_text(strip=True),
                        'home_team': cells[1].get_text(strip=True),
                        'predictions': {
                            'model_win_prob_away': None,
                            'model_win_prob_home': None,
                            'predicted_spread': None,
                            'predicted_total': None
                        },
                        'market_data': {
                            'market_spread': None,
                            'market_total': None
                        }
                    }
                    
                    # Extract numerical data from remaining cells
                    for i, cell in enumerate(cells[2:], 2):
                        text = cell.get_text(strip=True)
                        if '%' in text:
                            # Probability data
                            prob_value = float(text.replace('%', '')) / 100
                            if i == 2:
                                game_data['predictions']['model_win_prob_away'] = prob_value
                            elif i == 3:
                                game_data['predictions']['model_win_prob_home'] = prob_value
                        elif any(char.isdigit() for char in text):
                            # Numerical data (spreads, totals, etc.)
                            try:
                                num_value = float(text.replace('+', '').replace('-', ''))
                                if i == 4:
                                    game_data['predictions']['predicted_spread'] = num_value
                                elif i == 5:
                                    game_data['predictions']['predicted_total'] = num_value
                            except ValueError:
                                continue
                    
                    predictions.append(game_data)
                    
                except (ValueError, IndexError) as e:
                    self.log(f"Error parsing prediction row: {str(e)}")
                    continue
            
            return predictions
            
        except Exception as e:
            self.log(f"Error parsing predictions table: {str(e)}")
            return []
    
    def find_edges(self, date: str = None, min_edge: float = 2.0) -> List[Dict]:
        """Find betting edges by comparing model predictions to market odds."""
        try:
            predictions = self.get_predictions(date)
            
            edges = []
            
            for game in predictions:
                game_edges = []
                
                # Check moneyline edges
                away_model_prob = game['predictions'].get('model_win_prob_away')
                home_model_prob = game['predictions'].get('model_win_prob_home')
                
                away_ml_odds = game['market_data'].get('away_ml_odds')
                home_ml_odds = game['market_data'].get('home_ml_odds')
                
                if away_model_prob and away_ml_odds:
                    market_prob = self.odds_to_probability(away_ml_odds)
                    edge = self.calculate_edge(away_model_prob, market_prob)
                    if abs(edge) >= min_edge:
                        game_edges.append({
                            'type': 'moneyline',
                            'team': game['away_team'],
                            'side': 'away',
                            'model_prob': away_model_prob,
                            'market_prob': market_prob,
                            'edge_percent': edge,
                            'recommended_bet': 'YES' if edge > 0 else 'NO'
                        })
                
                if home_model_prob and home_ml_odds:
                    market_prob = self.odds_to_probability(home_ml_odds)
                    edge = self.calculate_edge(home_model_prob, market_prob)
                    if abs(edge) >= min_edge:
                        game_edges.append({
                            'type': 'moneyline',
                            'team': game['home_team'],
                            'side': 'home',
                            'model_prob': home_model_prob,
                            'market_prob': market_prob,
                            'edge_percent': edge,
                            'recommended_bet': 'YES' if edge > 0 else 'NO'
                        })
                
                # Add spread and total edges here (similar logic)
                
                if game_edges:
                    edge_game = {
                        'game': f"{game['away_team']} @ {game['home_team']}",
                        'date': game['date'],
                        'edges': game_edges,
                        'max_edge': max(abs(edge['edge_percent']) for edge in game_edges)
                    }
                    edges.append(edge_game)
            
            # Sort by maximum edge
            edges.sort(key=lambda x: x['max_edge'], reverse=True)
            
            return edges
            
        except Exception as e:
            self.log(f"Error finding edges: {str(e)}")
            return []
    
    def get_today_games(self) -> List[Dict]:
        """Get today's games with predictions and odds."""
        return self.get_predictions('today')

def main():
    parser = argparse.ArgumentParser(
        description='DRatings Predictions & Edge Finder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s predictions --date 2026-03-15
  %(prog)s today
  %(prog)s edge-finder --date today --min-edge 3.0
  %(prog)s edge-finder --min-edge 5.0
        '''
    )
    
    parser.add_argument('command', choices=[
        'predictions', 'today', 'edge-finder'
    ], help='Command to execute')
    
    parser.add_argument('--date', help='Date in YYYY-MM-DD format or "today"/"tomorrow"')
    parser.add_argument('--min-edge', type=float, default=2.0, help='Minimum edge percentage to report (default: 2.0)')
    
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    parser.add_argument('--csv', action='store_true', help='Output in CSV format')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    analyzer = DRatingsAnalyzer(debug=args.debug)
    result = None
    
    try:
        if args.command == 'predictions':
            result = analyzer.get_predictions(args.date)
            
        elif args.command == 'today':
            result = analyzer.get_today_games()
            
        elif args.command == 'edge-finder':
            result = analyzer.find_edges(args.date, args.min_edge)
        
        # Output result
        if result is not None:
            print(analyzer.format_output(result, args.pretty, args.csv))
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