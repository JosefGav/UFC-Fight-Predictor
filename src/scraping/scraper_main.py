from ufc_scraper import UFCScraper

scraper = UFCScraper()

fights = scraper.get_all_fight_data(10)

import pandas as pd

df = pd.DataFrame(fights)
print(df)

df_modified = df.copy()
df_modified["fighter_a_record"] = df_modified["fighter_a_record"].apply(lambda x: f"\t{x}")
df_modified["fighter_b_record"] = df_modified["fighter_b_record"].apply(lambda x: f"\t{x}")


df_modified.to_csv("fights_data.csv")
