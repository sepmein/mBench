# https://www.researchgate.net/profile/John-Beier/publication/12867829_Short_report_Entomologic_inoculation_rates_and_Plasmodium_falciparum_malaria_prevalence_in_Africa/links/004635142eb595e31a000000/Short-report-Entomologic-inoculation-rates-and-Plasmodium-falciparum-malaria-prevalence-in-Africa.pdf

get_prevalence_by_eir <- function(eir) {
    prevalence <- 24.2 * log10(eir) + 24.68
    return(prevalence)
}

get_eir_by_prevalence <- function(prevalence) {
    eir <- 10^((prevalence - 24.68) / 24.2)
    return(eir)
}