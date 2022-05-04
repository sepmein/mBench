from tkinter import W
from typing import Any, List, Optional, Union, Annotated
from mbench import ValueRange


class Parameter:
    """Base class for all parameters.

    Returns:
        _type_: none
    """

    _value: Any = None

    def __init__(
        self,
        name: str,
        default_value: Any = None,
        aliases: List[str] = None,
        description: str = None,
    ) -> None:
        """Geven a name, a default value, and a list of aliases, create a parameter.

        Args:
            name (str): The name of the parameter.
            default_value (Any, optional): Default value of the parameter. Defaults to None.
            aliases (list[str], optional): Aliases of the parameter. Defaults to None.
            description (str, optional): Description of the parameter. Defaults to None.
        """
        self._name = name
        self.default_value = default_value
        self.aliases = aliases
        self.description = description

    @property
    def value(self):
        """getter for value

        Returns:
            _type_: parameter value
        """
        return self._value

    @value.setter
    def value(self, value):
        """setter for value

        Args:
            value (_type_): value to set
        """
        self._value = value

    @property
    def name(self) -> str:
        """Get parameter name

        Returns:
            str: name of the parameter
        """
        return self._name


# create a MortalityBioassayParameter and inherit from Parameter
class MortalityBioassayParameter(Parameter):
    """Parameter for a mortality bioassay.

    Returns:
        _type_: none
    """

    _value: Optional[float] = None

    def __init__(
        self,
        name: str,
        default_value: Optional[float] = None,
        aliases: Optional[list[str]] = None,
        description: Optional[str] = None,
    ) -> None:
        """Geven a name, a default value, and a list of aliases, create a parameter.

        Args:
            name (str): The name of the parameter.
            default_value (Optional[float], optional): Default value of the parameter. Defaults to None.
            aliases (Optional[list[str]], optional): Aliases of the parameter. Defaults to None.
            description (Optional[str], optional): Description of the parameter. Defaults to None.
        """
        super().__init__(name, default_value, aliases, description)

    @property
    def value(self):
        """getter for value

        Returns:
            _type_: parameter value
        """
        return self._value

    @value.setter
    def value(self, value):
        """setter for value

        Args:
            value (_type_): value to set
        """
        self._value = value


# create a EfficacyofHutTrailParameter and inherit from Parameter
class EfficacyofHutTrailParameter(Parameter):
    """Parameter for an efficacy of hut trail.

    Returns:
        _type_: none
    """

    _value: Optional[float] = None

    def __init__(
        self,
        name: str,
        default_value: Optional[float] = None,
        aliases: Optional[list[str]] = None,
        description: Optional[str] = None,
    ) -> None:
        """Geven a name, a default value, and a list of aliases, create a parameter.

        Args:
            name (str): The name of the parameter.
            default_value (Optional[float], optional): Default value of the parameter. Defaults to None.
            aliases (Optional[list[str]], optional): Aliases of the parameter. Defaults to None.
            description (Optional[str], optional): Description of the parameter. Defaults to None.
        """
        super().__init__(name, default_value, aliases, description)

    @property
    def value(self):
        """getter for value

        Returns:
            _type_: parameter value
        """
        return self._value

    @value.setter
    def value(self, value):
        """setter for value

        Args:
            value (_type_): value to set
        """
        self._value = value


class Prevalence(Parameter):
    """Prevalence of the disease.
    Defaults to 0.0.
    Must be between 0.0 and 1.0.
    Example: 0.1
    Type: float
    Inherited from: Parameter

    Args:
        Parameter (_type_): the parameter to inherit from.
    """

    def __init__(
        self,
        default_value: Annotated[float, ValueRange(0.0, 1.0)] = None,
        name: str = "Prevalence",
        aliases: list[str] = None,
    ) -> None:
        """The prevalence of the disease. Defaults to 0.0. Must be between 0.0 and 1.0.

        Args:
            default_value (Annotated[float, ValueRange, optional): _description_. Defaults to None.
            name (str, optional): _description_. Defaults to "Prevalence".
            aliases (list[str], optional): _description_. Defaults to None.
        """
        super().__init__(name, default_value, aliases)


class EIR(Parameter):
    """Entomology Innoculation Rate. Defaults to 0.0. Must be greater than or equal to 0.0.

    Args:
        Parameter (_type_): existing parameter to inherit from.
    """

    def __init__(
        self,
        default_value: Annotated[float, ValueRange(0.0)] = None,
        name: str = "EIR",
        aliases=["Entomology Innoculation Rate", "EIR"],
    ) -> None:
        """Given a name, a default value, and a list of aliases, create a parameter.

        Args:
            default_value (Annotated[float, ValueRange, optional): Default value of EIR. Defaults to None.
            name (str, optional): Defaults to "EIR".
            aliases (_type_, optional): Defaults to None.
        """
        super().__init__(name, default_value, aliases)
        if aliases is None:
            aliases = ["Entomology Innoculation Rate"]


class ItnCoverage(Parameter):
    """Insecticide treated net coverage. Defaults to 0.0. Must be between 0.0 and 1.0.

    Args:
        Parameter (_type_): _description_
    """

    def __init__(
        self,
        name: str = "Itn Coverage",
        default_value: Any = None,
        aliases: list[str] = None,
        description: str = "Insecticide treated net coverage. Defaults to 0.0. Must be between 0.0 and 1.0.",
    ) -> None:
        super().__init__(name, default_value, aliases, description)
