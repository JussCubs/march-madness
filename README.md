# March Madness NCAA Basketball Analytics

A comprehensive toolkit for NCAA college basketball data analysis and March Madness prediction modeling.

## 🏀 Features

- **25+ Free Data Sources**: Access to all major free college basketball analytics
- **Multiple Prediction Models**: T-Rank, BPI, NET, KenPom-style metrics
- **Edge Finding**: Compare model predictions vs betting lines for profitable opportunities
- **Historical Data**: Multi-season data for backtesting and model training
- **Tournament Focus**: Specialized tools for March Madness bracket prediction

## 📊 Data Sources

All data sources are **FREE** and include:

- **CBBpy**: ESPN play-by-play and boxscore data
- **Barttorvik**: T-Rank tempo-free analytics  
- **NCAA**: Official NET rankings and statistics
- **DRatings**: Computer predictions and betting analysis
- **ESPN**: BPI ratings and comprehensive coverage
- **Warren Nolan**: NET rankings, RPI, strength of schedule
- **Massey Ratings**: Composite computer rankings
- **Haslametrics**: Computer predictions and unique analytics
- **Kaggle**: Historical March Madness tournament datasets

See [data_sources.md](references/data_sources.md) for complete documentation of all 25 sources.

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/JussCubs/march-madness.git
cd march-madness
pip3 install -r requirements.txt
```

### Basic Usage

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

## 🛠 Available Tools

### Core Data Tools
- **cbbpy_tools.py**: ESPN data via CBBpy (schedules, boxscores, play-by-play)
- **espn_scraper.py**: Direct ESPN API access (BPI ratings, scores)
- **ncaa_stats.py**: Official NCAA statistics and NET rankings
- **kaggle_data.py**: March Madness historical datasets

### Analytics Sites
- **barttorvik.py**: T-Rank ratings and tempo-free analytics
- **warren_nolan.py**: NET rankings, RPI, strength of schedule
- **massey_ratings.py**: Composite computer ratings
- **haslametrics.py**: Computer predictions and analytics

### Betting & Predictions
- **dratings.py**: Computer predictions with odds comparison
- **odds_comparison.py**: Multi-source odds and trends  
- **edge_finder.py**: Identify profitable betting opportunities

## 📈 Examples

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

## 📋 Output Formats

All tools support multiple output formats:

```bash
# JSON (default)
python3 scripts/barttorvik.py rankings --top 10

# Pretty JSON  
python3 scripts/barttorvik.py rankings --top 10 --pretty

# CSV format
python3 scripts/barttorvik.py rankings --top 10 --csv
```

## 📚 Documentation

- [Data Sources Guide](references/data_sources.md) - Complete documentation of all 25 data sources
- [Metrics Guide](references/metrics_guide.md) - Understanding advanced basketball metrics
- [March Madness Calendar](references/march_madness_calendar.md) - Tournament structure and key dates

## 🎯 March Madness Workflow

1. **Regular Season Analysis** (Nov-Feb)
   - Track team performance with T-Rank and BPI
   - Monitor NET rankings for tournament seeding
   - Identify potential Cinderella teams

2. **Conference Tournament Week** (Early March)
   - Update models with conference tournament results
   - Watch for bid stealers and bubble teams
   - Final bracket projections

3. **Selection Sunday** (March 15, 2026)
   - Compare predictions to actual seeding
   - Identify over/under-seeded teams
   - Find bracket pool edges

4. **Tournament Play** (March 19 - April 6)
   - Live game predictions and betting edges
   - Update models with each round
   - Track bracket performance

## 🔧 Advanced Usage

### Edge Finding
```bash
# Find edges across multiple models
python3 scripts/edge_finder.py scan --sources all --min-edge 5.0

# Backtest edge finding performance  
python3 scripts/edge_finder.py backtest --start-date 2025-01-01

# Today's best opportunities
python3 scripts/edge_finder.py today --min-edge 3.0
```

### Historical Analysis
```bash
# Download Kaggle March Madness data
python3 scripts/kaggle_data.py download

# Analyze seed performance
python3 scripts/kaggle_data.py analyze --type seeds --years 2019-2024

# Load specific datasets
python3 scripts/kaggle_data.py load --dataset seeds --year 2024
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Additional data sources
- Enhanced prediction models  
- Better web scraping (handling Cloudflare, etc.)
- Visualization tools
- Machine learning models

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. All data is from publicly available sources. Users are responsible for compliance with terms of service of data providers and applicable laws regarding sports betting.

## 🔗 Related Projects

- [OpenClaw](https://github.com/openclaw/openclaw) - The AI automation platform this skill was built for
- [CBBpy](https://github.com/adcox/CBBpy) - Python package for college basketball data
- [Kaggle March Madness](https://www.kaggle.com/competitions/march-machine-learning-mania-2025) - Annual prediction competition

---

**Built for [OpenClaw](https://openclaw.com) - AI that does things.**