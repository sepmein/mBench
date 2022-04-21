"""_summary_

    Returns:
        _type_: _description_
"""
import math
from dataclasses import dataclass
from math import log10
from typing import Annotated, Any, Callable, Iterator, Optional, Union, Type
from pydantic import validate_arguments
from scipy.special import expit

import pandas as pd

import mbench.demographic
import mbench.intervention
import mbench.util


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
        aliases: list[str] = None,
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


class ParameterConverter:
    """Convert a parameter from one type to another."""

    def __init__(
        self,
        start: Union[Type[ParameterData], List[Type[ParameterData]]],
        to: Union[Type[ParameterData], List[Type[ParameterData]]],
    ) -> None:
        """Given a start parameter, a target parameter, and a function, create a converter.

        Args:
            start (Union[list[Type[Parameter]], Type[Parameter]]): The start parameter.
            to (Type[Parameter]): the target parameter.
            fn (Callable): the function to convert between the two parameters.
        """
        self.start = start
        self.to = to

    def convert_single(self) -> float:
        """convert a single parameter

        Returns:
            _type_: single value of the converted parameter
        """
        pass

    def convert(self) -> ParameterData:
        """Batch convert function using the convert_single function.

        Returns:
            _type_: converted parameter
        """
        pass


@dataclass
class ValueRange:
    """Value range for a parameter.

    Raises:
        ValueError: if the value is not in the range.
    """

    min: float = -math.inf
    max: float = math.inf

    def validate_value(self, x: float) -> None:
        """function to validate a value is in the range of the parameter. Raises ValueError if not.

        Args:
            x (float): value to validate.

        Raises:
            ValueError: error if value is not in range.
        """
        if not (self.min <= x <= self.max):
            raise ValueError(f"{x} must be in range [{self.min}, {self.max}]")


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


# create a converter class from MortalityBioassayParameter to EfficacyofHutTrailParameter
class MortalityBioassayToEfficacyofHutTrailConverter(ParameterConverter):
    """Converter from MortalityBioassayParameter to EfficacyofHutTrailParameter.

    Returns:
        _type_: none
    """

    def __init__(
        self,
        start: MortalityBioassayParameter,
        to: EfficacyofHutTrailParameter,
        verbose: bool = False,
    ) -> None:
        """Given a start parameter, a target parameter, and a function, create a converter.

        Args:
            start (MortalityBioassayParameter): The start parameter.
            to (EfficacyofHutTrailParameter): the target parameter.
        """
        super().__init__(start, to)
        self.verbose = verbose

    def convert(self):
        """
        Covert from the bioassay mortality to efficacy hut trail.
        """
        if self.verbose:
            rds_regular, rds_pbo, pyrethroid_outputs, pbo_outputs = self.start.data.map(
                self.convert_single
            )
        else:
            rds_regular, rds_pbo = self.start.data.map(self.convert_single)

        (
            repeating_regular,
            repeating_regular_with_decay,
            dying_regular,
            feeding_regular,
        ) = rds_regular
        repeating_pbo, repeating_pbo_with_decay, dying_pbo, feeding_pbo = rds_pbo

        repeating_regular_parameter = Parameter(
            "repeating_regular",
            description="Proportion of mosquitoes that repeat in the hut trail.",
        )
        repeating_regular_with_decay_parameter = Parameter(
            "repeating_regular_with_decay",
            description="Proportion of mosquitoes that repeat after decay in the hut trail",
        )
        dying_regular_parameter = Parameter("dying_regular")
        feeding_regular_parameter = Parameter("feeding_regular")
        repeating_pbo_parameter = Parameter("repeating_pbo")
        repeating_pbo_with_decay_parameter = Parameter("repeating_pbo_with_decay")
        dying_pbo_parameter = Parameter("dying_pbo")
        feeding_pbo_parameter = Parameter("feeding_pbo")

        repeating_regular_parameter_data = ParameterData(
            parameter=repeating_regular_parameter,
            country=self.start.country,
            data=repeating_regular,
        )
        repeating_regular_with_decay_parameter_data = ParameterData(
            parameter=repeating_regular_with_decay_parameter,
            country=self.start.country,
            data=repeating_regular_with_decay,
        )

        dying_regular_parameter_data = ParameterData(
            parameter=dying_regular_parameter,
            country=self.start.country,
            data=dying_regular,
        )
        feeding_regular_parameter_data = ParameterData(
            parameter=feeding_regular_parameter,
            country=self.start.country,
            data=feeding_regular,
        )
        repeating_pbo_parameter_data = ParameterData(
            parameter=repeating_pbo_parameter,
            country=self.start.country,
            data=repeating_pbo,
        )
        repeating_pbo_with_decay_parameter_data = ParameterData(
            parameter=repeating_pbo_with_decay_parameter,
            country=self.start.country,
            data=repeating_pbo_with_decay,
        )
        dying_pbo_parameter_data = ParameterData(
            parameter=dying_pbo_parameter, country=self.start.country, data=dying_pbo
        )
        feeding_pbo_parameter_data = ParameterData(
            parameter=feeding_pbo_parameter,
            country=self.start.country,
            data=feeding_pbo,
        )
        if self.verbose:
            return (
                repeating_regular_parameter_data,
                repeating_regular_with_decay_parameter_data,
                dying_regular_parameter_data,
                feeding_regular_parameter_data,
                repeating_pbo_parameter_data,
                repeating_pbo_with_decay_parameter_data,
                dying_pbo_parameter_data,
                feeding_pbo_parameter_data,
                pyrethroid_outputs,
                pbo_outputs,
            )
        else:
            return (
                repeating_regular_parameter_data,
                repeating_regular_with_decay_parameter_data,
                dying_regular_parameter_data,
                feeding_regular_parameter_data,
                repeating_pbo_parameter_data,
                repeating_pbo_with_decay_parameter_data,
                dying_pbo_parameter_data,
                feeding_pbo_parameter_data,
            )


