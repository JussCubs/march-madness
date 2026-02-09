#!/usr/bin/env python3
"""
Sports-Reference.com NCAAB Scraper
Scrapes basketball-reference.com/cbb for college basketball stats.
"""

import argparse
import json
import sys

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Install dependencies: pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://www.sports-reference.com/cbb"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}

def get_team_stats(team: str, season: int = 2026, pretty: bool = False) -> dict:
    """Get team stats from sports-reference."""
    team_slug = team.lower().replace(" ", "-")
    url = f"{BASE_URL}/schools/{team_slug}/men/{season}.html"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Team info
        info = {"team": team, "season": season, "url": url}
        
        # Overall record
        record_el = soup.select_one("[data-stat='overall_record']") or soup.find(string=lambda s: s and "Record:" in str(s))
        if record_el:
            info["record"] = record_el.get_text(strip=True) if hasattr(record_el, 'get_text') else str(record_el).strip()
        
        # Per game stats table
        per_game = soup.select_one("#per_game")
        if per_game:
            stats = {}
            for row in per_game.select("tbody tr"):
                cells = row.select("td")
                if cells:
                    for cell in cells:
                        stat_name = cell.get("data-stat", "")
                        if stat_name:
                            stats[stat_name] = cell.get_text(strip=True)
            info["per_game_stats"] = stats
        
        # Schedule/results
        schedule = soup.select_one("#schedule")
        if schedule:
            games = []
            for row in schedule.select("tbody tr"):
                game = {}
                for cell in row.select("td, th"):
                    stat = cell.get("data-stat", "")
                    if stat:
                        game[stat] = cell.get_text(strip=True)
                if game:
                    games.append(game)
            info["games"] = games[:10]  # Last 10 games
            info["total_games"] = len(games)
        
        info["source"] = "sports-reference.com"
        return info
        
    except Exception as e:
        return {"team": team, "error": str(e), "source": "sports-reference.com"}

def get_rankings(season: int = 2026, poll: str = "ap", pretty: bool = False) -> dict:
    """Get AP or Coaches poll rankings."""
    url = f"{BASE_URL}/seasons/{season}-polls.html"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        rankings = []
        table = soup.select_one(f"#{poll}-poll") or soup.select_one("table")
        if table:
            for row in table.select("tbody tr"):
                entry = {}
                for cell in row.select("td, th"):
                    stat = cell.get("data-stat", "")
                    if stat:
                        entry[stat] = cell.get_text(strip=True)
                if entry:
                    rankings.append(entry)
        
        return {
            "poll": poll.upper(),
            "season": season,
            "rankings": rankings[:25],
            "source": "sports-reference.com"
        }
    except Exception as e:
        return {"error": str(e), "source": "sports-reference.com"}

def get_player_stats(player: str, pretty: bool = False) -> dict:
    """Search for a player's stats."""
    search_url = f"{BASE_URL}/search/search.fcgi?search={player.replace(' ', '+')}"
    
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Check if redirected to player page
        if "/players/" in resp.url:
            info = {"player": player, "url": resp.url}
            
            per_game = soup.select_one("#per_game")
            if per_game:
                seasons = []
                for row in per_game.select("tbody tr"):
                    season = {}
                    for cell in row.select("td, th"):
                        stat = cell.get("data-stat", "")
                        if stat:
                            season[stat] = cell.get_text(strip=True)
                    if season:
                        seasons.append(season)
                info["seasons"] = seasons
            
            info["source"] = "sports-reference.com"
            return info
        
        # Search results
        results = []
        for link in soup.select(".search-item a"):
            results.append({"name": link.get_text(strip=True), "url": link.get("href", "")})
        
        return {"player": player, "search_results": results[:10], "source": "sports-reference.com"}
        
    except Exception as e:
        return {"player": player, "error": str(e), "source": "sports-reference.com"}

def get_conference_standings(conference: str = "big-12", season: int = 2026, pretty: bool = False) -> dict:
    """Get conference standings."""
    url = f"{BASE_URL}/seasons/{season}.html"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        teams = []
        for row in soup.select("table tbody tr"):
            team = {}
            for cell in row.select("td, th"):
                stat = cell.get("data-stat", "")
                if stat:
                    team[stat] = cell.get_text(strip=True)
            if team:
                teams.append(team)
        
        return {
            "season": season,
            "teams": teams[:50],
            "source": "sports-reference.com"
        }
    except Exception as e:
        return {"error": str(e), "source": "sports-reference.com"}

def main():
    parser = argparse.ArgumentParser(description="Sports-Reference NCAAB Scraper")
    sub = parser.add_subparsers(dest="command")
    
    t = sub.add_parser("team", help="Team stats")
    t.add_argument("name", help="Team name")
    t.add_argument("--season", type=int, default=2026)
    t.add_argument("--pretty", action="store_true")
    
    r = sub.add_parser("rankings", help="Poll rankings")
    r.add_argument("--poll", default="ap", choices=["ap", "coaches"])
    r.add_argument("--season", type=int, default=2026)
    r.add_argument("--pretty", action="store_true")
    
    p = sub.add_parser("player", help="Player stats")
    p.add_argument("name", help="Player name")
    p.add_argument("--pretty", action="store_true")
    
    c = sub.add_parser("standings", help="Conference standings")
    c.add_argument("--conference", default="big-12")
    c.add_argument("--season", type=int, default=2026)
    c.add_argument("--pretty", action="store_true")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "team":
        result = get_team_stats(args.name, args.season, args.pretty)
    elif args.command == "rankings":
        result = get_rankings(args.season, args.poll, args.pretty)
    elif args.command == "player":
        result = get_player_stats(args.name, args.pretty)
    elif args.command == "standings":
        result = get_conference_standings(args.conference, args.season, args.pretty)
    
    indent = 2 if getattr(args, "pretty", False) else None
    print(json.dumps(result, indent=indent, default=str))

if __name__ == "__main__":
    main()
