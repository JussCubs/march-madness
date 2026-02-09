#!/usr/bin/env python3
"""
FantasyPros NCAAB Data Scraper
Scrapes fantasypros.com for college basketball projections, DFS, and news.
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

BASE_URL = "https://www.fantasypros.com/college-basketball"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

def get_projections(stat: str = "overall", pretty: bool = False) -> dict:
    """Get player projections/rankings."""
    url = f"{BASE_URL}/stats/college-basketball-stats.php"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        players = []
        table = soup.select_one("table.table") or soup.select_one("#data table") or soup.select_one("table")
        if table:
            headers_row = [th.get_text(strip=True) for th in table.select("thead th")]
            for row in table.select("tbody tr"):
                cells = [td.get_text(strip=True) for td in row.select("td")]
                if headers_row and cells:
                    players.append(dict(zip(headers_row, cells)))
                elif cells:
                    players.append(cells)
        
        return {
            "type": "projections",
            "stat": stat,
            "players": players[:50],
            "total": len(players),
            "source": "fantasypros.com"
        }
    except Exception as e:
        return {"error": str(e), "source": "fantasypros.com"}

def get_expert_picks(pretty: bool = False) -> dict:
    """Get expert CBB picks."""
    url = f"{BASE_URL}/expert-picks.php"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        picks = []
        for article in soup.select("article, .pick-card, .expert-pick"):
            pick = {}
            title = article.select_one("h2, h3, .title")
            if title:
                pick["title"] = title.get_text(strip=True)
            desc = article.select_one("p, .description, .summary")
            if desc:
                pick["description"] = desc.get_text(strip=True)
            if pick:
                picks.append(pick)
        
        return {
            "type": "expert_picks",
            "picks": picks[:20],
            "source": "fantasypros.com"
        }
    except Exception as e:
        return {"error": str(e), "source": "fantasypros.com"}

def get_news(pretty: bool = False) -> dict:
    """Get latest NCAAB news from FantasyPros."""
    url = f"{BASE_URL}/news/"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        articles = []
        for item in soup.select("article, .news-item, .story"):
            article = {}
            title = item.select_one("h2, h3, .headline, a")
            if title:
                article["title"] = title.get_text(strip=True)
                link = title.get("href") or (title.select_one("a") or {}).get("href", "")
                if link:
                    article["url"] = link if link.startswith("http") else f"https://www.fantasypros.com{link}"
            date = item.select_one("time, .date, .timestamp")
            if date:
                article["date"] = date.get_text(strip=True)
            if article.get("title"):
                articles.append(article)
        
        return {
            "type": "news",
            "articles": articles[:20],
            "source": "fantasypros.com"
        }
    except Exception as e:
        return {"error": str(e), "source": "fantasypros.com"}

def main():
    parser = argparse.ArgumentParser(description="FantasyPros NCAAB Scraper")
    sub = parser.add_subparsers(dest="command")
    
    p = sub.add_parser("projections", help="Player projections/rankings")
    p.add_argument("--stat", default="overall")
    p.add_argument("--pretty", action="store_true")
    
    e = sub.add_parser("picks", help="Expert picks")
    e.add_argument("--pretty", action="store_true")
    
    n = sub.add_parser("news", help="Latest NCAAB news")
    n.add_argument("--pretty", action="store_true")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "projections":
        result = get_projections(args.stat, args.pretty)
    elif args.command == "picks":
        result = get_expert_picks(args.pretty)
    elif args.command == "news":
        result = get_news(args.pretty)
    
    indent = 2 if getattr(args, "pretty", False) else None
    print(json.dumps(result, indent=indent, default=str))

if __name__ == "__main__":
    main()
