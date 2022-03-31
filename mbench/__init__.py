"""_summary_

    Returns:
        _type_: _description_
"""
import math
from dataclasses import dataclass
from math import log10
from typing import Annotated, Any, Callable, Iterator, Optional, Union, Type

import pandas as pd

import mbench.demographic
import mbench.intervention
import mbench.util


class Parameter:
    """_summary_"""

    _value: Any = None

    def __init__(
        self, name: str, default_value: Any = None, aliases: list[str] = None
    ) -> None:
        self._name = name
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

    @property
    def name(self) -> str:
        """Get parameter name

        Returns:
            str: name of the parameter
        """
        return self._name


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
    """_summary_

    Raises:
        ValueError: _description_
    """

    min: float = -math.inf
    max: float = math.inf

    def validate_value(self, x):
        if not (self.min <= x <= self.max):
            raise ValueError(f"{x} must be in range [{self.min}, {self.max}]")


class Prevalence(Parameter):
    """_summary_

    Args:
        Parameter (_type_): _description_
    """

    def __init__(
        self,
        default_value: Annotated[float, ValueRange(0.0, 1.0)] = None,
        name: str = "Prevalence",
        aliases: list[str] = None,
    ) -> None:
        """_summary_

        Args:
            default_value (Annotated[float, ValueRange, optional): _description_. Defaults to None.
            name (str, optional): _description_. Defaults to "Prevalence".
            aliases (list[str], optional): _description_. Defaults to None.
        """
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
    """_summary_

    Args:
        ParameterConverter (_type_): _description_
    """

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
        """Create a district of a country

        Args:
            iso (str): iso name of the district
            name (str, optional): name of the District. Defaults to "".
            aliases (list[str], optional): aliases name of the district. Defaults to [].
        """
        self.aliases = aliases
        self.iso = self.format(iso)
        self.name = self.format(name)

    def format(self, string: str) -> str:
        """
        Format string to uppercase, and replace connection symbols to '_'

        Args:
            string (str): string to be formatted

        Returns:
            str: formatted string
        """
        string = string.replace("-", "_")
        string = string.replace(" ", "_")
        string = string.replace("  ", "_")
        string = string.replace("/", "_")
        string = string.upper()
        return string

    def search(self, search_string: str) -> str | bool:
        """
        Search a given string, this function will reformat the search string and the aliases of District first and match,
        if found in this District, return the iso name of it

        Args:
            search_string (str): search string, case insensitive

        Returns:
            str | bool: Iso string if found, and False if not found
        """
        # upper case and format search string
        search_string = self.format(search_string)

        # reformat aliases
        aliases = [self.format(alias) for alias in self.aliases]
        # if found return iso string
        if search_string in aliases:
            return self.iso
        else:
            return False


class Districts:
    """_summary_"""

    def __init__(self, district_list: list[Type[District]]) -> None:
        self._list = district_list

    def add(self, district: Type[District]) -> None:
        self._list.append(district)

    @property
    def l(self) -> list[str]:
        return [district.iso for district in self._list]

    @property
    def n(self) -> int:
        return len(self._list)

    def reformat(
        self, to_format: str | list[str] | Type[pd.Series] | Type[pd.Index]
    ) -> str | Type[pd.Series]:
        """
        from name
        :param name:
        :return:
        """

        formated = to_format

        def reformat_in_districts(name):
            formated_district = name
            for district in self._list:
                formated_district = district.format(string=name)
            return formated_district

        if isinstance(to_format, str):
            formated = reformat_in_districts(to_format)
            # if
        elif isinstance(to_format, list):
            formated = [reformat_in_districts(n) for n in to_format]
        elif isinstance(to_format, pd.Series):
            formated = to_format.map(reformat_in_districts)
        elif isinstance(to_format, pd.Index):
            formated = to_format.map(reformat_in_districts)
        return formated

    def match_iso(
        self, to_match: str | list[str] | Type[pd.Series]
    ) -> str | list[str] | Type[pd.Series]:
        """match iso district name for to match string or list

        Args:
            to_match (str | list[str]): _description_

        Raises:
            Exception: _description_

        Returns:
            str | list[str]: _description_
        """

        def match_in_districts(_to_match: str) -> str:
            result = _to_match
            for district in self._list:
                search_result = district.search(search_string=_to_match)
                if search_result is not False:
                    result = search_result
            return result

        if isinstance(to_match, str):
            return match_in_districts(to_match)
        elif isinstance(to_match, list):
            return [match_in_districts(t) for t in to_match]
        elif isinstance(to_match, pd.Series):
            return to_match.apply(match_in_districts)


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
        self,
        columns: list[str],
        start: Type[pd.Series],
        to: Type[pd.Series],
        districts: Type[Districts],
    ) -> None:
        """_summary_

        Args:
            columns (list[str]): _description_
            data (Type[pd.DataFrame]): _description_
        """
        self.columns = columns
        self.start_column = columns[0]
        self.to_column = columns[1]
        self.districts = districts
        self.data = pd.concat([start, to], axis=1)
        self.data.columns = self.columns

    def map(
        self, to_map: Type[pd.DataFrame | pd.Series], left_on: str = None
    ) -> Type[pd.DataFrame]:
        """This function was created to map from A dataframe to B dataframe with common column
        For example:
        to_map:
        {
            '_a': 1,
            '_b': 2
        }

        self.data
        {
            'a': '_a',
            'b': '_b'
        }


        Args:
            to_map (Type[pd.DataFrame  |  pd.Series]): _description_
            left_on (str, optional): _description_. Defaults to None.

        Returns:
            Type[pd.DataFrame]: _description_
        """
        if left_on is None:
            left_on = self.start_column

        # reformat to map index
        to_map.index = self.districts.reformat(to_format=to_map.index)
        result = self.data.merge(
            right=to_map, how="left", left_on=left_on, right_index=True
        )
        return result


