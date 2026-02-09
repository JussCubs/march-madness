#!/usr/bin/env python3
"""
Kaggle March Madness Data Loader

Downloads and loads historical March Madness datasets from Kaggle.
Requires Kaggle API setup (kaggle.json in ~/.kaggle/).

Usage:
    python3 kaggle_data.py download --competition march-machine-learning-mania-2024
    python3 kaggle_data.py load --dataset teams --year 2024
    python3 kaggle_data.py analyze --type seeds --years 2019-2024
"""

import argparse
import json
import sys
import traceback
import os
from typing import Dict, List, Any

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("Error: Install with: pip3 install pandas numpy")
    sys.exit(1)

try:
    import kaggle
    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False

class KaggleMarchMadnessData:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.data_dir = "kaggle_data"
        
        # Ensure data directory exists
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
    def log(self, message: str):
        if self.debug:
            print(f"[DEBUG] {message}", file=sys.stderr)
    
    def format_output(self, data: Any, pretty: bool = False, csv: bool = False) -> str:
        if csv and isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            return pd.DataFrame(data).to_csv(index=False)
        return json.dumps(data, indent=2 if pretty else None, default=str)
    
    def check_kaggle_setup(self) -> bool:
        """Check if Kaggle API is properly configured."""
        if not KAGGLE_AVAILABLE:
            return False
        
        try:
            kaggle.api.authenticate()
            return True
        except Exception as e:
            self.log(f"Kaggle authentication failed: {str(e)}")
            return False
    
    def download_competition_data(self, competition: str) -> Dict:
        """Download March Madness competition data from Kaggle."""
        try:
            if not self.check_kaggle_setup():
                return {
                    'error': 'Kaggle API not available or not configured',
                    'setup_instructions': [
                        '1. Install kaggle: pip install kaggle',
                        '2. Create account at kaggle.com',
                        '3. Go to Account -> Create New API Token',
                        '4. Place kaggle.json in ~/.kaggle/',
                        '5. chmod 600 ~/.kaggle/kaggle.json'
                    ]
                }
            
            self.log(f"Downloading competition data: {competition}")
            
            # Download competition files
            download_path = os.path.join(self.data_dir, competition)
            kaggle.api.competition_download_files(competition, path=download_path)
            
            # List downloaded files
            files = []
            if os.path.exists(download_path):
                for file in os.listdir(download_path):
                    files.append(file)
            
            return {
                'competition': competition,
                'download_path': download_path,
                'files': files,
                'status': 'success'
            }
            
        except Exception as e:
            self.log(f"Error downloading competition data: {str(e)}")
            return {'error': str(e)}
    
    def load_dataset(self, dataset: str, year: int = None) -> List[Dict]:
        """Load a specific dataset (teams, seeds, results, etc.)."""
        try:
            # Map dataset names to file patterns
            file_patterns = {
                'teams': 'Teams.csv',
                'seeds': 'NCAATourneySeeds.csv',
                'results': 'NCAATourneyCompactResults.csv',
                'detailed_results': 'NCAATourneyDetailedResults.csv',
                'regular_season': 'RegularSeasonCompactResults.csv',
                'regular_season_detailed': 'RegularSeasonDetailedResults.csv',
                'coaches': 'TeamCoaches.csv',
                'conferences': 'Conferences.csv'
            }
            
            if dataset not in file_patterns:
                return [{'error': f'Unknown dataset: {dataset}. Available: {list(file_patterns.keys())}'}]
            
            filename = file_patterns[dataset]
            
            # Look for file in downloaded competition data
            file_path = None
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    if file.endswith(filename):
                        file_path = os.path.join(root, file)
                        break
                if file_path:
                    break
            
            if not file_path:
                return [{'error': f'File not found: {filename}. Run download command first.'}]
            
            self.log(f"Loading dataset from: {file_path}")
            
            # Load CSV data
            df = pd.read_csv(file_path)
            
            # Filter by year if specified
            if year and 'Season' in df.columns:
                df = df[df['Season'] == year]
            
            # Convert to list of dictionaries
            data = df.to_dict('records')
            
            return data
            
        except Exception as e:
            self.log(f"Error loading dataset: {str(e)}")
            return [{'error': str(e)}]
    
    def analyze_data(self, analysis_type: str, years: str = None) -> Dict:
        """Perform analysis on March Madness historical data."""
        try:
            if analysis_type == 'seeds':
                return self.analyze_seed_performance(years)
            elif analysis_type == 'upsets':
                return self.analyze_upset_patterns(years)
            elif analysis_type == 'conferences':
                return self.analyze_conference_performance(years)
            else:
                return {'error': f'Unknown analysis type: {analysis_type}'}
                
        except Exception as e:
            self.log(f"Error in analysis: {str(e)}")
            return {'error': str(e)}
    
    def analyze_seed_performance(self, years: str = None) -> Dict:
        """Analyze how different seeds perform historically."""
        try:
            # Load tournament results
            results = self.load_dataset('results')
            seeds = self.load_dataset('seeds')
            
            if not results or not seeds:
                return {'error': 'Could not load required datasets'}
            
            # Convert to DataFrames for analysis
            results_df = pd.DataFrame(results)
            seeds_df = pd.DataFrame(seeds)
            
            # Parse years range
            year_list = []
            if years:
                if '-' in years:
                    start_year, end_year = map(int, years.split('-'))
                    year_list = list(range(start_year, end_year + 1))
                else:
                    year_list = [int(years)]
            
            if year_list:
                results_df = results_df[results_df['Season'].isin(year_list)]
                seeds_df = seeds_df[seeds_df['Season'].isin(year_list)]
            
            # Analyze seed performance
            analysis = {
                'seed_win_rates': {},
                'upset_analysis': {},
                'championship_seeds': []
            }
            
            # Calculate basic seed statistics
            for seed in range(1, 17):
                seed_teams = seeds_df[seeds_df['Seed'].str.contains(f'{seed:02d}', na=False)]
                total_teams = len(seed_teams)
                
                if total_teams > 0:
                    analysis['seed_win_rates'][f'seed_{seed}'] = {
                        'total_appearances': total_teams,
                        'avg_wins': f"Analysis would require game-by-game processing",
                        'championship_rate': 0.0,
                        'final_four_rate': 0.0
                    }
            
            return analysis
            
        except Exception as e:
            self.log(f"Error analyzing seed performance: {str(e)}")
            return {'error': str(e)}
    
    def analyze_upset_patterns(self, years: str = None) -> Dict:
        """Analyze upset patterns in tournament history."""
        return {
            'analysis_type': 'upsets',
            'note': 'Upset analysis requires detailed game-by-game processing',
            'common_upsets': {
                '12_over_5': 'Historically ~35% success rate',
                '13_over_4': 'Less common but bracket-breaking',
                '14_over_3': 'Rare but memorable',
                '15_over_2': 'Very rare, like UMBC over Virginia'
            }
        }
    
    def analyze_conference_performance(self, years: str = None) -> Dict:
        """Analyze conference performance in tournament."""
        return {
            'analysis_type': 'conferences',
            'note': 'Conference analysis requires team-conference mapping',
            'power_conferences': ['ACC', 'Big Ten', 'Big 12', 'SEC', 'Pac-12', 'Big East'],
            'metrics_to_analyze': ['bid_count', 'avg_seed', 'total_wins', 'championship_rate']
        }

