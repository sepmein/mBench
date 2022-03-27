from math import log10


def get_prevalence_by_eir(eir):
    prevalence = (24.2 * log10(eir) + 24.68) / 100
    return prevalence


def get_eir_by_prevalence(prevalence):
    eir = 10 ** ((prevalence * 100 - 24.68) / 24.2)
    return eir
