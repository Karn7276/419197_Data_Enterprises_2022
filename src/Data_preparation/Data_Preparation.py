import subprocess
import os
import pandas as pd
import requests
import json


def JH_Data_repo():
    """ Get data by a git pull request, the source code has to be pulled first
        Result is stored in the predefined csv structure
    """
    git_pull = subprocess.Popen("user/bin/JH_Data_gitPull",
                                cwd=os.path.dirname('data/raw/COVID-19/'),
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE) # Change directory path as per your need
    (out, error) = git_pull.communicate()

    print("Error : " + str(error))
    print("out : " + str(out))


def Example_for_Germany():
    """ Get current data from germany, attention API endpoint not too stable
        Result data frame is stored as pd.DataFrame and later saved in CSV file in local drive

    """
    data = requests.get(
        'https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_Landkreisdaten/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json')

    json_object = json.loads(data.content)  # load all data
    German_data_list = []
    for pos, each_dict in enumerate(json_object['features'][:]):
        German_data_list.append(each_dict['attributes'])

    df_Germany = pd.DataFrame(German_data_list)  # prepare a Dataframe containing final data
    df_Germany.to_csv(r'C:\Users\HP\Desktop\pythonProject\data/GER_state_data.csv', sep=';')  # save data as CSV file in needed folder
    print(' Regions rows: ' + str(df_Germany.shape[0]))


if __name__ == '__main__':
    # JH_Data_repo()
    Example_for_Germany()
