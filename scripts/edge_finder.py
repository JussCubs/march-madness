#!/usr/bin/env python3
"""
Edge Finder - The Money Maker

Pulls predictions from multiple models, compares against betting lines,
and outputs ranked edges with confidence scores for profitable opportunities.

Usage:
    python3 edge_finder.py scan --date today --min-edge 3.0
    python3 edge_finder.py today --sources all
    python3 edge_finder.py backtest --start-date 2025-03-01
"""

import argparse
import json
import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import subprocess

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("Error: Required packages not installed. Install with: pip3 install pandas numpy")
    sys.exit(1)

class EdgeFinder:
    """Find profitable betting opportunities by comparing model predictions to market odds."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.available_sources = [
            'barttorvik', 'dratings', 'kenpom', 'haslametrics', 'massey'
        ]
        
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
        if market_prob <= 0:
            return 0
        return ((model_prob - market_prob) / market_prob) * 100
    
    def kelly_criterion(self, edge_prob: float, market_prob: float, bankroll: float = 1000) -> float:
        """Calculate optimal bet size using Kelly Criterion."""
        if market_prob <= 0 or edge_prob <= 0:
            return 0
        
        odds = (1 / market_prob) - 1
        edge = edge_prob - market_prob
        
        if edge <= 0:
            return 0
        
        kelly_fraction = edge / odds
        optimal_bet = bankroll * kelly_fraction
        
        # Cap at 5% of bankroll for safety
        return min(optimal_bet, bankroll * 0.05)
    
    def run_script(self, script_name: str, args: List[str]) -> Dict:
        """Run one of the other scripts and return parsed JSON result."""
        try:
            cmd = ['python3', f'scripts/{script_name}.py'] + args
            self.log(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                self.log(f"Script {script_name} failed: {result.stderr}")
                return {}
            
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError as e:
                self.log(f"Failed to parse JSON from {script_name}: {str(e)}")
                return {}
                
        except subprocess.TimeoutExpired:
            self.log(f"Script {script_name} timed out")
            return {}
        except Exception as e:
            self.log(f"Error running {script_name}: {str(e)}")
            return {}
    
    def get_multi_source_predictions(self, date: str, sources: List[str]) -> Dict[str, List[Dict]]:
        """Get predictions from multiple sources."""
        predictions = {}
        
        for source in sources:
            self.log(f"Getting predictions from {source}")
            
            if source == 'barttorvik':
                # Get T-Rank predictions (would need to implement game prediction functionality)
                data = self.run_script('barttorvik', ['rankings', '--top', '50'])
                predictions[source] = data
                
            elif source == 'dratings':
                data = self.run_script('dratings', ['predictions', '--date', date])
                predictions[source] = data
                
            elif source == 'cbbpy':
                data = self.run_script('cbbpy_tools', ['games-today', '--date', date])
                predictions[source] = data
            
            # Add other sources as needed
            else:
                self.log(f"Source {source} not implemented yet")
                predictions[source] = []
        
        return predictions
    
    def normalize_team_names(self, team_name: str) -> str:
        """Normalize team names for matching across sources."""
        # Common normalizations
        name = team_name.strip()
        
        # Remove common prefixes/suffixes
        name = name.replace('University of ', '')
        name = name.replace(' University', '')
        name = name.replace(' State', ' St')
        name = name.replace('College', '')
        
        # Handle specific cases
        name_mapping = {
            'UNC': 'North Carolina',
            'Duke': 'Duke',
            'UCLA': 'UCLA',
            'UConn': 'Connecticut',
            'ASU': 'Arizona State'
        }
        
        return name_mapping.get(name, name)
    
    def match_games_across_sources(self, predictions: Dict[str, List[Dict]]) -> List[Dict]:
        """Match games across different prediction sources."""
        matched_games = []
        
        # Use one source as the base (preferably the most complete)
        base_source = None
        for source in ['dratings', 'cbbpy', 'barttorvik']:
            if source in predictions and predictions[source]:
                base_source = source
                break
        
        if not base_source:
            return []
        
        for base_game in predictions[base_source]:
            # Extract team names from base game
            if 'away_team' in base_game and 'home_team' in base_game:
                away_team = self.normalize_team_names(base_game['away_team'])
                home_team = self.normalize_team_names(base_game['home_team'])
            else:
                continue
            
            matched_game = {
                'away_team': away_team,
                'home_team': home_team,
                'date': base_game.get('date', ''),
                'predictions': {base_source: base_game},
                'consensus': {}
            }
            
            # Find matching games in other sources
            for source, games in predictions.items():
                if source == base_source:
                    continue
                
                for game in games:
                    if self.is_same_game(game, away_team, home_team):
                        matched_game['predictions'][source] = game
                        break
            
            matched_games.append(matched_game)
        
        return matched_games
    
    def is_same_game(self, game: Dict, target_away: str, target_home: str) -> bool:
        """Check if a game matches the target teams."""
        if 'away_team' in game and 'home_team' in game:
            away = self.normalize_team_names(game['away_team'])
            home = self.normalize_team_names(game['home_team'])
            return away == target_away and home == target_home
        return False
    
    def calculate_consensus_prediction(self, matched_game: Dict) -> Dict:
        """Calculate consensus prediction from multiple sources."""
        predictions = matched_game['predictions']
        consensus = {
            'away_win_prob': [],
            'home_win_prob': [],
            'spread': [],
            'total': []
        }
        
        # Collect predictions from all sources
        for source, prediction in predictions.items():
            if isinstance(prediction, dict):
                # Extract win probabilities
                if 'predictions' in prediction:
                    pred_data = prediction['predictions']
                    if 'model_win_prob_away' in pred_data and pred_data['model_win_prob_away']:
                        consensus['away_win_prob'].append(pred_data['model_win_prob_away'])
                    if 'model_win_prob_home' in pred_data and pred_data['model_win_prob_home']:
                        consensus['home_win_prob'].append(pred_data['model_win_prob_home'])
                    if 'predicted_spread' in pred_data and pred_data['predicted_spread']:
                        consensus['spread'].append(pred_data['predicted_spread'])
                    if 'predicted_total' in pred_data and pred_data['predicted_total']:
                        consensus['total'].append(pred_data['predicted_total'])
        
        # Calculate averages
        result = {}
        for key, values in consensus.items():
            if values:
                result[f'avg_{key}'] = np.mean(values)
                result[f'std_{key}'] = np.std(values) if len(values) > 1 else 0
                result[f'count_{key}'] = len(values)
        
        return result
    
    def find_edges(self, date: str = None, sources: List[str] = None, min_edge: float = 2.0) -> List[Dict]:
        """Find betting edges across multiple sources."""
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            else:
                date = self.parse_date(date)
            
            if sources is None:
                sources = ['dratings', 'cbbpy']
            elif 'all' in sources:
                sources = self.available_sources
            
            self.log(f"Finding edges for {date} using sources: {sources}")
            
            # Get predictions from all sources
            predictions = self.get_multi_source_predictions(date, sources)
            
            # Match games across sources
            matched_games = self.match_games_across_sources(predictions)
            
            # Find edges for each game
            edges = []
            
            for game in matched_games:
                consensus = self.calculate_consensus_prediction(game)
                game_edges = self.identify_game_edges(game, consensus, min_edge)
                
                if game_edges:
                    edge_game = {
                        'game': f"{game['away_team']} @ {game['home_team']}",
                        'date': game['date'],
                        'consensus': consensus,
                        'edges': game_edges,
                        'max_edge': max(edge['edge_percent'] for edge in game_edges),
                        'sources_count': len(game['predictions'])
                    }
                    edges.append(edge_game)
            
            # Sort by edge strength and source agreement
            edges.sort(key=lambda x: (x['max_edge'], x['sources_count']), reverse=True)
            
            return edges
            
        except Exception as e:
            self.log(f"Error finding edges: {str(e)}")
            return []
    
    def identify_game_edges(self, game: Dict, consensus: Dict, min_edge: float) -> List[Dict]:
        """Identify specific betting edges for a game."""
        edges = []
        
        # Get market data (would need to implement odds scraping)
        # For now, use placeholder odds
        placeholder_market = {
            'away_ml_odds': 110,  # Even money
            'home_ml_odds': -110,
            'spread': 2.5,
            'total': 145.0
        }
        
        # Check moneyline edges
        if 'avg_away_win_prob' in consensus:
            model_prob = consensus['avg_away_win_prob']
            market_prob = self.odds_to_probability(placeholder_market['away_ml_odds'])
            edge = self.calculate_edge(model_prob, market_prob)
            
            if abs(edge) >= min_edge:
                kelly_bet = self.kelly_criterion(model_prob, market_prob)
                edges.append({
                    'type': 'moneyline',
                    'team': game['away_team'],
                    'side': 'away',
                    'model_prob': model_prob,
                    'market_prob': market_prob,
                    'edge_percent': edge,
                    'kelly_bet_amount': kelly_bet,
                    'confidence': self.calculate_confidence(consensus, 'away_win_prob'),
                    'recommended': edge > 0
                })
        
        if 'avg_home_win_prob' in consensus:
            model_prob = consensus['avg_home_win_prob']
            market_prob = self.odds_to_probability(placeholder_market['home_ml_odds'])
            edge = self.calculate_edge(model_prob, market_prob)
            
            if abs(edge) >= min_edge:
                kelly_bet = self.kelly_criterion(model_prob, market_prob)
                edges.append({
                    'type': 'moneyline',
                    'team': game['home_team'],
                    'side': 'home',
                    'model_prob': model_prob,
                    'market_prob': market_prob,
                    'edge_percent': edge,
                    'kelly_bet_amount': kelly_bet,
                    'confidence': self.calculate_confidence(consensus, 'home_win_prob'),
                    'recommended': edge > 0
                })
        
        # Check spread and total edges (similar logic)
        # Implementation would compare predicted spreads/totals to market lines
        
        return edges
    
    def calculate_confidence(self, consensus: Dict, metric_type: str) -> float:
        """Calculate confidence score based on source agreement."""
        count_key = f'count_{metric_type}'
        std_key = f'std_{metric_type}'
        
        source_count = consensus.get(count_key, 0)
        std_dev = consensus.get(std_key, 0)
        
        # Higher confidence with more sources and lower standard deviation
        if source_count == 0:
            return 0
        
        source_score = min(source_count / 3, 1.0)  # Max score at 3+ sources
        agreement_score = max(0, 1 - std_dev * 4)  # Penalize high std dev
        
        return (source_score * 0.6 + agreement_score * 0.4) * 100
    
    def scan_today(self, sources: List[str] = None, min_edge: float = 2.0) -> List[Dict]:
        """Scan today's games for edges."""
        return self.find_edges('today', sources, min_edge)
    
    def backtest(self, start_date: str, end_date: str = None, sources: List[str] = None) -> Dict:
        """Backtest edge finding performance over a date range."""
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            self.log(f"Backtesting from {start_date} to {end_date}")
            
            # Generate date range
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            current = start
            
            results = {
                'period': f"{start_date} to {end_date}",
                'total_edges_found': 0,
                'profitable_edges': 0,
                'total_roi': 0.0,
                'daily_results': []
            }
            
            while current <= end:
                date_str = current.strftime('%Y-%m-%d')
                daily_edges = self.find_edges(date_str, sources)
                
                daily_result = {
                    'date': date_str,
                    'edges_found': len(daily_edges),
                    'max_edge': max((edge['max_edge'] for edge in daily_edges), default=0)
                }
                
                results['daily_results'].append(daily_result)
                results['total_edges_found'] += len(daily_edges)
                
                current += timedelta(days=1)
            
            return results
            
        except Exception as e:
            self.log(f"Error backtesting: {str(e)}")
            return {}

