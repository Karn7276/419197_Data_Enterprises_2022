import pandas as pd


def JH_data_Extraction():
    """ Creation of relative data

    """

    path = r'C:\Users\HP\Desktop\pythonProject/data/raw/COVID-19/csse_covid_19_data/csse_covid_19_time_series' \
           r'/time_series_covid19_confirmed_global.csv '
    df_raw = pd.read_csv(path, delimiter=",")
    df_db = df_raw.rename(columns={'Country/Region': 'country',
                                   'Province/State': 'state'})

    df_db['state'] = df_db['state'].fillna('no')

    df_db = df_db.drop(['Lat', 'Long'], axis=1)

    df_rel = df_db.set_index(['state', 'country']) \
        .T \
        .stack(level=[0, 1]) \
        .reset_index() \
        .rename(columns={'level_0': 'date',
                         0: 'confirmed'},
                )

    df_rel['date'] = df_rel.date.astype('datetime64[ns]')

    df_rel.to_csv(r'C:\Users\HP\Desktop\pythonProject\data/COVID_relational_confirmed.csv', sep=';', index=False) # Change directory path as per your need
    print(' Stored rows: ' + str(df_rel.shape[0]))
    print(' Latest date is: ' + str(max(df_rel.date)))


if __name__ == '__main__':
    JH_data_Extraction()
