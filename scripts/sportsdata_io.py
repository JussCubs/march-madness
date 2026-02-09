#!/usr/bin/env python3
"""
SportsData.io NCAAB API Client
Access the SportsDataIO college basketball API.
Free tier available with registration.
API docs: https://sportsdata.io/developers/api-documentation/ncaa-basketball
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("Install: pip install requests", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://api.sportsdata.io/v3/cbb"
API_KEY = os.environ.get("SPORTSDATA_API_KEY", "")

def _get(endpoint: str, params: dict = None) -> dict:
    """Make API request to SportsDataIO."""
    if not API_KEY:
        return {"error": "Set SPORTSDATA_API_KEY environment variable. Get free key at sportsdata.io"}
    
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP {resp.status_code}: {str(e)}", "url": url}
    except Exception as e:
        return {"error": str(e)}

def get_games_today(pretty: bool = False) -> dict:
    """Get today's games."""
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    result = _get(f"scores/json/GamesByDate/{today}")
    return {"date": today, "games": result, "source": "sportsdata.io"}

def get_teams(pretty: bool = False) -> dict:
    """Get all teams."""
    result = _get("scores/json/teams")
    return {"teams": result, "source": "sportsdata.io"}

def get_standings(season: int = 2026, pretty: bool = False) -> dict:
    """Get conference standings."""
    result = _get(f"scores/json/Standings/{season}")
    return {"season": season, "standings": result, "source": "sportsdata.io"}

def get_team_stats(season: int = 2026, pretty: bool = False) -> dict:
    """Get team season stats."""
    result = _get(f"scores/json/TeamSeasonStats/{season}")
    return {"season": season, "stats": result, "source": "sportsdata.io"}

def get_player_stats(season: int = 2026, pretty: bool = False) -> dict:
    """Get player season stats."""
    result = _get(f"stats/json/PlayerSeasonStats/{season}")
    return {"season": season, "stats": result, "source": "sportsdata.io"}

def get_odds(pretty: bool = False) -> dict:
    """Get current game odds."""
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    result = _get(f"odds/json/GameOddsByDate/{today}")
    return {"date": today, "odds": result, "source": "sportsdata.io"}

def get_schedule(season: int = 2026, pretty: bool = False) -> dict:
    """Get season schedule."""
    result = _get(f"scores/json/Games/{season}")
    return {"season": season, "games": result, "source": "sportsdata.io"}

def main():
    parser = argparse.ArgumentParser(description="SportsData.io NCAAB API")
    parser.add_argument("--key", help="API key (or set SPORTSDATA_API_KEY env var)")
    sub = parser.add_subparsers(dest="command")
    
    sub.add_parser("today", help="Today's games")
    sub.add_parser("teams", help="All teams")
    
    s = sub.add_parser("standings", help="Conference standings")
    s.add_argument("--season", type=int, default=2026)
    
    ts = sub.add_parser("team-stats", help="Team season stats")
    ts.add_argument("--season", type=int, default=2026)
    
    ps = sub.add_parser("player-stats", help="Player season stats")
    ps.add_argument("--season", type=int, default=2026)
    
    o = sub.add_parser("odds", help="Today's odds")
    
    sc = sub.add_parser("schedule", help="Season schedule")
    sc.add_argument("--season", type=int, default=2026)
    
    for s in sub.choices.values():
        s.add_argument("--pretty", action="store_true")
    
    args = parser.parse_args()
    
    if args.key:
        global API_KEY
        API_KEY = args.key
    
    if not args.command:
        parser.print_help()
        print("\nNote: Requires SPORTSDATA_API_KEY. Get free key at https://sportsdata.io")
        sys.exit(1)
    
    commands = {
        "today": lambda: get_games_today(args.pretty),
        "teams": lambda: get_teams(args.pretty),
        "standings": lambda: get_standings(getattr(args, "season", 2026), args.pretty),
        "team-stats": lambda: get_team_stats(getattr(args, "season", 2026), args.pretty),
        "player-stats": lambda: get_player_stats(getattr(args, "season", 2026), args.pretty),
        "odds": lambda: get_odds(args.pretty),
        "schedule": lambda: get_schedule(getattr(args, "season", 2026), args.pretty),
    }
    
    result = commands[args.command]()
    indent = 2 if getattr(args, "pretty", False) else None
    print(json.dumps(result, indent=indent, default=str))

if __name__ == "__main__":
    main()
