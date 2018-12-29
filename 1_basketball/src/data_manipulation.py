"""
Helper functions for data analysis
"""
import pandas as pd


def get_winning_teams_per_season(df):
    """
    For each input season figure out which of 16 teams came first and second
    Assumpution: team who wins the most games is playoffs winner?
    """
    first_place, second_place = {}, {}
    seasons = list(set(df.season))

    for season in sorted(seasons):
        # Filter by season
        season_df = df.loc[df.season == season]

        # Get team with max number of games won
        winning_counts = season_df.groupby('winner').game_id.nunique()
        winning_ordred = winning_counts.sort_values(ascending=False).index
        first_place[season] = winning_ordred[0]
        second_place[season] = winning_ordred[1]

    return first_place, second_place


def get_top_scoring_teams_per_season(df):
    """
    For each input season figure out which team was top scorer
    """
    top_scorers = {}
    seasons = list(set(df.season))

    teams = list(set(df.team_a) | set(df.team_b))

    # Iterate through seasons
    for season in sorted(seasons):
        # Filter by season
        season_df = df.loc[df.season == season]

        # Keep track of top score and corresponding team
        top_score = 0
        top_team = teams[0]
        # Iterate through teams
        for team in teams:
            score = _count_scores(df=season_df, team=team)
            # Update trackers
            if score > top_score:
                top_score = score
                top_team = team

        top_scorers[season] = top_team

    return top_scorers


def create_team_per_season_scores_df(df, teams_per_season_dict):
    """
    Create and return dataframe containing total scores per input season per
    corresponding team
    """
    total_scores = []

    total_seasons = list(teams_per_season_dict.keys())

    # Iterate through seasons
    for season in sorted(total_seasons):
        # Filter by season
        season_df = df.loc[df.season == season]

        # Get specific team
        team = teams_per_season_dict[season]

        # Get total scores for specific team
        scores = _count_scores(df=season_df, team=team)

        # Update total_scores
        total_scores.append(scores)

    # Create dataframe
    scores_df = pd.DataFrame({
        'season': total_seasons,
        'team': [teams_per_season_dict[i] for i in total_seasons],
        'score': total_scores
    })

    # Sort by season
    scores_df = scores_df.set_index('season').sort_index()

    return scores_df


def add_winning_team(row):
    if row['score_a'] > row['score_b']:
        return row['team_a']
    elif row['score_b'] > row['score_a']:
        return row['team_a']
    else:
        return 'draw'


def _count_scores(df, team):
    # Remove duplicates by game id - keeping last entry
    df = df.drop_duplicates(subset='game_id', keep='last')

    # Filter games where team scored
    team_a_df = df.loc[df.team_a == team]
    team_b_df = df.loc[df.team_b == team]

    # Return sum total scores
    return team_a_df.score_a.sum() + team_b_df.score_b.sum()