class MortalityBioassayToEfficacyofHutTrailConverterElife2016(
    MortalityBioassayToEfficacyofHutTrailConverter
):
    def __init__(
        self,
        start: MortalityBioassayParameter,
        to: EfficacyofHutTrailParameter,
        verbose: bool = False,
        species: str = "gambiae",
    ) -> None:
        super().__init__(start, to)
        self.half_life_itn = 365 * 2.65
        self.species = ""
        self.verbose = verbose

        if species == "funestus":
            self.beta1 = 2.53
            self.beta2 = 0.89
            self.beta3 = 0.78
        else:
            self.beta1 = 3.41
            self.beta2 = 5.88
            self.beta3 = 0.78

        self.delta1 = 0.071
        self.delta2 = 1.26
        self.delta3 = 1.52

        # formula 1
        self.alpha1 = 0.63
        self.alpha2 = 4.0

        # equation 11
        self.theta1 = 0.02
        self.theta2 = 3.32

        # formula 4
        self.tao = 0.5

        # decay parameters
        self.mu_p = -2.36
        self.rho_p = -3.05

        # k_0
        self.k_0 = 0.699

        self.r_m = 0.24

    def mortality_bioassay_to_hut_trail(self, mortality_bioassay):
        """
        formula 2, from x to l
        :param mortality_bioassay:
        :return: mortality hut trail
        """
        return expit(self.alpha1 + self.alpha2 * (mortality_bioassay - self.tao))

    def mortality_pbo_bioassay(self, mortality_pyrethroid_bioassay):
        """
        formula 4, from x to f
        :param mortality_pyrethroid_bioassay:
        :return: mortality pbo bioassay
        """
        return expit(
            self.beta1
            + self.beta2
            * (mortality_pyrethroid_bioassay - self.tao)
            / (1 + self.beta3 * (mortality_pyrethroid_bioassay - self.tao))
        )

    def ratio_of_mosquitoes_entering_hut_to_without_net(self, mortality_hut_trail):
        """
        formula 8, from l to m_p
        :param mortality_hut_trail:
        :return:
        """
        return 1 - (
            self.delta1
            + self.delta2 * (mortality_hut_trail - self.tao)
            + self.delta3
            * (mortality_hut_trail - self.tao)
            * (mortality_hut_trail - self.tao)
        )

    def proportion_of_mosquitoes_successfully_feed_upon_entering(
        self, mortality_hut_trail
    ):
        """
        formula 11, from l to k_p
        :param mortality_hut_trail:
        :return:
        """
        return self.theta1 * math.exp(
            self.theta2 * (1 - mortality_hut_trail - self.tao)
        )

    @staticmethod
    def proportion_of_mosquitoes_exiting_without_feeding(p_mortality, p_feed):
        """
        j_p = 1 - l_p - k_p
        :param p_mortality:
        :param p_feed:
        :return:
        """
        return 1 - p_mortality - p_feed

    @staticmethod
    def proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(
        p_entering, p_enter_without_fed
    ):
        """
        j_p' = m_p * j_p + (1 - m_p)
        :param p_entering:
        :param p_enter_without_fed:
        :return:
        """
        return p_entering * p_enter_without_fed + (1 - p_entering)

    @staticmethod
    def proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(
        p_entering, p_feed
    ):
        """
        k_p' = m_p * k_p
        :param p_entering:
        :param p_feed:
        :return:
        """
        return p_entering * p_feed

    @staticmethod
    def proportion_of_mosquitoes_dead_accounting_deterrence(p_entering, p_death):
        """
        l_p' = m_p * l_p
        :param p_entering:
        :param p_death:
        :return:
        """
        return p_entering * p_death

    def repeating(self, k_p_d, j_p_d, l_p_d):
        """
        formula 12, calculating r_p_0
        :param k_p_d:
        :param j_p_d:
        :param l_p_d:
        :return:
        """
        return (1 - k_p_d / self.k_0) * (j_p_d / (j_p_d + l_p_d))

    def dying(self, k_p_d, j_p_d, l_p_d):
        """
        formula 13, calculating d_p_0
        :param k_p_d:
        :param j_p_d:
        :param l_p_d:
        :return:
        """
        return (1 - k_p_d / self.k_0) * (l_p_d / (j_p_d + l_p_d))

    def feeding(self, k_p_d):
        """
        formula 14, calculating s_p_0
        :param k_p_d:
        :return:
        """
        return k_p_d / self.k_0

    def gamma_p(self, mortality_hut_trail):
        """
        formula 16, calculating gamma_p, the decay parameter
        :param mortality_hut_trail:
        :return:
        """
        return expit(self.mu_p + self.rho_p * (mortality_hut_trail - self.tao))

    def r_p(self, r_p_0, gamma_p_):
        """
        formula 17, calculate r_p
        :param r_p_0:
        :param gamma_p_:
        :return:
        """
        # suppose life years of itn is 3 year, remind to change this if using other parameters
        return (r_p_0 - self.r_m) * math.exp(
            -1 * gamma_p_ * self.half_life_itn
        ) + self.r_m

    def mortality_pyrethroid_to_mortality_hut(self, mortality_pyrethroid_bioassay):
        # from pyrethroid mortality in bioassay compute mortality in pyrethroid hut trail using eq 4
        mortality_pyrethroid_hut_trail = self.mortality_bioassay_to_hut_trail(
            mortality_pyrethroid_bioassay
        )

        # from pyrethroid mortality in bioassay compute mortality in pbo bioassay
        mortality_pbo_bioassay = self.mortality_pbo_bioassay(
            mortality_pyrethroid_bioassay
        )
        # from mortality in pbo bioassay to mortality in pbo hut trail
        mortality_pbo_hut_trail = self.mortality_bioassay_to_hut_trail(
            mortality_pbo_bioassay
        )

        return (
            mortality_pyrethroid_hut_trail,
            mortality_pbo_bioassay,
            mortality_pbo_hut_trail,
        )

    def convert_single(self, mortality_pyrethroid_bioassay):
        """
        from mortality_pyrethroid_bioassay calculate efficacy results for bednets and PBO nets
        :param mortality_pyrethroid_bioassay:
        :return:
        """
        # proportion mosquitoes dying in a discriminating dose pyrethroid bioassay
        # mortality_pyrethroid_bioassay

        (
            mortality_pyrethroid_hut_trail,
            mortality_pbo_bioassay,
            mortality_pbo_hut_trail,
        ) = self.mortality_pyrethroid_to_mortality_hut(mortality_pyrethroid_bioassay)

        # m_p
        # from mortality to number of mosquitoes entering hut
        p_entering_regular = self.ratio_of_mosquitoes_entering_hut_to_without_net(
            mortality_pyrethroid_hut_trail
        )
        p_entering_pbo = self.ratio_of_mosquitoes_entering_hut_to_without_net(
            mortality_pbo_hut_trail
        )

        # k_p
        p_feed_regular = self.proportion_of_mosquitoes_successfully_feed_upon_entering(
            mortality_pyrethroid_hut_trail
        )
        p_feed_pbo = self.proportion_of_mosquitoes_successfully_feed_upon_entering(
            mortality_pbo_hut_trail
        )

        # j_p
        p_exiting_regular = self.proportion_of_mosquitoes_exiting_without_feeding(
            mortality_pyrethroid_hut_trail, p_feed_regular
        )
        p_exiting_pbo = self.proportion_of_mosquitoes_exiting_without_feeding(
            mortality_pbo_hut_trail, p_feed_pbo
        )

        # j_p'
        p_exit_with_deterrence_regular = self.proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(
            p_entering_regular, p_exiting_regular
        )
        p_exit_with_deterrence_pbo = self.proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(
            p_entering_pbo, p_exiting_pbo
        )

        # k_p'
        p_feed_with_deterrence_regular = self.proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(
            p_entering_regular, p_feed_regular
        )
        p_feed_with_deterrence_pbo = self.proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(
            p_entering_pbo, p_feed_pbo
        )

        # l_p'
        mortality_pyrethroid_hut_trail_with_deterrence = (
            self.proportion_of_mosquitoes_dead_accounting_deterrence(
                p_entering_regular, mortality_pyrethroid_hut_trail
            )
        )

        mortality_pbo_hut_trail_with_deterrence = (
            self.proportion_of_mosquitoes_dead_accounting_deterrence(
                p_entering_pbo, mortality_pbo_hut_trail
            )
        )

        # r_p_0
        repeating_regular = self.repeating(
            k_p_d=p_feed_with_deterrence_regular,
            j_p_d=p_exit_with_deterrence_regular,
            l_p_d=mortality_pyrethroid_hut_trail_with_deterrence,
        )
        repeating_pbo = self.repeating(
            k_p_d=p_feed_with_deterrence_pbo,
            j_p_d=p_exit_with_deterrence_pbo,
            l_p_d=mortality_pbo_hut_trail_with_deterrence,
        )

        # d_p_0
        dying_regular = self.dying(
            k_p_d=p_feed_with_deterrence_regular,
            j_p_d=p_exit_with_deterrence_regular,
            l_p_d=mortality_pyrethroid_hut_trail_with_deterrence,
        )
        dying_pbo = self.dying(
            k_p_d=p_feed_with_deterrence_pbo,
            j_p_d=p_exit_with_deterrence_pbo,
            l_p_d=mortality_pbo_hut_trail_with_deterrence,
        )

        # s_p_0
        feeding_regular = self.feeding(k_p_d=p_feed_with_deterrence_regular)
        feeding_pbo = self.feeding(k_p_d=p_feed_with_deterrence_pbo)

        # decay rate
        # decay parameter rho_p
        gamma_p_regular = self.gamma_p(mortality_pyrethroid_hut_trail)
        gamma_p_pbo = self.gamma_p(mortality_pbo_hut_trail)

        # r_p repeat rate with decay
        repeating_regular_with_decay = self.r_p(repeating_regular, gamma_p_regular)
        repeating_pbo_with_decay = self.r_p(repeating_pbo, gamma_p_pbo)

        rds_regular = (
            repeating_regular,
            repeating_regular_with_decay,
            dying_regular,
            feeding_regular,
        )
        pyrethroid_outputs = (
            mortality_pyrethroid_bioassay,
            mortality_pyrethroid_hut_trail,
            p_entering_regular,
            p_feed_regular,
            p_exiting_regular,
            p_exit_with_deterrence_regular,
            p_feed_with_deterrence_regular,
            mortality_pyrethroid_hut_trail_with_deterrence,
        )
        rds_pbo = (repeating_pbo, repeating_pbo_with_decay, dying_pbo, feeding_pbo)
        pbo_outputs = (
            mortality_pbo_bioassay,
            mortality_pbo_hut_trail,
            p_entering_pbo,
            p_feed_pbo,
            p_exiting_pbo,
            p_exit_with_deterrence_pbo,
            p_feed_with_deterrence_pbo,
            mortality_pbo_hut_trail_with_deterrence,
        )
        if self.verbose:
            return rds_regular, rds_pbo, pyrethroid_outputs, pbo_outputs
        else:
            return rds_regular, rds_pbo


