import math

import pandas as pd


def missing_data(
        df: pd.DataFrame, neighbour: pd.DataFrame, column: str, round_n: int = 3
):
    """
    Missing_data_interpolate(), when data was missing in some provinces, use this function to interpolate the missing data.
    :param neighbour:
    :param df: pandas dataframe to be processed, the dataframe should firstly be process with reformat function, and the index of df should be adm1 provinces
    :param column: the target column
    :param round_n: round of averaging, the larger number the smoother, but requires more computing power, default is 3
    :return: df: calculated dataframe with filled data
    """

    def get_adjacent(
            adm1: str,
            adjacent_list: pd.DataFrame,
            from_column: str = "from",
            to_column: str = "to",
    ):
        return adjacent_list[adjacent_list[from_column] == adm1][to_column]

    def interpolate(
            _df: pd.DataFrame,
            targeted_adm1: str,
            targeted_column: str,
            adjacent_adm1: pd.Series,
    ):
        adjacent_adm1_row = _df.loc[adjacent_adm1.tolist(), :]
        interpolated = adjacent_adm1_row[targeted_column].mean()
        result_row = _df.loc[targeted_adm1, :]
        result_row[targeted_column] = interpolated
        return result_row

    # 1. notation 标记
    df["__missing"] = df[column].map(lambda x: math.isnan(x))
    # 2. get missing adm1 regions
    for i in range(round_n):
        df = df.apply(
            lambda row: interpolate(
                _df=df,
                targeted_adm1=row.name,
                targeted_column=column,
                adjacent_adm1=get_adjacent(adm1=row.name, adjacent_list=neighbour),
            )
            if row["__missing"]
            else row,
            axis=1,
        )

    df.drop(columns=["__missing"])
    return df
