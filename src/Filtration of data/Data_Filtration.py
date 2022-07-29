import pandas as pd
import numpy as np

from sklearn import linear_model
from scipy import signal

reg = linear_model.LinearRegression(fit_intercept=True)


def doubling_T_via_reg(in_array):
    """ Using a linear regression to calculate the doubling rate
        Parameters:
        ----------
        in_array : pandas.series

        Returns:
        ----------
        Doubling rate: double
    """

    y = np.array(in_array)
    X = np.arange(-1, 2).reshape(-1, 1)  # shaping x, y arrays

    assert len(in_array) == 3
    reg.fit(X, y)  # regression
    intercept = reg.intercept_
    slope = reg.coef_

    return intercept / slope


def savgol_fil(input_data, column='confirmed', window=5):
    """ Savgol Filter which can be used in groupby apply function (data structure kept)
        parameters:
        ----------
        input_data : pandas.series
        column : str
        window : int
            used data points to calculate the filter result

        Returns:
        ----------
        df_result: pd.DataFrame
            the index of the input_data has to be preserved in result
    """

    degree = 1
    df_result = input_data

    filter_in = input_data[column].fillna(0)  # attention with the neutral element here

    result = signal.savgol_filter(np.array(filter_in),
                                  window,  # window size used for filtering
                                  1)
    df_result[str(column + '_filtered')] = result
    return df_result


def rolling_reg(input_data, col='confirmed'):
    """ Rolling Regression to approximate the doubling time'
        Parameters:
        ----------
        input_data: pd.DataFrame
        col: str
            defines the used column
        Returns:
        ----------
        result: pd.DataFrame
    """
    days_back = 3
    result = input_data[col].rolling(
        window=days_back,
        min_periods=days_back).apply(doubling_T_via_reg, raw=False)

    return result


def filtered_data(input_data, filter_on='confirmed'):
    """  Calculate savgol filter and return merged data frame
        Parameters:
        ----------
        input_data: pd.DataFrame
        filter_on: str
            defines the used column
        Returns:
        ----------
        output: pd.DataFrame
            the result will be joined as a new column on the input data frame
    """

    must_contain = set(['state', 'country', filter_on])
    assert must_contain.issubset(set(input_data.columns)), ' Error in filtered_data not all columns in data frame'

    output = input_data.copy()  # we need a copy here otherwise the filter_on column will be overwritten

    pd_filtered_result = output[['state', 'country', filter_on]].groupby(['state', 'country']).apply(
        savgol_fil)  # .reset_index()

    output = pd.merge(output, pd_filtered_result[[str(filter_on + '_filtered')]], left_index=True,
                      right_index=True, how='left')
    return output.copy()


def doubling_rate(input_data, filter_on='confirmed'):
    """ Calculate approximated doubling rate and return merged data frame
        Parameters:
        ----------
        input_data: pd.DataFrame
        filter_on: str
            defines the used column
        Returns:
        ----------
        output: pd.DataFrame
            the result will be joined as a new column on the input data frame
    """

    must_contain = set(['state', 'country', filter_on])
    assert must_contain.issubset(set(input_data.columns)), ' Error in filtered_data not all columns in data frame'

    pd_DR_result = input_data.groupby(['state', 'country']).apply(rolling_reg, filter_on).reset_index()

    pd_DR_result = pd_DR_result.rename(columns={filter_on: filter_on + '_DR',
                                                'level_2': 'index'})

    # Merging on the index of our big table and on the index column after groupby
    output = pd.merge(input_data, pd_DR_result[['index', str(filter_on + '_DR')]], left_index=True, right_on=['index'],
                      how='left')
    output = output.drop(columns=['index'])

    return output


if __name__ == '__main__':
    # select directory path as per your folder structure
    JH_data = pd.read_csv(r'/data/COVID_relational_confirmed.csv', sep=';', parse_dates=[0])
    JH_data = JH_data.sort_values('date', ascending=True).copy()
    result_larg = filtered_data(JH_data)
    result_larg = doubling_rate(result_larg)
    result_larg = doubling_rate(result_larg, 'confirmed_filtered')

    mask_data = result_larg['confirmed'] > 100
    result_larg['confirmed_filtered_DR'] = result_larg['confirmed_filtered_DR'].where(mask_data, other=np.NaN)
    result_larg.to_csv(r'C:\Users\HP\Desktop\pythonProject\data/processed/COVID_final_set.csv', sep=';', index=False)
