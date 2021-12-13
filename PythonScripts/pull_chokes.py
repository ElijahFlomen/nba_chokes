import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder, playbyplay, winprobabilitypbp
from nba_api.stats.library.parameters import Season, SeasonType

def main():

    team_ls = pd.DataFrame(teams.get_teams())
    team_ids = list(team_ls.id)
    tos = 1 # read timeout number (RT#)
    seasons = ["2018-19", "2017-18"] #"2018-19", "2019-20", "2020-21", 
    season_types = ["Regular Season", "Playoffs"]

    chokes_df = pd.DataFrame({"game_id": [], "season": [], "home_team": [], "away_team": [], "home_choke": []})
    for season in seasons:
        for season_type in season_types:
            for team in team_ids:
                team = int(team)
                # grab game ids for each team
                games = leaguegamefinder.LeagueGameFinder(team_id_nullable=team,
                                        season_nullable=season,
                                        season_type_nullable=season_type)
                games = pd.DataFrame(games.get_normalized_dict()["LeagueGameFinderResults"])
                for i in range(games.shape[0]):
                    game_number = games.iloc[i].GAME_ID
                    if game_number not in list(chokes_df.game_id):
                        try:
                            win_prob = winprobabilitypbp.WinProbabilityPBP(game_number).get_data_frames()[0]
                            win_prob = win_prob[["HOME_PCT", "HOME_PTS", "VISITOR_PTS"]].dropna(subset=["HOME_PTS", "VISITOR_PTS"])
                            # print(win_prob.head())
                            max_pct = win_prob.HOME_PCT.max()
                            min_pct = win_prob.HOME_PCT.min()
                            print(max_pct, min_pct)
                            if win_prob.HOME_PCT.max() > 0.9 and win_prob.HOME_PTS.iloc[-1] < win_prob.VISITOR_PTS.iloc[-1]:
                                # home choke case
                                matchup = games.loc[i, 'MATCHUP'].split()
                                choke = 1
                                if "vs." in matchup[1]:
                                    home = matchup[0]
                                    away = matchup[2]
                                else:
                                    away = matchup[0]
                                    home = matchup[2]
                
                                chokes_df.loc[len(chokes_df.index)] = [game_number, season, home, away, choke]
                                print('home choke')

                            elif win_prob.HOME_PCT.min() < 0.1 and win_prob.HOME_PTS.iloc[-1] > win_prob.VISITOR_PTS.iloc[-1]:
                                # away choke case
                                matchup = games.loc[i, 'MATCHUP'].split()
                                choke = 0
                                if "vs." in matchup[1]:
                                    home = matchup[0]
                                    away = matchup[2]
                                else:
                                    away = matchup[0]
                                    home = matchup[2]
                
                                chokes_df.loc[len(chokes_df.index)] = [game_number, season, home, away, choke]
                                print('away choke')
                        except:
                            print(tos)
                            tos += 1
                        time.sleep(1)
                    time.sleep(1)
                time.sleep(1)
    chokes_df.to_csv('choke_list_171819.csv', index=False)

if __name__ == "__main__":
    main()


