#!/usr/bin/env python3
"""
CBBpy Tools - ESPN College Basketball Data Wrapper

Provides access to ESPN college basketball data via CBBpy package.
Supports schedules, boxscores, play-by-play, player info, and more.

Usage:
    python3 cbbpy_tools.py schedule --team "Duke" --season 2026
    python3 cbbpy_tools.py games-today --with-odds
    python3 cbbpy_tools.py boxscore --game-id 12345
"""

import argparse
import json
import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

try:
    import cbbpy.mens_scraper as cbb
except ImportError:
    print("Error: CBBpy not installed. Install with: pip3 install CBBpy")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("Error: pandas not installed. Install with: pip3 install pandas")
    sys.exit(1)

class CBBpyTools:
    """ESPN college basketball data wrapper using CBBpy."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        
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
    
    def get_team_schedule(self, team: str, season: int = None) -> List[Dict]:
        """Get team's full schedule for the season."""
        try:
            if season is None:
                season = datetime.now().year
                if datetime.now().month < 7:  # Before July = previous season
                    season -= 1
            
            self.log(f"Getting schedule for {team}, season {season}")
            
            # CBBpy function to get schedule
            schedule = cbb.get_team_schedule(team=team, season=season)
            
            if schedule is None or schedule.empty:
                return []
            
            # Convert to list of dictionaries
            games = []
            for _, game in schedule.iterrows():
                game_dict = {
                    'date': game.get('Date', ''),
                    'opponent': game.get('Opponent', ''),
                    'location': game.get('Location', ''),
                    'result': game.get('Result', ''),
                    'team_score': game.get('Tm', 0),
                    'opponent_score': game.get('Opp', 0),
                    'game_id': game.get('Game_ID', '')
                }
                games.append(game_dict)
            
            return games
            
        except Exception as e:
            self.log(f"Error getting schedule: {str(e)}")
            return []
    
    def get_games_today(self, date: str = None, with_odds: bool = False) -> List[Dict]:
        """Get all games for a specific date (default: today)."""
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            self.log(f"Getting games for {date}")
            
            # CBBpy function to get games
            games_data = cbb.get_games_range(date, date)
            
            if games_data is None or games_data.empty:
                return []
            
            games = []
            for _, game in games_data.iterrows():
                game_dict = {
                    'date': game.get('Date', date),
                    'home_team': game.get('Home', ''),
                    'away_team': game.get('Away', ''),
                    'home_score': game.get('Home_Score', 0),
                    'away_score': game.get('Away_Score', 0),
                    'status': game.get('Status', ''),
                    'game_id': game.get('Game_ID', ''),
                    'time': game.get('Time', '')
                }
                
                # Add odds if requested (placeholder - would need additional source)
                if with_odds:
                    game_dict['spread'] = None
                    game_dict['total'] = None
                    game_dict['home_ml'] = None
                    game_dict['away_ml'] = None
                
                games.append(game_dict)
            
            return games
            
        except Exception as e:
            self.log(f"Error getting today's games: {str(e)}")
            return []
    
    def get_boxscore(self, game_id: str) -> Dict:
        """Get detailed boxscore for a specific game."""
        try:
            self.log(f"Getting boxscore for game {game_id}")
            
            boxscore = cbb.get_game_boxscore(game_id)
            
            if boxscore is None:
                return {}
            
            # Extract team stats
            result = {
                'game_id': game_id,
                'teams': {},
                'stats': {}
            }
            
            # Process team stats if available
            if hasattr(boxscore, 'keys'):
                for team in boxscore.keys():
                    if isinstance(boxscore[team], pd.DataFrame):
                        result['teams'][team] = boxscore[team].to_dict('records')
            
            return result
            
        except Exception as e:
            self.log(f"Error getting boxscore: {str(e)}")
            return {}
    
    def get_play_by_play(self, game_id: str) -> List[Dict]:
        """Get play-by-play data for a specific game."""
        try:
            self.log(f"Getting play-by-play for game {game_id}")
            
            pbp = cbb.get_game_pbp(game_id)
            
            if pbp is None or pbp.empty:
                return []
            
            plays = []
            for _, play in pbp.iterrows():
                play_dict = {
                    'time': play.get('Time', ''),
                    'score': play.get('Score', ''),
                    'play_text': play.get('Play', ''),
                    'team': play.get('Team', ''),
                    'period': play.get('Period', 1)
                }
                plays.append(play_dict)
            
            return plays
            
        except Exception as e:
            self.log(f"Error getting play-by-play: {str(e)}")
            return []
    
    def get_player_info(self, player_name: str) -> Dict:
        """Get information about a specific player."""
        try:
            self.log(f"Getting player info for {player_name}")
            
            player_data = cbb.get_player_info(player_name)
            
            if player_data is None or player_data.empty:
                return {}
            
            # Convert to dictionary
            player_info = player_data.to_dict('records')[0] if not player_data.empty else {}
            
            return player_info
            
        except Exception as e:
            self.log(f"Error getting player info: {str(e)}")
            return {}
    
    def get_conference_standings(self, conference: str, season: int = None) -> List[Dict]:
        """Get conference standings."""
        try:
            if season is None:
                season = datetime.now().year
                if datetime.now().month < 7:
                    season -= 1
            
            self.log(f"Getting {conference} standings for season {season}")
            
            standings = cbb.get_conference_standings(conference=conference, season=season)
            
            if standings is None or standings.empty:
                return []
            
            teams = []
            for _, team in standings.iterrows():
                team_dict = {
                    'team': team.get('Team', ''),
                    'conference_record': team.get('Conf', ''),
                    'overall_record': team.get('Overall', ''),
                    'conference_wins': team.get('W', 0),
                    'conference_losses': team.get('L', 0),
                    'win_percentage': team.get('PCT', 0.0)
                }
                teams.append(team_dict)
            
            return teams
            
        except Exception as e:
            self.log(f"Error getting conference standings: {str(e)}")
            return []

