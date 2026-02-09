#!/usr/bin/env python3
"""
NCAA Official Statistics Scraper

Scrapes stats.ncaa.org and ncaa.com for official NCAA statistics,
NET rankings, team stats, and tournament data.

Usage:
    python3 ncaa_stats.py net-rankings --top 25
    python3 ncaa_stats.py team-stats --team "Duke"
    python3 ncaa_stats.py standings --conference "ACC"
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

class NCAAStatsScraper:
    """Scraper for official NCAA basketball statistics and NET rankings."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.ncaa_stats_url = "https://stats.ncaa.org"
        self.ncaa_url = "https://www.ncaa.com"
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
    
    def get_net_rankings(self, top: int = None) -> List[Dict]:
        """Get NCAA NET rankings."""
        try:
            self.log("Getting NCAA NET rankings")
            
            # Try the official NCAA NET rankings page
            url = f"{self.ncaa_url}/rankings/basketball-men/d1/ncaa-mens-basketball-net-rankings"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            rankings = []
            
            # Look for rankings table or list
            table = soup.find('table', class_=lambda x: x and 'ranking' in x.lower() if x else False)
            if not table:
                # Try alternative selectors
                table = soup.find('table')
                if not table:
                    # Try looking for div-based rankings
                    ranking_items = soup.find_all('div', class_=lambda x: x and 'team' in x.lower() if x else False)
                    return self.parse_ranking_divs(ranking_items, top)
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for i, row in enumerate(rows):
                    if top and i >= top:
                        break
                        
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 3:
                        continue
                    
                    try:
                        rank_data = {
                            'net_rank': int(cells[0].get_text(strip=True)),
                            'team': cells[1].get_text(strip=True),
                            'record': cells[2].get_text(strip=True) if len(cells) > 2 else None,
                            'conference': cells[3].get_text(strip=True) if len(cells) > 3 else None,
                            'quadrant_1_record': cells[4].get_text(strip=True) if len(cells) > 4 else None,
                            'quadrant_2_record': cells[5].get_text(strip=True) if len(cells) > 5 else None,
                            'quadrant_3_record': cells[6].get_text(strip=True) if len(cells) > 6 else None,
                            'quadrant_4_record': cells[7].get_text(strip=True) if len(cells) > 7 else None,
                        }
                        rankings.append(rank_data)
                    except (ValueError, IndexError) as e:
                        self.log(f"Error parsing NET ranking row {i}: {str(e)}")
                        continue
            
            return rankings
            
        except Exception as e:
            self.log(f"Error getting NET rankings: {str(e)}")
            return []
    
    def parse_ranking_divs(self, ranking_items: List, top: int = None) -> List[Dict]:
        """Parse rankings from div-based layout."""
        rankings = []
        
        for i, item in enumerate(ranking_items):
            if top and i >= top:
                break
                
            try:
                # Extract rank and team name from div structure
                rank_elem = item.find(['span', 'div'], class_=lambda x: x and 'rank' in x.lower() if x else False)
                team_elem = item.find(['span', 'div'], class_=lambda x: x and 'team' in x.lower() if x else False)
                
                if rank_elem and team_elem:
                    rank_data = {
                        'net_rank': int(rank_elem.get_text(strip=True)),
                        'team': team_elem.get_text(strip=True),
                        'record': None,
                        'conference': None
                    }
                    rankings.append(rank_data)
            except Exception as e:
                self.log(f"Error parsing ranking div {i}: {str(e)}")
                continue
        
        return rankings
    
    def get_team_stats(self, team: str, season: str = None) -> Dict:
        """Get official team statistics."""
        try:
            if season is None:
                season = str(datetime.now().year)
            
            self.log(f"Getting team stats for {team}")
            
            # Search for team page on stats.ncaa.org
            search_url = f"{self.ncaa_stats_url}/teams"
            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            team_data = {
                'team': team,
                'season': season,
                'stats': {},
                'rankings': {}
            }
            
            # Look for team statistics tables
            tables = soup.find_all('table')
            
            for table in tables:
                # Try to identify what type of stats table this is
                caption = table.find('caption')
                headers = [th.get_text(strip=True) for th in table.find_all('th')]
                
                table_type = 'general'
                if caption:
                    caption_text = caption.get_text(strip=True).lower()
                    if 'offense' in caption_text:
                        table_type = 'offense'
                    elif 'defense' in caption_text:
                        table_type = 'defense'
                    elif 'rebounding' in caption_text:
                        table_type = 'rebounding'
                
                # Parse table rows
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        stat_name = cells[0].get_text(strip=True)
                        stat_value = cells[1].get_text(strip=True)
                        
                        # Try to convert to number if possible
                        try:
                            if '.' in stat_value:
                                stat_value = float(stat_value)
                            elif stat_value.isdigit():
                                stat_value = int(stat_value)
                        except ValueError:
                            pass
                        
                        if table_type not in team_data['stats']:
                            team_data['stats'][table_type] = {}
                        team_data['stats'][table_type][stat_name] = stat_value
            
            return team_data
            
        except Exception as e:
            self.log(f"Error getting team stats: {str(e)}")
            return {}
    
    def get_conference_standings(self, conference: str, season: str = None) -> List[Dict]:
        """Get conference standings."""
        try:
            if season is None:
                season = str(datetime.now().year)
            
            self.log(f"Getting {conference} standings")
            
            # Try to find conference standings page
            url = f"{self.ncaa_stats_url}/conferences"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            standings = []
            
            # Look for standings table
            table = soup.find('table', class_=lambda x: x and 'standing' in x.lower() if x else False)
            if not table:
                table = soup.find('table')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 4:
                        continue
                    
                    try:
                        team_data = {
                            'rank': len(standings) + 1,
                            'team': cells[0].get_text(strip=True),
                            'conference_record': cells[1].get_text(strip=True),
                            'overall_record': cells[2].get_text(strip=True),
                            'conference_win_pct': cells[3].get_text(strip=True) if len(cells) > 3 else None,
                            'conference': conference,
                            'season': season
                        }
                        standings.append(team_data)
                    except (ValueError, IndexError) as e:
                        self.log(f"Error parsing standings row: {str(e)}")
                        continue
            
            return standings
            
        except Exception as e:
            self.log(f"Error getting conference standings: {str(e)}")
            return []
    
    def get_tournament_bracket(self, year: int = None) -> Dict:
        """Get March Madness tournament bracket."""
        try:
            if year is None:
                year = datetime.now().year
            
            self.log(f"Getting {year} tournament bracket")
            
            url = f"{self.ncaa_url}/march-madness/brackets/{year}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            bracket = {
                'year': year,
                'regions': {},
                'final_four': [],
                'championship': None
            }
            
            # Look for bracket structure
            regions = ['south', 'west', 'east', 'midwest']
            
            for region in regions:
                region_data = {
                    'name': region.title(),
                    'teams': [],
                    'games': []
                }
                
                # Find region-specific elements
                region_section = soup.find(['div', 'section'], class_=lambda x: x and region in x.lower() if x else False)
                if region_section:
                    # Extract teams and games from region
                    teams = region_section.find_all(['span', 'div'], class_=lambda x: x and 'team' in x.lower() if x else False)
                    for team in teams:
                        team_name = team.get_text(strip=True)
                        if team_name:
                            region_data['teams'].append(team_name)
                
                bracket['regions'][region] = region_data
            
            return bracket
            
        except Exception as e:
            self.log(f"Error getting tournament bracket: {str(e)}")
            return {}

