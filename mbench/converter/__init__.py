from mbench import *
from mbench.parameter import Parameter
from typing import Union, List, Callable


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


class PrevalenceToEIRConverter(ParameterConverter):
    """_summary_

    Args:
        ParameterConverter (_type_): _description_
    """

    def __init__(
        self,
        start: Union[list[Type[Parameter]], Type[Parameter]] = Prevalence(),
        to: Type[Parameter] = EIR(default_value=10),
    ) -> None:
        """

        :param fn:
        :param start:
        :param to:
        """
        super().__init__(start, to)

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