def main():
    parser = argparse.ArgumentParser(
        description='Edge Finder - Find profitable betting opportunities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s scan --date today --min-edge 3.0
  %(prog)s today --sources all --min-edge 5.0
  %(prog)s backtest --start-date 2025-03-01 --end-date 2025-03-15
        '''
    )
    
    parser.add_argument('command', choices=[
        'scan', 'today', 'backtest'
    ], help='Command to execute')
    
    parser.add_argument('--date', help='Date in YYYY-MM-DD format or "today"')
    parser.add_argument('--start-date', help='Start date for backtest (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date for backtest (YYYY-MM-DD)')
    parser.add_argument('--sources', nargs='+', help='Prediction sources to use (or "all")')
    parser.add_argument('--min-edge', type=float, default=2.0, help='Minimum edge percentage (default: 2.0)')
    
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    parser.add_argument('--csv', action='store_true', help='Output in CSV format')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    edge_finder = EdgeFinder(debug=args.debug)
    result = None
    
    try:
        if args.command == 'scan':
            result = edge_finder.find_edges(args.date, args.sources, args.min_edge)
            
        elif args.command == 'today':
            result = edge_finder.scan_today(args.sources, args.min_edge)
            
        elif args.command == 'backtest':
            if not args.start_date:
                print("Error: --start-date is required for backtest command", file=sys.stderr)
                sys.exit(1)
            result = edge_finder.backtest(args.start_date, args.end_date, args.sources)
        
        # Output result
        if result is not None:
            print(edge_finder.format_output(result, args.pretty, args.csv))
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