def main():
    parser = argparse.ArgumentParser(
        description='NCAA Official Statistics Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s net-rankings --top 25
  %(prog)s team-stats --team "Duke"
  %(prog)s standings --conference "ACC"
  %(prog)s tournament-bracket --year 2026
        '''
    )
    
    parser.add_argument('command', choices=[
        'net-rankings', 'team-stats', 'standings', 'tournament-bracket'
    ], help='Command to execute')
    
    parser.add_argument('--top', type=int, help='Limit results to top N teams')
    parser.add_argument('--team', help='Team name')
    parser.add_argument('--conference', help='Conference name')
    parser.add_argument('--season', help='Season year (default: current)')
    parser.add_argument('--year', type=int, help='Tournament year (default: current)')
    
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    parser.add_argument('--csv', action='store_true', help='Output in CSV format')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    scraper = NCAAStatsScraper(debug=args.debug)
    result = None
    
    try:
        if args.command == 'net-rankings':
            result = scraper.get_net_rankings(args.top)
            
        elif args.command == 'team-stats':
            if not args.team:
                print("Error: --team is required for team-stats command", file=sys.stderr)
                sys.exit(1)
            result = scraper.get_team_stats(args.team, args.season)
            
        elif args.command == 'standings':
            if not args.conference:
                print("Error: --conference is required for standings command", file=sys.stderr)
                sys.exit(1)
            result = scraper.get_conference_standings(args.conference, args.season)
            
        elif args.command == 'tournament-bracket':
            result = scraper.get_tournament_bracket(args.year)
        
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