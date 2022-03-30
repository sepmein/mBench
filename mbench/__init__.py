"""_summary_

    Returns:
        _type_: _description_
"""
from abc import abstractmethod
import math
from dataclasses import dataclass
from math import log10
from tkinter import W
from typing import Annotated, Any, Callable, Iterator, Optional, Union, Type

import pandas as pd

import mbench.demographic
import mbench.intervention
import mbench.util


class Parameter:
    """_summary_"""

    _value: Any = None

    def __init__(
        self, name: str, default_value: Any, aliases: list[str] = None
    ) -> None:
        self.name = name
        self.default_value = default_value
        self.aliases = aliases

    @property
    def value(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._value

    @value.setter
    def value(self, value):
        """_summary_

        Args:
            value (_type_): _description_
        """
        self._value = value


class ParameterConverter:
    """_summary_"""

    def __init__(
        self,
        start: Union[list[Type[Parameter]], Type[Parameter]],
        to: Type[Parameter],
        fn: Callable,
    ) -> None:
        """_summary_

        Args:
            start (Union[list[Type[Parameter]], Type[Parameter]]): _description_
            to (Type[Parameter]): _description_
            fn (Callable): _description_
        """
        self.start = start
        self.to = to
        self.fn = fn

    def convert(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.fn(self.start.value, self.to.value)


@dataclass
class ValueRange:
    min: float = -math.inf
    max: float = math.inf

    def validate_value(self, x):
        if not (self.min <= x <= self.max):
            raise ValueError(f"{x} must be in range [{self.min}, {self.max}]")


class Prevalence(Parameter):
    def __init__(
        self,
        default_value: Annotated[float, ValueRange(0.0, 1.0)] = None,
        name: str = "Prevalence",
        aliases: list[str] = None,
    ) -> None:
        super().__init__(name, default_value, aliases)


class EIR(Parameter):
    def __init__(
        self,
        default_value: Annotated[float, ValueRange(0.0)] = None,
        name: str = "EIR",
        aliases=None,
    ) -> None:
        super().__init__(name, default_value, aliases)
        if aliases is None:
            aliases = ["Entomology Innoculation Rate"]


class PrevalenceToEIRConverter(ParameterConverter):
    def __init__(
        self,
        fn: Callable,
        start: Union[list[Type[Parameter]], Type[Parameter]] = Prevalence(),
        to: Type[Parameter] = EIR(default_value=10),
    ) -> None:
        """

        :param fn:
        :param start:
        :param to:
        """
        if fn:
            self.fn = fn
        else:
            self.fn = self._converter
        super().__init__(start, to, fn)

    @staticmethod
    def _converter(prevalence):
        eir = 10 ** ((prevalence * 100 - 24.68) / 24.2)
        return eir


class EIRToPrevalenceConverter(ParameterConverter):
    """_summary_

    Args:
        ParameterConverter (_type_): _description_
    """

    def __init__(
        self,
        fn: Callable,
        start: Union[list[Type[Parameter]], Type[Parameter]] = EIR(),
        to: Type[Parameter] = Prevalence(0.5),
    ) -> None:
        if fn:
            self.fn = fn
        else:
            self.fn = self._converter
        super().__init__(start, to, fn)

    @staticmethod
    def _converter(eir):
        """_summary_

        Args:
            eir (_type_): _description_

        Returns:
            _type_: _description_
        """
        prevalence = (24.2 * log10(eir) + 24.68) / 100
        return prevalence


class ParameterList:
    """_summary_"""

    def __init__(self, parameters: list[Type[Parameter]]) -> None:
        self.parameters = parameters


class DemographyParameterList(ParameterList):
    """_summary_

    Args:
        ParameterList (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()


class EntomologyParameterList(ParameterList):
    """_summary_

    Args:
        ParameterList (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()


class InterventionParameterList(ParameterList):
    """_summary_

    Args:
        ParameterList (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()


class MonitoringParameterList(ParameterList):
    """_summary_

    Args:
        ParameterList (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()


class HealthSystemParameterList(ParameterList):
    """_summary_

    Args:
        ParameterList (_type_): _description_
    """

    def __init__(self) -> None:
        super().__init__()


class Model:
    """_summary_"""

    def __init__(
        self,
        _exec_path: str,
        name: str,
    ) -> None:
        """_summary_

        Args:
            _exec_path (str): _description_
            name (str): _description_
        """

    @property
    def exec_path(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._exec_path

    @exec_path.setter
    def exec_path(self, path_for_exec):
        """_summary_

        Args:
            path_for_exec (_type_): _description_
        """
        self._exec_path = path_for_exec


class Scenario:
    """_summary_"""

    def __init__(self) -> None:
        """_summary_"""


class PredefinedScenario:
    """_summary_"""

    def __init__(self) -> None:
        """_summary_"""


class District:
    """_summary_"""

    def __init__(self, iso: str, name: str = "", aliases: list[str] = []) -> None:
        """_summary_"""
        self.aliases = aliases
        self.iso = iso
        self.name = name
        self._uppercase()
        self._format()

    def _uppercase(self) -> None:
        self.iso = self.iso.upper()
        self.aliases = [alias.upper() for alias in self.aliases]

    def _format(self) -> None:
        self.name = self.name.replace("-", "_")
        self.aliases = [alias.replace("-", "_") for alias in self.aliases]
        self.aliases = [alias.replace(" ", "_") for alias in self.aliases]
        self.aliases = [alias.replace("  ", "_") for alias in self.aliases]
        self.aliases = [alias.replace("/", "_") for alias in self.aliases]


class Districts:
    def __init__(self, district_list: list[Type[District]]):
        self._list = district_list

    def add(self, district: Type[District]):
        self._list.append(district)

    @property
    def list(self):
        return [district.iso for district in self._list]

    def reformat(self, name: str) -> str:
        """
        from name
        :param name:
        :return:
        """
        formated_district = ""
        for district in self._list:
            if name in district.aliases:
                formated_district = district.iso
        return formated_district


class OldDistricts(Districts):
    """_summary_

    Args:
        Districts (_type_): _description_
    """

    def __init__(self, district_list: list[Type[District]]):
        """_summary_

        Args:
            district_list (list[Type[District]]): _description_
        """
        super().__init__(district_list)
        self.type = "old districts"


class DistrictsToDistricts:
    """_summary_

    Returns:
        _type_: _description_
    """

    def __init__(
        self, columns: list[str], data: Type[pd.DataFrame], districts: Type[Districts]
    ) -> None:
        """_summary_

        Args:
            columns (list[str]): _description_
            data (Type[pd.DataFrame]): _description_
        """
        self.columns = columns
        self.districts = districts
        self.data = data
        self._import_dataframe()

    def _import_dataframe(self):
        self.data = self.data.applymap(lambda x: self.districts.reformat(x))
        self.data.columns = self.columns


class OldDistrictToNewDistrict(DistrictsToDistricts):
    """_summary_

    Args:
        DistrictsToDistricts (_type_): _description_

    Returns:
        _type_: _description_
    """

    def __init__(
        self,
        data: Type[pd.DataFrame],
        districts: Type[Districts],
        columns: list[str] = ["old", "new"],
    ) -> None:
        """_summary_

        Args:
            data (Type[pd.DataFrame]): _description_
            districts (Type[Districts]): _description_
            columns (list[str], optional): _description_. Defaults to ['old', 'new'].
        """
        super().__init__(columns, data, districts)


class AdjacentDistricts(DistrictsToDistricts):
    """_summary_

    Args:
        DistrictsToDistricts (_type_): _description_

    Returns:
        _type_: _description_
    """

    def __init__(
        self,
        data: Type[pd.DataFrame],
        districts: Type[Districts],
        columns: list[str] = ["from", "to"],
    ) -> None:
        """_summary_

        Args:
            data (Type[pd.DataFrame]): _description_
            districts (Type[Districts]): _description_
            columns (list[str], optional): _description_. Defaults to ["from", "to"].
        """
        super().__init__(columns, data, districts)


class Country:
    """_summary_"""

    def __init__(
        self,
        districts: Type[Districts],
        adjacent_districts: Type[Districts],
        old_new_district_comparison_table: Type[OldDistrictToNewDistrict] = None,
    ) -> None:
        """_summary_

        Args:
            districts (Iterator[str]): _description_
            adjacent_districts (Iterator[str]): _description_
            old_districts (Iterator[str], optional): _description_. Defaults to None.
            new_old_district_comparison_table (Iterator[str], optional): _description_. Defaults to None.
        """

        self.districts = districts
        self.adjacent_districts = adjacent_districts
        self.new_old_district_comparison_table = old_new_district_comparison_table

    @staticmethod
    def _reformat_adm1_name(
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
        if isinstance(df, pd.DataFrame):
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
        elif isinstance(df, pd.Series):
            df = df.rename(new_column_name)
            # 2. reformat district name
            ## to upper case
            df.index = df.index.map(lambda x: x.upper())
            ## change space to _
            df.index = df.index.map(lambda x: x.replace(" ", "_"))
            ## change - to _
            df.index = df.index.map(lambda x: x.replace("-", "_"))

        return df


#
# gha = Country(
#     districts=[ahafo, ashanti, bono, bono_east, central, eastern, greater_accra, north_east, northern, oti, savannah,
#                upper_east, upper_west, volta, western, western_north],
#
#
# )


class Data:
    """_summary_"""

    def __init__(
        self, parameter: Type[Parameter], value: float | list | pd.DataFrame | pd.Series
    ) -> None:
        """_summary_"""
        self.parameter = parameter
        self.value = value


class CountryData(pd.DataFrame):
    """_summary_

    Args:
        pd (_type_): _description_
    """

    # properties
    _metadata = ["added_property"]

    def __init__(self, country: Type[Country], *args, **kw):
        super(CountryData, self).__init__(*args, **kw)
        self.country = country

    @property
    def _constructor(self):
        return CountryData
