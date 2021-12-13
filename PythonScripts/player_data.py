import numpy as np
import pandas as pd
import os

def main():
    choke_df = pd.read_csv(os.getcwd() + '/data/choke_list_full.csv')

    choke_pbp = pd.read_csv(os.getcwd() + '/data/pbp_data_full.csv')

    final = pd.DataFrame({'player': [], 'points_bf': [],'points_af': [], 'team': [], 'game_id': []}).set_index('player')

    for idx1, game_meta in choke_df.iterrows():
        game = choke_pbp[choke_pbp.game_id == game_meta.game_id]

        home_df_bf = pd.DataFrame({'player': [], 'points_bf': []})
        home_df_af = pd.DataFrame({'player': [], 'points_af': []})
        away_df_bf = pd.DataFrame({'player': [], 'points_bf': []})
        away_df_af = pd.DataFrame({'player': [], 'points_af': []})
        if game_meta.home_choke == 1:
            choke_point = game['home_pct'].idxmax()
        else:
            choke_point = game['visitor_pct'].idxmax()
        
        for idx, row in game.iterrows():
            if idx < choke_point:
                if row.home_desc is not np.NaN and 'pts' in row.home_desc.strip().lower():
                    desc_list = row.home_desc.split()
                    player = desc_list[0]
                    pts = [i[1:] for i in desc_list if '(' in i][0]
                    home_df_bf.loc[len(home_df_bf.index)] = [player, int(pts)]
                elif row.visitor_desc is not np.NaN and 'pts' in row.visitor_desc.strip().lower():
                    desc_list = row.visitor_desc.split()
                    player = desc_list[0]
                    pts = [i[1:] for i in desc_list if '(' in i][0]
                    away_df_bf.loc[len(away_df_bf.index)] = [player, int(pts)]
            else:
                if row.home_desc is not np.NaN and 'pts' in row.home_desc.strip().lower():
                    desc_list = row.home_desc.split()
                    player = desc_list[0]
                    pts = [i[1:] for i in desc_list if '(' in i][0]
                    home_df_af.loc[len(home_df_af.index)] = [player, int(pts)]
                elif row.visitor_desc is not np.NaN and 'pts' in row.visitor_desc.strip().lower():
                    desc_list = row.visitor_desc.split()
                    player = desc_list[0]
                    pts = [i[1:] for i in desc_list if '(' in i][0]
                    away_df_af.loc[len(away_df_af.index)] = [player, int(pts)]

        home_df_bf = home_df_bf.groupby(['player'], sort=False)['points_bf'].max()
        home_df_af = home_df_af.groupby(['player'], sort=False)['points_af'].max()
        away_df_bf = away_df_bf.groupby(['player'], sort=False)['points_bf'].max()
        away_df_af = away_df_af.groupby(['player'], sort=False)['points_af'].max()
        home = pd.concat([home_df_bf, home_df_af], axis=1)
        home['team'] = 'home'
        away = pd.concat([away_df_bf, away_df_af], axis=1)
        away['team'] = 'visitor'
        total = home.append(away)
        total['game_id'] = game_meta.game_id
        total = total.fillna(0)
        total.points_af = total.points_af - total.points_bf
        total.points_af = total.points_af.clip(lower=0)

        final = final.append(total)
        print(game_meta.game_id)
    
    final.to_csv('data/player_scoring_data.csv')
    print("saved")

if __name__ == "__main__":
    main()