class OldDistrictToNewDistrict(DistrictsToDistricts):
    """_summary_

    Args:
        DistrictsToDistricts (_type_): _description_

    Returns:
        _type_: _description_
    """

    def __init__(
        self,
        start: Type[pd.Series],
        to: Type[pd.Series],
        districts: Type[Districts],
        columns: list[str] = None,
    ) -> None:
        """mapping from old district to new district

        Args:
            columns (list[str]): _description_
            start (Type[pd.Series]): _description_
            to (Type[pd.Series]): _description_
            districts (Type[Districts]): _description_
        """
        if columns is None:
            columns = ["old", "new"]
        start = districts.reformat(to_format=start)
        to = districts.match_iso(to_match=to)
        super().__init__(columns, start, to, districts)
    
    def map(
        self, to_map: Type[pd.DataFrame | pd.Series], left_on: str = None
    ) -> Type[pd.DataFrame]:
        """This function was created to map from A dataframe to B dataframe with common column
        For example:
        to_map:
        {
            '_a': 1,
            '_b': 2
        }

        self.data
        {
            'a': '_a',
            'b': '_b'
        }


        Args:
            to_map (Type[pd.DataFrame  |  pd.Series]): _description_
            left_on (str, optional): _description_. Defaults to None.

        Returns:
            Type[pd.DataFrame]: _description_
        """
        results  = super().map(to_map=to_map, left_on=left_on)
        results.rename(columns = {'new': 'district'}, inplace=True)
        results = results.set_index(results['district'])
        results = results.iloc[: , -1]
        return results


class AdjacentDistricts(DistrictsToDistricts):
    """_summary_

    Args:
        DistrictsToDistricts (_type_): _description_

    Returns:
        _type_: _description_
    """

    def __init__(
        self,
        start: Type[pd.Series],
        to: Type[pd.Series],
        districts: Type[Districts],
        columns: list[str] = None,
    ) -> None:
        if columns is None:
            columns = ["start", "to"]
        super().__init__(columns, start, to, districts)


class Country:
    """_summary_"""

    def __init__(
        self,
        districts: Type[Districts],
        adjacent_districts: Type[Districts] = None,
        old_districts_to_new_districts: Type[OldDistrictToNewDistrict] = None,
    ) -> None:
        """_summary_

        Args:
            districts (Iterator[str]): _description_
            adjacent_districts (Iterator[str]): _description_
            old_districts (Iterator[str], optional): _description_. Defaults to None.
            new_old_district_comparison_table (Iterator[str], optional): _description_. Defaults to None.
        """

        self._districts = districts
        self.n_districts = districts.n
        self.adjacent_districts = adjacent_districts
        self.old_districts_to_new_districts = old_districts_to_new_districts

    @staticmethod
    def _reformat_adm1_name(
        df: Type[pd.DataFrame],
        original_column_name: str = "adm1",
        new_column_name: str = "adm1",
        set_index: bool = True,
    ) -> Type[pd.DataFrame]:
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

    @property
    def districts(self):
        return self._districts.l


class ParameterData:
    """_summary_"""

    def __init__(
        self,
        parameter: Type[Parameter],
        value: float | list | pd.DataFrame | pd.Series,
        country: Type[Country],
        from_old_districts_system: bool = False,
        interpolate_from_neighbour: bool = False,
    ) -> None:
        self.parameter = parameter
        self._value = value
        self.country = country

        if isinstance(value, (list, pd.DataFrame, pd.Series)):
            if from_old_districts_system:
                mapped_value = self.country.old_districts_to_new_districts.map(
                    to_map=value
                )
                self._value = mapped_value
                self._value.name = self.parameter.name
            if interpolate_from_neighbour:
                # TODO: add code for interpolation
                pass
            if len(self._value) != self.country.n_districts:
                raise Exception(
                    "Add Parameter error. Number of new parameter value differs from the number of districts"
                )

    @property
    def name(self) -> str:
        """Name for Parameter data, a convinient function for retrieve name

        Returns:
            str: the name of the parameter
        """
        return self.parameter.name

    @property
    def value(self) -> float | list | pd.DataFrame | pd.Series:
        return self.value


class CountryData(pd.DataFrame):
    """_summary_

    Args:
        pd (_type_): _description_
    """

    # properties
    _metadata = ["CountryData"]

    def __init__(self, country: Type[Country], *args, **kw):
        super().__init__(*args, **kw)
        self.country = country
        self.index = country.districts

    @property
    def _constructor(self):
        return CountryData

    @property
    def _constructor_sliced(self):
        return CountryDataColumn

    def add_parameter(
        self,
        parameter_data: Type[ParameterData],
    ):
        """_summary_

        Args:
            parameter (_type_): _description_

        Returns:
            _type_: _description_
        """

        self[parameter_data.name] = parameter_data.value