class MortalityBioassayToEfficacyofHutTrailConverterEllie2022(
    MortalityBioassayToEfficacyofHutTrailConverterElife2016
):
    def __init__(
        self,
        start: MortalityBioassayParameter,
        to: EfficacyofHutTrailParameter,
        verbose: bool = False,
    ) -> None:
        super().__init__(start, to, verbose)
        self.alpha1 = 0.89
        self.alpha2 = 0.47

        # equation s1.2
        self.beta1 = -1.43
        self.beta2 = 5.60

        # for calculation ratio of mosquito entering hut with / without a hut
        self.delta1 = 0.36
        self.delta2 = 0.49
        self.delta3 = 2.57

        # calculating decay
        self.mu_p = -2.43
        self.rho_p = -3.01

        # feeding
        self.theta1 = 0.04
        self.theta2 = 4.66

    def mortality_bioassay_to_hut_trail(self, mortality_bioassay):
        """
        mortality from bioassay to hut trail
        :param mortality_bioassay:
        :return: mortality hut trail
        """
        power = -1.0 * self.alpha2
        return 1 - 1 / (1 + ((1 - mortality_bioassay) / self.alpha1) ** power)

    def mortality_hut_trail_from_pyrethroid_to_pbo(
        self, mortality_pyrethroid_hut_trail
    ):
        """
        from l1 to l2
        :param mortality_pyrethroid_hut_trail:
        :return: mortality PBO hut trail
        """
        return 1 / (
            1
            + math.exp(-1 * (self.beta1 + self.beta2 * mortality_pyrethroid_hut_trail))
        )

    def ratio_of_mosquitoes_entering_hut_to_without_net(self, mortality_hut_trail):
        return self.delta1 * math.exp(
            self.delta2
            * (1 - math.exp((1 - mortality_hut_trail) * self.delta3))
            / self.delta3
        )

    def proportion_of_mosquitoes_successfully_feed_upon_entering(
        self, mortality_hut_trail
    ):
        return 1 - math.exp(
            self.theta1
            * (1 - math.exp(self.theta2 * (1 - mortality_hut_trail)))
            / self.theta2
        )

    def mortality_pyrethroid_to_mortality_hut(self, mortality_pyrethroid_bioassay):
        mortality_pyrethroid_hut_trail = self.mortality_bioassay_to_hut_trail(
            mortality_pyrethroid_bioassay
        )
        mortality_pbo_bioassay = None
        mortality_pbo_hut_trail = self.mortality_hut_trail_from_pyrethroid_to_pbo(
            mortality_pyrethroid_hut_trail
        )
        return (
            mortality_pyrethroid_hut_trail,
            mortality_pbo_bioassay,
            mortality_pbo_hut_trail,
        )

    def convert_single(self, mortality_pyrethroid_bioassay):
        """
        from mortality_pyrethroid_bioassay calculate efficacy results for bednets and PBO nets
        :param mortality_pyrethroid_bioassay:
        :return:
        """
        # proportion mosquitoes dying in a discriminating dose pyrethroid bioassay
        # mortality_pyrethroid_bioassay

        (
            mortality_pyrethroid_hut_trail,
            mortality_pbo_bioassay,
            mortality_pbo_hut_trail,
        ) = self.mortality_pyrethroid_to_mortality_hut(mortality_pyrethroid_bioassay)

        # m_p
        # from mortality to number of mosquitoes entering hut
        p_entering_regular = self.ratio_of_mosquitoes_entering_hut_to_without_net(
            mortality_pyrethroid_hut_trail
        )
        p_entering_pbo = self.ratio_of_mosquitoes_entering_hut_to_without_net(
            mortality_pbo_hut_trail
        )

        # k_p
        p_feed_regular = self.proportion_of_mosquitoes_successfully_feed_upon_entering(
            mortality_pyrethroid_hut_trail
        )
        p_feed_pbo = self.proportion_of_mosquitoes_successfully_feed_upon_entering(
            mortality_pbo_hut_trail
        )

        # j_p
        p_exiting_regular = self.proportion_of_mosquitoes_exiting_without_feeding(
            mortality_pyrethroid_hut_trail, p_feed_regular
        )
        p_exiting_pbo = self.proportion_of_mosquitoes_exiting_without_feeding(
            mortality_pbo_hut_trail, p_feed_pbo
        )

        # j_p'
        p_exit_with_deterrence_regular = self.proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(
            p_entering_regular, p_exiting_regular
        )
        p_exit_with_deterrence_pbo = self.proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(
            p_entering_pbo, p_exiting_pbo
        )

        # k_p'
        p_feed_with_deterrence_regular = self.proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(
            p_entering_regular, p_feed_regular
        )
        p_feed_with_deterrence_pbo = self.proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(
            p_entering_pbo, p_feed_pbo
        )

        # l_p'
        mortality_pyrethroid_hut_trail_with_deterrence = (
            self.proportion_of_mosquitoes_dead_accounting_deterrence(
                p_entering_regular, mortality_pyrethroid_hut_trail
            )
        )

        mortality_pbo_hut_trail_with_deterrence = (
            self.proportion_of_mosquitoes_dead_accounting_deterrence(
                p_entering_pbo, mortality_pbo_hut_trail
            )
        )

        # r_p_0
        repeating_regular = self.repeating(
            k_p_d=p_feed_with_deterrence_regular,
            j_p_d=p_exit_with_deterrence_regular,
            l_p_d=mortality_pyrethroid_hut_trail_with_deterrence,
        )
        repeating_pbo = self.repeating(
            k_p_d=p_feed_with_deterrence_pbo,
            j_p_d=p_exit_with_deterrence_pbo,
            l_p_d=mortality_pbo_hut_trail_with_deterrence,
        )

        # d_p_0
        dying_regular = self.dying(
            k_p_d=p_feed_with_deterrence_regular,
            j_p_d=p_exit_with_deterrence_regular,
            l_p_d=mortality_pyrethroid_hut_trail_with_deterrence,
        )
        dying_pbo = self.dying(
            k_p_d=p_feed_with_deterrence_pbo,
            j_p_d=p_exit_with_deterrence_pbo,
            l_p_d=mortality_pbo_hut_trail_with_deterrence,
        )

        # s_p_0
        feeding_regular = self.feeding(k_p_d=p_feed_with_deterrence_regular)
        feeding_pbo = self.feeding(k_p_d=p_feed_with_deterrence_pbo)

        # decay rate
        # decay parameter rho_p
        gamma_p_regular = self.gamma_p(mortality_pyrethroid_hut_trail)
        gamma_p_pbo = self.gamma_p(mortality_pbo_hut_trail)

        # r_p repeat rate with decay
        repeating_regular_with_decay = self.r_p(repeating_regular, gamma_p_regular)
        repeating_pbo_with_decay = self.r_p(repeating_pbo, gamma_p_pbo)

        rds_regular = (
            repeating_regular,
            repeating_regular_with_decay,
            dying_regular,
            feeding_regular,
        )
        pyrethroid_outputs = (
            mortality_pyrethroid_bioassay,
            mortality_pyrethroid_hut_trail,
            p_entering_regular,
            p_feed_regular,
            p_exiting_regular,
            p_exit_with_deterrence_regular,
            p_feed_with_deterrence_regular,
            mortality_pyrethroid_hut_trail_with_deterrence,
        )
        rds_pbo = (repeating_pbo, repeating_pbo_with_decay, dying_pbo, feeding_pbo)
        pbo_outputs = (
            mortality_pbo_bioassay,
            mortality_pbo_hut_trail,
            p_entering_pbo,
            p_feed_pbo,
            p_exiting_pbo,
            p_exit_with_deterrence_pbo,
            p_feed_with_deterrence_pbo,
            mortality_pbo_hut_trail_with_deterrence,
        )
        if self.verbose:
            return rds_regular, rds_pbo, pyrethroid_outputs, pbo_outputs
        else:
            return rds_regular, rds_pbo


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
    ) -> None:
        super().__init__(name, default_value, aliases, description)


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
    ) -> str | list[str] | Type[pd.Index] | Type[pd.Series]:
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
        elif isinstance(to_format, (pd.Series, pd.Index)):
            formated = to_format.map(reformat_in_districts)
        return formated

    def match_iso(
        self, to_match: str | list[str] | Type[pd.Series] | Type[pd.Index]
    ) -> str | list[str] | Type[pd.Series] | Type[pd.Index]:
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
        elif isinstance(to_match, (pd.Series, pd.Index)):
            return to_match.map(match_in_districts)
        else:
            raise Exception(
                "Districts: Match ISO failed, to match value should be one of str, list of str, pd.Series or pd.Index"
            )


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
        results = super().map(to_map=to_map, left_on=left_on)
        results.rename(columns={"new": "district"}, inplace=True)
        results = results.set_index(results["district"])
        results = results.iloc[:, -1]
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

    def reformat(self, to_format):
        return self._districts.reformat(to_format)

    def match_iso(self, to_match):
        return self._districts.match_iso(to_match)


