import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder, playbyplay, winprobabilitypbp

def main():
    fails = 0
    
    full_df = pd.DataFrame({
        "event" : [],
        "game_id": [],
        "period": [],
        "time_remaining" : [],
        "home_pts": [],
        "visitor_pts": [],
        "home_pct": [],
        "visitor_pct": [],
        "home_desc": [],
        "neut_desc": [],
        "visitor_desc": [],
        "home_short": [],
        "visitor_short": []
    })
    

    chokes_df = pd.read_csv('choke_list_full.csv')

    for idx, row in chokes_df.iterrows():
        game_id = '00' + str(row.game_id)
        try:
            time.sleep(1)
            win_df = winprobabilitypbp.WinProbabilityPBP(game_id=game_id).get_data_frames()[0]
            time.sleep(1)
            pbp_df = playbyplay.PlayByPlay(game_id=game_id).get_data_frames()[0]
            print("Loaded id {} successfully".format(game_id))

            pbp_df['EVENT_NUM'] = pd.to_numeric(pbp_df.EVENTNUM)
            pbp_df = pbp_df.dropna(subset=['EVENT_NUM']).set_index('EVENT_NUM')
            joined = pbp_df.merge(win_df)
            joined = joined[['GAME_ID', 'PERIOD','PCTIMESTRING', 'HOME_PTS', 'VISITOR_PTS', 'HOME_PCT', 'VISITOR_PCT',
                            'HOMEDESCRIPTION', 'NEUTRALDESCRIPTION', 'VISITORDESCRIPTION'
                            ]]
            joined = joined.drop_duplicates(subset=['HOMEDESCRIPTION','VISITORDESCRIPTION', 'NEUTRALDESCRIPTION']).reset_index(drop=True).reset_index()
            joined = joined.rename(columns={
                'index': "event",
                'GAME_ID': "game_id",
                'PERIOD': "period",
                'PCTIMESTRING': "time_remaining",
                'HOME_PTS': "home_pts",
                'VISITOR_PTS': "visitor_pts",
                'HOME_PCT': "home_pct",
                'VISITOR_PCT': "visitor_pct",
                'HOMEDESCRIPTION': "home_desc",
                'NEUTRALDESCRIPTION': "neut_desc",
                'VISITORDESCRIPTION': "visitor_desc"
            })

            joined['home_short']= ''
            joined['visitor_short'] = ''

            for i in joined.index:
                home_desc = joined.loc[i, "home_desc"]
                visitor_desc = joined.loc[i, "visitor_desc"]

                if home_desc is not None and "miss" in home_desc.strip().lower():
                    joined.at[i, 'home_short'] = "miss"

                if home_desc is not None and 'steal' in home_desc.strip().lower():
                    joined.at[i, 'home_short'] = "steal"

                if home_desc is not None and 'rebound' in home_desc.strip().lower():
                    joined.at[i, 'home_short'] = "rebound"

                if home_desc is not None and 'sub' in home_desc.strip().lower():
                    joined.at[i, 'home_short'] = "sub"
                    
                if home_desc is not None and 'block' in home_desc.strip().lower():
                    joined.at[i, 'home_short'] = "block"

                if visitor_desc is not None and "miss" in visitor_desc.strip().lower():
                    joined.at[i, 'visitor_short'] = "miss"

                if visitor_desc is not None and 'steal' in visitor_desc.strip().lower():
                    joined.at[i, 'visitor_short'] = "steal"

                if visitor_desc is not None and 'rebound' in visitor_desc.strip().lower():
                    joined.at[i, 'visitor_short'] = "rebound"

                if visitor_desc is not None and 'sub' in visitor_desc.strip().lower():
                    joined.at[i, 'visitor_short'] = "sub"

                if visitor_desc is not None and 'block' in visitor_desc.strip().lower():
                    joined.at[i, 'visitor_short'] = "block"
                
            full_df = full_df.append(joined)
        except:
            print('FAILED TO LOAD id {}'.format(game_id))
            fails += 1
    full_df.to_csv("pbp_data_full.csv", index=False)
    print("Saved as .csv")
    print(str(fails) + " games failed to load")

if __name__ == '__main__':
    main()
