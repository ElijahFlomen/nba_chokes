import pandas as pd
import numpy as np
import os
import json


def main(filepath):
    cwd = os.getcwd()
    df_players = pd.read_csv(cwd + 'data/player_scoring_data.csv')
    df_games = pd.read_csv(cwd + 'data/choke_list_full.csv')
    df_pbp = pd.read_csv(cwd + 'data/pbp_data_full.csv')

    ## shorten dataframes to playoff only games
    df_pbp = df_pbp[df_pbp.game_id > 40000000]
    df_players = df_players[df_players.game_id > 40000000]
    df_games = df_games[df_games.game_id > 40000000]
    df_pbp.loc[(df_pbp.home_pct == 0.62946), 'event']

    # create dictionary with the information we need each game
    d2 = dict()
    for idx, row in df_games.iterrows():
        matchup = row.away_team + " @ " + row.home_team
        season = row.season
        game_id = row.game_id
        box_score = df_players[df_players.game_id == game_id]
        pbp = df_pbp[df_pbp.game_id == game_id]
        total_before = box_score.points_bf.sum()
        home_before = box_score[box_score.team == "home"].points_bf.sum()
        away_before = box_score[box_score.team == "visitor"].points_bf.sum()

        total_after = box_score.points_af.sum()
        home_after = box_score[box_score.team == "home"].points_af.sum()
        away_after = box_score[box_score.team == "visitor"].points_af.sum()

        #locate top 3 scorers on each side before infelction
        home_top3 = list(box_score[box_score.team == "home"].nlargest(3, 'points_bf')["player"])

        away_top3 = list(box_score[box_score.team == "visitor"].nlargest(3, 'points_bf')["player"])

        #find home percentages
        top3_home_pts_before = 0
        top3_home_pts_after = 0
        for home_player in home_top3:
            top3_home_pts_before += box_score.loc[(box_score.player == home_player), 'points_bf'].iloc[0]
            top3_home_pts_after += box_score.loc[(box_score.player == home_player), 'points_af'].iloc[0]
        top3_home_before = np.around(top3_home_pts_before / total_before, 5)
        top3_home_after = np.around(top3_home_pts_after / total_after, 5)
        bottom_home_pts_before = np.around((home_before - top3_home_pts_before) / total_before, 5)
        bottom_home_pts_after = np.around((home_after - top3_home_pts_after) / total_after, 5)
        # print(top3_home_before, top3_home_after, bottom_home_pts_before, bottom_home_pts_after)
        #find away percentages
        top3_away_pts_before = 0
        top3_away_pts_after = 0
        for away_player in away_top3:
            top3_away_pts_before += box_score.loc[(box_score.player == away_player), 'points_bf'].iloc[0]
            top3_away_pts_after += box_score.loc[(box_score.player == away_player), 'points_af'].iloc[0]
        top3_away_before = np.around(top3_away_pts_before / total_before, 5)
        top3_away_after = np.around(top3_away_pts_after / total_after, 5)
        bottom_away_pts_before = np.around((away_before - top3_away_pts_before) / total_before, 5)
        bottom_away_pts_after = np.around((away_after - top3_away_pts_after) / total_after, 5)
        # find the inflection point
        num_events = pbp.loc[(pbp.event == pbp.event.max()), 'event'].iloc[0]
        if row.home_choke == 1:
            infelction_event = pbp.loc[(pbp.home_pct == pbp.home_pct.max()), 'event'].iloc[0]
            infelction_pct = np.around(infelction_event / num_events, 5)
        else:
            infelction_event = pbp.loc[(pbp.home_pct == pbp.home_pct.min()), 'event'].iloc[0]
            infelction_pct = np.around(infelction_event / num_events, 5)
        
        # create dictionaries with values
        before_dict = {
            "game_pct": infelction_pct,
            "season": season,
            "home_top3_pct": top3_home_before,
            "home_bottom_pct": bottom_home_pts_before,
            "away_top3_pct": top3_away_before,
            "away_bottom_pct": bottom_away_pts_before
            }
        after_dict = {
            "game_pct": np.around(1 - infelction_pct, 5),
            "season": season,
            "home_top3_pct": top3_home_after,
            "home_bottom_pct": bottom_home_pts_after,
            "away_top3_pct": top3_away_after,
            "away_bottom_pct": bottom_away_pts_after
        }

        # add game to dictionary of games
        if matchup not in d2.keys():
            d2[matchup] = [before_dict, after_dict]
        else:
            d2[matchup + ' 2'] = [before_dict, after_dict]

    with open(filepath, 'w') as out:
        json.dump(d2, out, indent=4)

if __name__ == "__main__":
    filepath = "interactive_data.json"
    main(filepath)