class ParameterData:
    """Data class for parameter data"""

    def __init__(
        self,
        parameter: Type[Parameter],
        country: Type[Country],
        data: Type[pd.Series],
        from_old_districts_system: bool = False,
        interpolate_from_neighbour: bool = False,
    ) -> None:
        """Given a parameter, country, and data, this class will create a ParameterData object.
        If the data is from old districts system, the data will be converted to new districts system.
        If the data is missing, the data will be interpolated from the neighbour districts.

        Args:
            parameter (Type[Parameter]): Parameter object
            country (Type[Country]): country object
            data (Type[pd.Series]):  data object
            from_old_districts_system (bool, optional): is from old district system or not. Defaults to False.
            interpolate_from_neighbour (bool, optional): whether the data is missing and should be interpolate from neighbour. Defaults to False.

        Raises:
            Exception:  if the data is not the panda Series type
        """

        self.country = country
        self.parameter = parameter
        self.from_old_districts_system = from_old_districts_system
        self.interpolate_from_neighbour = interpolate_from_neighbour
        # data type should be pd.Series
        if not isinstance(data, pd.Series):
            raise Exception("Data type should be pd.Series")

        # if from old district
        if from_old_districts_system:
            self.data = pd.Series(
                data=country.old_districts_to_new_districts.map(to_map=data)
            )

        elif interpolate_from_neighbour:
            pass

        else:
            # format and match_iso:self index using country.districts.format
            self.data = pd.Series(data)
            self.data.index = country.reformat(self.data.index)
            self.data.index = country.match_iso(self.data.index)

    @property
    def name(self) -> str:
        """Name for Parameter data, a convinient function for retrieve name

        Returns:
            str: the name of the parameter
        """
        return self.parameter.name


class CountryData:
    """_summary_

    Args:
        pd (_type_): _description_
    """

    def __init__(self, country: Type[Country]):
        self.data = pd.DataFrame()
        self.data.index = country.districts
        self.country = country

    def add_parameter(
        self,
        parameter_data: Type[ParameterData],
    ) -> None:
        """_summary_

        Args:
            parameter (_type_): _description_

        Returns:
            _type_: _description_
        """
        self.data[parameter_data.name] = parameter_data.data.values
