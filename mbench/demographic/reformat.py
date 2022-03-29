import pandas as pd


def adm1_name(
    df,
    original_column_name: str = "adm1",
    new_column_name: str = "adm1",
    set_index: bool = True,
):
    """
    pd dataframe reformater for the pandas dataframe.
    This function is suggested to run every time when importing data from external resource, to ensure the adm1 level district in the Country could be matched to each other.
    - adm1_name_reformat(), when given a `pandas.DataFrame` object and a target column, this function will
    - Uppercase() the values in the column
    - Substitute space to underscore
    - Substitute - to underscore
    - (Optional) `pd.set_index` using formatted adm1 column
    :param set_index:
    :param df:
    :param original_column_name:
    :param new_column_name:
    :return: new pandas DataFrame
    """

    assert type(original_column_name) is str
    # 1. Rename the column name to new_column_name
    if type(df) is pd.DataFrame:
        df = df.rename(columns={original_column_name: new_column_name})
        # 2. reformat district name
        ## to upper case
        df[new_column_name] = df[new_column_name].map(lambda x: x.upper())
        ## change space to _
        df[new_column_name] = df[new_column_name].map(lambda x: x.replace(" ", "_"))
        ## change - to _
        df[new_column_name] = df[new_column_name].map(lambda x: x.replace("-", "_"))

        # 3. set index to the new column name
        if set_index:
            df = df.set_index(new_column_name)
    elif type(df) is pd.Series:
        df = df.rename(new_column_name)
        # 2. reformat district name
        ## to upper case
        df.index = df.index.map(lambda x: x.upper())
        ## change space to _
        df.index = df.index.map(lambda x: x.replace(" ", "_"))
        ## change - to _
        df.index = df.index.map(lambda x: x.replace("-", "_"))

    return df
