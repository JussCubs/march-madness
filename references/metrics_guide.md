# Basketball Analytics Metrics Guide

A comprehensive guide to understanding advanced basketball metrics used in March Madness prediction models.

## Core Efficiency Metrics

### Offensive Efficiency (OE)
- **Definition**: Points scored per 100 possessions
- **Formula**: (Points Scored × 100) / Possessions Used
- **Interpretation**: Higher values indicate better offensive performance
- **Sources**: KenPom, T-Rank, BPI
- **Typical Range**: 90-130 (Division I)

### Defensive Efficiency (DE)
- **Definition**: Points allowed per 100 possessions
- **Formula**: (Points Allowed × 100) / Opponent Possessions
- **Interpretation**: Lower values indicate better defensive performance
- **Sources**: KenPom, T-Rank, BPI
- **Typical Range**: 85-120 (Division I)

### Net Efficiency (NetRtg)
- **Definition**: Offensive Efficiency minus Defensive Efficiency
- **Formula**: OE - DE
- **Interpretation**: Point differential per 100 possessions
- **Sources**: All major analytics sites
- **Typical Range**: -30 to +30 (Division I)

## Tempo Metrics

### Pace (Tempo)
- **Definition**: Possessions per 40-minute game
- **Formula**: Estimated possessions in a 40-minute game
- **Interpretation**: Higher = faster tempo, more possessions
- **Sources**: KenPom, T-Rank, BPI
- **Typical Range**: 60-80 possessions per game

### Effective Possession Length
- **Definition**: Average seconds per possession
- **Formula**: (Game Length in Seconds) / Total Possessions
- **Interpretation**: Measures pace of play
- **Sources**: Advanced analytics sites

## Shooting Metrics

### Effective Field Goal Percentage (eFG%)
- **Definition**: Field goal percentage adjusted for 3-point value
- **Formula**: (FGM + 0.5 × 3PM) / FGA
- **Interpretation**: Better measure than raw FG% due to 3-point weighting
- **Sources**: All major statistics platforms
- **Typical Range**: 45%-65% (Division I)

### True Shooting Percentage (TS%)
- **Definition**: Shooting percentage accounting for 2s, 3s, and free throws
- **Formula**: Points / (2 × (FGA + 0.44 × FTA))
- **Interpretation**: Most comprehensive shooting efficiency metric
- **Sources**: Advanced analytics sites
- **Typical Range**: 50%-65% (Division I)

### 3-Point Rate (3PAr)
- **Definition**: Percentage of field goal attempts that are 3-pointers
- **Formula**: 3PA / FGA
- **Interpretation**: Measures reliance on 3-point shooting
- **Sources**: All statistics platforms
- **Typical Range**: 30%-50% (modern college basketball)

## Rebounding Metrics

### Offensive Rebounding Percentage (OR%)
- **Definition**: Percentage of available offensive rebounds obtained
- **Formula**: OR / (OR + Opponent DR)
- **Interpretation**: Measures offensive rebounding ability
- **Sources**: All major analytics sites
- **Typical Range**: 20%-40% (Division I)

### Defensive Rebounding Percentage (DR%)
- **Definition**: Percentage of available defensive rebounds obtained
- **Formula**: DR / (DR + Opponent OR)
- **Interpretation**: Measures defensive rebounding ability
- **Sources**: All major analytics sites
- **Typical Range**: 60%-80% (Division I)

### Total Rebounding Percentage (TR%)
- **Definition**: Percentage of available rebounds obtained
- **Formula**: (OR + DR) / (OR + DR + Opponent OR + Opponent DR)
- **Sources**: All major analytics sites

## Turnover Metrics

### Turnover Percentage (TO%)
- **Definition**: Turnovers per 100 possessions used
- **Formula**: (TO × 100) / Possessions
- **Interpretation**: Lower is better for offense, higher is better for defense
- **Sources**: All major analytics sites
- **Typical Range**: 15%-25% (Division I)

### Steal Percentage (Stl%)
- **Definition**: Steals per 100 opponent possessions
- **Formula**: (Steals × 100) / Opponent Possessions
- **Interpretation**: Measures defensive pressure and turnover generation
- **Sources**: Advanced analytics sites
- **Typical Range**: 5%-15% (Division I)

## Rating Systems

### T-Rank (Barttorvik)
- **Definition**: Tempo-free rating system similar to KenPom methodology
- **Components**: Adjusted efficiency margins, strength of schedule
- **Scale**: Typically 0-30+ (higher = better)
- **Source**: barttorvik.com
- **Free Access**: Yes

### NET Rating (NCAA)
- **Definition**: NCAA Evaluation Tool for tournament selection
- **Components**: Game results, strength of schedule, location, margin of victory (capped)
- **Scale**: 1-358 ranking (lower = better)
- **Source**: NCAA official
- **Tournament Use**: Primary selection committee tool

### BPI (ESPN)
- **Definition**: Basketball Power Index
- **Components**: Efficiency metrics, strength of schedule, pace
- **Scale**: Typically 0-30+ (higher = better)
- **Source**: ESPN
- **Access**: Free on ESPN.com

### KenPom Rating
- **Definition**: Adjusted efficiency margin
- **Formula**: Offensive Efficiency - Defensive Efficiency (vs average)
- **Scale**: Typically -30 to +30 (higher = better)
- **Source**: kenpom.com
- **Access**: $20/year subscription

### Sagarin Rating
- **Definition**: Computer rating based on margin of victory and strength of schedule
- **Components**: Pure points, recent performance weighting
- **Scale**: Typically 50-100 (higher = better)
- **Source**: sagarin.com
- **Access**: Free

## Strength of Schedule Metrics

