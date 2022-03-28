import mbench.demographic
import mbench.intervention
import mbench.util
from typing import Any


class Mbench:
    """
    Mbench the central class for running malaria modelling benchmarking
    """

    def __init__(self) -> None:
        pass

    def preprocess(self):
        pass

    def set_scenario(self):
        pass

    def run_benchmarking(self):
        pass


class Parameter:
    def __init__(
        self,
        name: str,
        default_value: Any,
        aliases: list = [],
    ) -> None:
        self.name = name
        self._value = default_value
        self.aliases = aliases

class Parameter_list:
    def __init__(self) -> None:
        pass

class Demography_Parameter_List(Parameter_list):
    def __init__(self) -> None:
        super().__init__()

class Entomology_Parameter_List(Parameter_list):
    def __init__(self) -> None:
        super().__init__()
class Intervention_Parameter_List(Parameter_list):
    def __init__(self) -> None:
        super().__init__()
class Monitoring_Parameter_List(Parameter_list):
    def __init__(self) -> None:
        super().__init__()
class HealthSystem_Parameter_List(Parameter_list):
    def __init__(self) -> None:
        super().__init__()
class Model:
    def __init__(self, name:str) -> None:
        pass


class Scenario:
    def __init__(self) -> None:
        pass


class PredefinedScenario:
    def __init__(self) -> None:
        pass
