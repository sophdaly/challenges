"""
Helper functions for generating features
"""
from src.utilities import add_info_a
import pandas as pd
import numpy as np


def encode_categorical_field(features_df, field):
    """
    One hot encode categorical data
    Return label encoded values and corresponding encoding list for decoding
    """
    dummies = features_df[field].str.get_dummies()
    encoded_df = pd.concat([features_df, dummies], axis=1)
    encoded_fields = list(dummies.columns)

    return encoded_df, encoded_fields


def add_target_info(features_df):
    """
    For each player check and add target by updating features_df with bool
    representing whether they actually did beat their NEXT year's score
    """
    total_dfs = []
    players = list(set(features_df.player))

    for player in players:
        df = features_df.loc[features_df.player == player]
        # Order by start year in ASCENDING order to subtract next year's points
        df = df.sort_values(by='year_start', ascending=True)
        # Get consecutive differences to determine whether total scores
        # increased/decreased in the next year
        df['temp_delta'] = df['total_score'].shift(-1) - df['total_score']
        total_dfs.append(df)

    # Combine all player dfs
    data = pd.concat(total_dfs, ignore_index=True)

    data['target'] = data.temp_delta.apply(_beat_score)

    # Remove temp_delta as we don't need this and it's confusing with previous
    # year delta score features
    data = data.drop(columns=['temp_delta'])

    return data


def get_previous_score_info(features_df):
    """
    For each player check and update features_df with info about whether they
    beat their PREVIOUS score and what the delta was
    """
    total_dfs = []
    players = list(set(features_df.player))

    for player in players:
        df = features_df.loc[features_df.player == player]
        # Order by start year in DESCENDING order so as to subtract last years
        # scores if they exist
        df = df.sort_values(by='year_start', ascending=False)
        # Get consecutive differences to determine whether total scores
        # increased/decreased in the past year
        df['previous_delta'] = df['total_score'] - df['total_score'].shift(-1)
        total_dfs.append(df)

    # Combine all player dfs
    results = pd.concat(total_dfs, ignore_index=True)

    results['beat_previous_score'] = results.previous_delta.apply(_beat_score)

    return results


def get_season_features(df):
    """
    For each player per season, concatenate the following into dataframe
    - team
    - number of games they scored
    - mean score
    """
    seasons = list(set(df.season))

    total_seasons = []
    total_players = []
    total_scores = []
    total_mean_scores = []
    total_max_scores = []
    total_season_games = []
    total_teams = []
    actual_scores = []

    for season in sorted(seasons):

        # Filter by season
        season_df = df.loc[df.season == season]

        players = list(set(season_df.player))

        for player in players:
            scores_per_game = []

            # Filter by games where player scored
            player_df = season_df.loc[season_df.player == player]

            # Get team
            team = _get_team(player_df)

            # Iterate through each game
            games = player_df.groupby('game_id')

            for game_id, game_df in games:
                game_score = game_df.shot_made.sum()

                scores_per_game.append(game_score)

            if scores_per_game:
                total_seasons.append(season)
                total_players.append(player)
                total_teams.append(team)
                total_mean_scores.append(np.mean(scores_per_game))
                total_max_scores.append(np.max(scores_per_game))
                total_season_games.append(len(scores_per_game))
                total_scores.append(sum(scores_per_game))
                actual_scores.append(scores_per_game)

    # Store everything in dataframe
    results = pd.DataFrame({
        'year_start': [_get_year_start(i) for i in total_seasons],
        'season': total_seasons,
        'player': total_players,
        'team': total_teams,
        'total_score': total_scores,
        'mean_score': total_mean_scores,
        'max_score': total_max_scores,
        'num_games': total_season_games,
        'actual_scores': actual_scores
    })

    return results


def _beat_score(delta):
    if np.isnan(delta):
        return -1
    elif delta > 0:
        return 1
    else:
        return 0


def _get_team(player_df):
    """
    VERY HACKY
    Assumes that players stay with same team all season (hope this is true?)
    """
    # Only include cases where 2 free throws awarded
    player_df = player_df.loc[player_df.play.str.contains('of 2')]

    # Take top two rows
    for i in range(0, len(player_df), 2):
        next_two = player_df[i: i + 2]

        if len(next_two) == 2:
            # Get start and end scores
            start_score = list(next_two.score)[0]
            end_score = list(next_two.score)[1]

            # As long as start != end we can assign team
            if start_score != end_score:
                # If score a increased then assign team_a
                start_score_a = int(add_info_a(end_score))
                end_score_a = int(add_info_a(end_score))
                if end_score_a > start_score_a:
                    return list(next_two.team_a)[0]
                else:
                    return list(next_two.team_b)[0]
            else:
                pass

    return "na"


def _get_year_start(season):
    return int(add_info_a(season))
