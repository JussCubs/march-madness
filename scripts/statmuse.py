#!/usr/bin/env python3
"""
StatMuse NCAAB Query Tool
Scrapes StatMuse.com for natural language basketball queries.
StatMuse lets you ask questions in plain English and get stats back.
"""

import argparse
import json
import sys
import re
import urllib.parse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Install dependencies: pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

def query_statmuse(question: str, pretty: bool = False) -> dict:
    """Ask StatMuse a natural language question about NCAAB stats."""
    encoded = urllib.parse.quote(question)
    url = f"https://www.statmuse.com/cbb/ask/{encoded}"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Extract the answer
        answer_el = soup.select_one("[class*='answer']") or soup.select_one("[class*='nlg-answer']")
        answer_text = answer_el.get_text(strip=True) if answer_el else None
        
        # Extract stats table if present
        tables = []
        for table in soup.select("table"):
            headers = [th.get_text(strip=True) for th in table.select("th")]
            rows = []
            for tr in table.select("tbody tr"):
                cells = [td.get_text(strip=True) for td in tr.select("td")]
                if headers and cells:
                    rows.append(dict(zip(headers, cells)))
                elif cells:
                    rows.append(cells)
            if rows:
                tables.append({"headers": headers, "rows": rows})
        
        result = {
            "query": question,
            "url": url,
            "answer": answer_text,
            "tables": tables,
            "source": "statmuse.com"
        }
        
        return result
        
    except Exception as e:
        return {"query": question, "error": str(e), "source": "statmuse.com"}

def team_stats(team: str, season: str = "2025-26", pretty: bool = False) -> dict:
    """Get team stats via StatMuse."""
    return query_statmuse(f"{team} stats {season} season", pretty)

def player_stats(player: str, season: str = "2025-26", pretty: bool = False) -> dict:
    """Get player stats via StatMuse."""
    return query_statmuse(f"{player} college basketball stats {season}", pretty)

def head_to_head(team1: str, team2: str, pretty: bool = False) -> dict:
    """Get head-to-head history."""
    return query_statmuse(f"{team1} vs {team2} college basketball", pretty)

def leader_query(stat: str, season: str = "2025-26", pretty: bool = False) -> dict:
    """Find stat leaders."""
    return query_statmuse(f"who leads ncaa basketball in {stat} {season}", pretty)

def main():
    parser = argparse.ArgumentParser(description="StatMuse NCAAB Query Tool")
    sub = parser.add_subparsers(dest="command", help="Command to run")
    
    # Query command
    q = sub.add_parser("query", help="Ask any question in natural language")
    q.add_argument("question", nargs="+", help="Question to ask")
    q.add_argument("--pretty", action="store_true")
    
    # Team stats
    t = sub.add_parser("team", help="Get team stats")
    t.add_argument("name", help="Team name")
    t.add_argument("--season", default="2025-26")
    t.add_argument("--pretty", action="store_true")
    
    # Player stats
    p = sub.add_parser("player", help="Get player stats")
    p.add_argument("name", help="Player name")
    p.add_argument("--season", default="2025-26")
    p.add_argument("--pretty", action="store_true")
    
    # H2H
    h = sub.add_parser("h2h", help="Head-to-head comparison")
    h.add_argument("team1", help="First team")
    h.add_argument("team2", help="Second team")
    h.add_argument("--pretty", action="store_true")
    
    # Leaders
    l = sub.add_parser("leaders", help="Stat leaders")
    l.add_argument("stat", help="Stat category (ppg, rpg, apg, etc.)")
    l.add_argument("--season", default="2025-26")
    l.add_argument("--pretty", action="store_true")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "query":
        result = query_statmuse(" ".join(args.question), args.pretty)
    elif args.command == "team":
        result = team_stats(args.name, args.season, args.pretty)
    elif args.command == "player":
        result = player_stats(args.name, args.season, args.pretty)
    elif args.command == "h2h":
        result = head_to_head(args.team1, args.team2, args.pretty)
    elif args.command == "leaders":
        result = leader_query(args.stat, args.season, args.pretty)
    
    indent = 2 if getattr(args, "pretty", False) else None
    print(json.dumps(result, indent=indent, default=str))

if __name__ == "__main__":
    main()