def main():
    parser = argparse.ArgumentParser(description='Kaggle March Madness Data Loader')
    parser.add_argument('command', choices=['download', 'load', 'analyze', 'list'])
    parser.add_argument('--competition', default='march-machine-learning-mania-2024')
    parser.add_argument('--dataset', help='Dataset to load (teams, seeds, results, etc.)')
    parser.add_argument('--year', type=int, help='Filter by specific year')
    parser.add_argument('--type', help='Analysis type (seeds, upsets, conferences)')
    parser.add_argument('--years', help='Year range for analysis (e.g., 2019-2024)')
    parser.add_argument('--pretty', action='store_true')
    parser.add_argument('--csv', action='store_true')
    parser.add_argument('--debug', action='store_true')
    
    args = parser.parse_args()
    loader = KaggleMarchMadnessData(debug=args.debug)
    
    try:
        if args.command == 'download':
            result = loader.download_competition_data(args.competition)
        elif args.command == 'load':
            if not args.dataset:
                print("Error: --dataset required for load command", file=sys.stderr)
                sys.exit(1)
            result = loader.load_dataset(args.dataset, args.year)
        elif args.command == 'analyze':
            if not args.type:
                print("Error: --type required for analyze command", file=sys.stderr)
                sys.exit(1)
            result = loader.analyze_data(args.type, args.years)
        elif args.command == 'list':
            result = {
                'available_datasets': ['teams', 'seeds', 'results', 'detailed_results', 'regular_season', 'coaches', 'conferences'],
                'available_analyses': ['seeds', 'upsets', 'conferences'],
                'data_directory': loader.data_dir
            }
        else:
            result = {'error': 'Unknown command'}
        
        print(loader.format_output(result, args.pretty, args.csv))
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        if args.debug:
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()