### Adjusted Schedule Strength
- **Definition**: Average efficiency of opponents faced
- **Calculation**: Weighted average of opponent ratings
- **Sources**: KenPom, T-Rank, NET system

### Non-Conference SOS
- **Definition**: Strength of schedule for non-conference games only
- **Use**: Tournament selection evaluation
- **Sources**: Warren Nolan, NCAA evaluation

### Quadrant Records (NCAA)
- **Quad 1**: Home vs 1-30, Neutral vs 1-50, Away vs 1-75 (NET ranking)
- **Quad 2**: Home vs 31-75, Neutral vs 51-100, Away vs 76-135
- **Quad 3**: Home vs 76-160, Neutral vs 101-200, Away vs 136-240
- **Quad 4**: All other games
- **Tournament Use**: Selection committee heavily weighs Quad 1 wins

## Advanced Metrics

### Win Probability Models
- **Definition**: Probability of winning based on current game metrics
- **Inputs**: Score, time remaining, possession, team efficiency ratings
- **Sources**: KenPom, ESPN, T-Rank game predictions

### Point Spread Predictions
- **Definition**: Expected margin of victory in neutral site game
- **Formula**: Team Rating Difference × Pace Adjustment
- **Sources**: All major prediction models
- **Betting Use**: Compare to actual lines for edge identification

### Over/Under Predictions
- **Definition**: Expected total points in game
- **Formula**: (Team 1 OE + Team 2 DE) + (Team 2 OE + Team 1 DE) / 2 × Pace / 100
- **Sources**: Advanced analytics sites
- **Betting Use**: Compare to posted totals

## Model Performance Metrics

### Log-Loss (Brier Score)
- **Definition**: Measures accuracy of probabilistic predictions
- **Formula**: -Σ(y × log(p) + (1-y) × log(1-p))
- **Interpretation**: Lower is better (0 = perfect)
- **Use**: Comparing prediction model accuracy

### ATS (Against the Spread) Record
- **Definition**: Wins vs losses when betting against point spreads
- **Calculation**: Compare predicted margin to actual spread
- **Use**: Measuring betting model profitability

### ROI (Return on Investment)
- **Definition**: Profit percentage from betting model
- **Formula**: (Profit - Initial Investment) / Initial Investment
- **Use**: Measuring overall betting performance

## Tournament-Specific Metrics

### Seed Predictiveness
- **Definition**: How well metrics predict tournament seeding
- **Analysis**: Correlation between rating and actual tournament seed
- **Use**: Identifying under/over-seeded teams

### Upset Probability
- **Definition**: Likelihood lower seed beats higher seed
- **Factors**: Efficiency gap, pace differential, experience
- **Historical**: Used for bracket pool strategy

### Championship Probability
- **Definition**: Probability of winning entire tournament
- **Calculation**: Product of individual game win probabilities
- **Sources**: KenPom, T-Rank tournament simulations

## Data Quality Notes

### Garbage Time Adjustment
- **Issue**: Blowout games can skew efficiency metrics
- **Solution**: Many systems adjust or remove garbage time possessions
- **Impact**: More accurate reflection of true team strength

### Home Court Advantage
- **Typical Value**: 3-4 point advantage in college basketball
- **Adjustment**: Neutral site predictions adjust for venue
- **Tournament**: All games neutral site (mostly)

### Sample Size Considerations
- **Early Season**: Small samples, high variance in metrics
- **Conference Play**: More stable, predictive metrics
- **Tournament**: Single elimination reduces sample size impact

## Using Metrics for Predictions

### Model Building Approach
1. **Feature Selection**: Choose most predictive metrics for your model
2. **Recency Weighting**: Weight recent games more heavily
3. **Opponent Adjustment**: Account for strength of schedule
4. **Tournament Context**: Adjust for neutral sites, single elimination
5. **Validation**: Backtest on historical tournament data

### Common Prediction Inputs
- **Efficiency Margins**: Primary predictor of game outcomes
- **Pace**: Affects total points and variance
- **Experience**: Tournament experience, senior leadership
- **Matchup Factors**: Style contrasts, specific strengths/weaknesses
- **Health**: Key player injuries or availability

### Red Flags in Data
- **Small Sample Sizes**: Early season or limited games
- **Schedule Strength Extremes**: All weak or all strong opponents  
- **Injury-Affected Data**: Missing key players during metric calculation
- **Garbage Time**: Blowout games affecting efficiency numbers

## Sources and Tools

### Free Analytics Access
- **Barttorvik.com**: Complete T-Rank system
- **Warren Nolan**: NET rankings, quadrant records
- **Massey Ratings**: Composite of multiple rating systems
- **ESPN**: BPI ratings and basic efficiency stats

### Premium Analytics
- **KenPom.com**: $20/year, gold standard for college basketball analytics
- **Synergy Sports**: Professional scouting platform
- **Torvik Premium**: Enhanced T-Rank features

### Data APIs and Packages
- **CBBpy**: Python package for ESPN data
- **cbbdata (R)**: Barttorvik and KenPom data wrapper
- **hoopR (R)**: SportsDataverse college basketball package
- **sportsreference**: Python Sports Reference scraper

## Glossary

**Adjusted Metrics**: Statistics normalized for pace and opponent strength
**Possession**: One team's opportunity to score (ends in shot, turnover, or foul)
**Tempo-Free**: Statistics per possession rather than per game
**True Shooting**: Comprehensive shooting efficiency including 2s, 3s, and FTs
**Usage Rate**: Percentage of team possessions used by a player when on court
**Value Over Replacement**: Player contribution above a replacement-level player

---

*This guide covers the most important metrics for March Madness prediction modeling. For specific formulas or advanced concepts, consult the original sources (KenPom, Basketball Prospectus, Dean Oliver's "Basketball on Paper").*