def main():
    parser = argparse.ArgumentParser(
        description='CBBpy Tools - ESPN College Basketball Data Wrapper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s schedule --team "Duke" --season 2026
  %(prog)s games-today --with-odds
  %(prog)s boxscore --game-id "401608548"
  %(prog)s pbp --game-id "401608548"
  %(prog)s player --name "Reed Bailey"
  %(prog)s conference-standings --conference "ACC"
        '''
    )
    
    parser.add_argument('command', choices=[
        'schedule', 'games-today', 'boxscore', 'pbp', 'player', 'conference-standings'
    ], help='Command to execute')
    
    parser.add_argument('--team', help='Team name (for schedule command)')
    parser.add_argument('--season', type=int, help='Season year (default: current)')
    parser.add_argument('--date', help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--with-odds', action='store_true', help='Include betting odds (games-today)')
    parser.add_argument('--game-id', help='ESPN game ID (for boxscore/pbp)')
    parser.add_argument('--name', help='Player name (for player command)')
    parser.add_argument('--conference', help='Conference name (for standings)')
    
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    parser.add_argument('--csv', action='store_true', help='Output in CSV format')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    cbb_tools = CBBpyTools(debug=args.debug)
    result = None
    
    try:
        if args.command == 'schedule':
            if not args.team:
                print("Error: --team is required for schedule command", file=sys.stderr)
                sys.exit(1)
            result = cbb_tools.get_team_schedule(args.team, args.season)
            
        elif args.command == 'games-today':
            result = cbb_tools.get_games_today(args.date, args.with_odds)
            
        elif args.command == 'boxscore':
            if not args.game_id:
                print("Error: --game-id is required for boxscore command", file=sys.stderr)
                sys.exit(1)
            result = cbb_tools.get_boxscore(args.game_id)
            
        elif args.command == 'pbp':
            if not args.game_id:
                print("Error: --game-id is required for pbp command", file=sys.stderr)
                sys.exit(1)
            result = cbb_tools.get_play_by_play(args.game_id)
            
        elif args.command == 'player':
            if not args.name:
                print("Error: --name is required for player command", file=sys.stderr)
                sys.exit(1)
            result = cbb_tools.get_player_info(args.name)
            
        elif args.command == 'conference-standings':
            if not args.conference:
                print("Error: --conference is required for conference-standings command", file=sys.stderr)
                sys.exit(1)
            result = cbb_tools.get_conference_standings(args.conference, args.season)
        
        # Output result
        if result is not None:
            print(cbb_tools.format_output(result, args.pretty, args.csv))
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