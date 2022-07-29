from datetime import datetime

import numpy as np
import pandas as pd


def Sir_model_data():
    data_path = r'C:\Users\HP\Desktop\pythonProject/data/raw/COVID-19/csse_covid_19_data/csse_covid_19_time_series' \
                r'/time_series_covid19_confirmed_global.csv '
    pd_raw = pd.read_csv(data_path)
    time_idx = pd_raw.columns[4:]
    df_plot = pd.DataFrame({
        'date': time_idx})
    country_list = ['India',
                    'US',
                    'Spain',
                    'Germany',
                    'France',
                    ]
    for each in country_list:
        df_plot[each] = np.array(pd_raw[pd_raw['Country/Region'] == each].iloc[:, 4::].sum(axis=0))
    time_idx = [datetime.strptime(each, "%m/%d/%y") for each in df_plot.date]  # convert to datetime
    time_str = [each.strftime('%Y-%m-%d') for each in time_idx]  # convert back to date ISO norm (str)
    df_plot['date'] = time_idx
    #print(df_plot)
    df_plot.to_csv(r'C:\Users\HP\Desktop\pythonProject/data/processed/COVID_small_flat_table.csv', sep=';', index=False)


if __name__ == '__main__':
    Sir_model_data()
