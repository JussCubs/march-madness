---
name: march-madness
description: NCAA college basketball analytics and March Madness prediction tools. Use when analyzing college basketball games, finding betting edges, building bracket predictions, or accessing NCAAB data. Includes tools for CBBpy (ESPN data), Barttorvik T-Rank, DRatings predictions, NCAA NET rankings, Massey composite ratings, Warren Nolan metrics, Kaggle tournament data, Haslametrics, and multi-source odds comparison. All data sources are FREE.
---

# March Madness NCAA Basketball Analytics

A comprehensive skill for NCAA college basketball data analysis and March Madness prediction modeling.

## Features

🏀 **Complete Data Coverage**: 25+ free data sources for NCAA basketball analytics
📊 **Multiple Prediction Models**: Access to T-Rank, BPI, NET, KenPom-style metrics, and computer ratings
💰 **Edge Finding**: Compare model predictions vs betting lines for profitable opportunities
📈 **Historical Data**: Multi-season data for backtesting and model training
🎯 **Tournament Focus**: Specialized tools for March Madness bracket prediction

## Available Tools

### Core Data Tools
- **cbbpy_tools.py**: ESPN data via CBBpy (schedules, boxscores, play-by-play, player stats)
- **espn_scraper.py**: Direct ESPN API access (BPI ratings, scores, standings)
- **ncaa_stats.py**: Official NCAA statistics and NET rankings
- **kaggle_data.py**: March Madness historical datasets

### Analytics Sites
- **barttorvik.py**: T-Rank ratings and tempo-free analytics
- **warren_nolan.py**: NET rankings, RPI, strength of schedule
- **massey_ratings.py**: Composite computer ratings from multiple systems
- **haslametrics.py**: Computer predictions and unique analytics

### Betting & Predictions
- **dratings.py**: Computer predictions with odds comparison
- **odds_comparison.py**: Multi-source odds and trends
- **edge_finder.py**: Identify profitable betting opportunities

## Quick Start

```bash
# Get today's games with predictions
python3 scripts/cbbpy_tools.py games-today --with-odds

# Find betting edges for today's games
python3 scripts/edge_finder.py today --min-edge 3.0

# Get T-Rank ratings for top 25 teams
python3 scripts/barttorvik.py rankings --top 25

# Compare model predictions vs betting lines
python3 scripts/dratings.py edge-finder --date today
```

## Installation

```bash
cd skills/march-madness
pip3 install -r requirements.txt
```

## Data Sources

All data sources are **FREE** and documented in `references/data_sources.md`. Key sources include:

- **CBBpy**: ESPN play-by-play and boxscore data
- **Barttorvik**: T-Rank tempo-free analytics
- **NCAA**: Official NET rankings and statistics
- **DRatings**: Computer predictions and betting analysis
- **Kaggle**: Historical March Madness tournament data
- **Warren Nolan**: Comprehensive NCAA metrics tracking

## Usage Examples

### Daily Game Analysis
```bash
# Get today's schedule with predictions
python3 scripts/cbbpy_tools.py games-today

# Get current T-Rank top 25
python3 scripts/barttorvik.py rankings --top 25

# Find today's best betting edges
python3 scripts/edge_finder.py scan --date today
```

### Team Research
```bash
# Get Duke's full schedule and stats
python3 scripts/cbbpy_tools.py schedule --team "Duke" --season 2026

# Get Duke's T-Rank metrics and predictions
python3 scripts/barttorvik.py team-stats --team "Duke"

# Get Duke's NET ranking and quad records
python3 scripts/warren_nolan.py net --team "Duke"
```

### Bracket Building
```bash
# Get current bracket projections
python3 scripts/warren_nolan.py bracket-projection

# Get computer rating consensus
python3 scripts/massey_ratings.py composite --top 68

# Backtest model performance
python3 scripts/edge_finder.py backtest --start-date 2025-03-01
```

## Output Formats

All tools support:
- **JSON**: Default machine-readable format
- **Pretty**: Human-readable format with `--pretty` flag
- **CSV**: Structured data export with `--csv` flag

## References

- `references/data_sources.md`: Complete documentation of all 25 data sources
- `references/metrics_guide.md`: Guide to understanding advanced basketball metrics
- `references/march_madness_calendar.md`: Important dates and tournament structure

## Contributing

This skill is open source. Contributions welcome for additional data sources, prediction models, or analytics tools.

## License

MIT License - see LICENSE file for details.