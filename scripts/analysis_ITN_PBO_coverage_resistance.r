

compute_cases <- function() {

}

get_itn_pbo_efficay_by_resistance <- function(resistance) {
    read.csv("/Users/sepmein/Dropbox/benchmar")
}

library(parallel)
library(foreach)
library(doParallel)
library(ICDMM,
    help,
    pos = 2, lib.loc = NULL
)
# seasonal data
# resource:
library(tidyverse)
library(ggplot2)
library(gdata)
library("gridExtra")


registerDoParallel(detectCores())

gha_params <-
    read.csv("/Users/sepmein/Dropbox/benchmarking/Data/GHA/gha.csv")
plot_export_path <- "/Users/sepmein/Dropbox/benchmarking/Results/ITN_PBO_Coverage_Resistance/" # nolint
itn_pbo_efficacy_ellie_2022_by_resistance_systematic_review <-
    read.csv("/Users/sepmein/dev/github/Mosquito-Net-Parameters/estimates/best_params_from_systematic_review1.csv")

adm1 <- c()
vector_resistance <- c()
pbo_cov_relative_to_itn <- c()
cases_difference <- c()

fx <- function(row) {

}
foreach(row = 1:nrow(gha_params)) %dopar% {
    eta <- gha_params[row, "eta"]
    rho <- gha_params[row, "rho"]
    eir <- gha_params[row, "eir"]
    province <- gha_params[row, "adm1"]
    old_province <- gha_params[row, "old_district_name"]
    itn_cov <- gha_params[row, "itn_cov"]
    pbo_cov_gf <- gha_params[row, "pbo_cov_gf"]
    pbo_cov_ellie <- gha_params[row, "pbo_cov_ellie"]
    irs_cov <- gha_params[row, "irs_cov"]
    treatment_seeking <- gha_params[row, "treatment_seeking"]
    d_ITN_0 <- gha_params[row, "d_ITN_0"]
    d_PBO_0 <- gha_params[row, "d_PBO_0"]
    r_ITN_0 <- gha_params[row, "r_ITN_0"] # nolint
    r_PBO_0 <- gha_params[row, "r_PBO_0"]
    total_population <- gha_params[row, "total_population"]
    llins_distributed <- gha_params[row, "llins_distributed"]
    half_life_itn <- gha_params[row, "h_ITN"] * 365
    half_life_pbo <- gha_params[row, "h_PBO"] * 365


    resistances <- seq(0, 100, by = 5) / 100
    pbo_itn_coverage_ratios <- seq(40, 80, by = 2)
    for (r in resistances) {
        for (ratio in pbo_itn_coverage_ratios) {
            # calculate pbo cov
            pbo_cov <- itn_cov * ratio / 100
            df_sub <- subset(
                itn_pbo_efficacy_ellie_2022_by_resistance_systematic_review,
                resistance == r
            )
            d_ITN_0 <- df_sub$d10
            d_PBO_0 <- df_sub$d20
            r_ITN_0 <- df_sub$r10
            r_PBO_0 <- df_sub$r20
            half_life_itn <- df_sub$h10 * 365
            half_life_pbo <- df_sub$h20 * 365
            adm1 <- run_model(
                init_EIR = eir,
                country = "Ghana",
                admin2 = old_province,
                time = 365 * 4,
                num_int = 3,
                itn_cov = itn_cov,
                irs_cov = irs_cov,
                d_ITN0 = d_ITN_0,
                r_ITN0 = r_ITN_0,
                # r_ITN1 = r_ITN_1,
                itn_half_life = half_life_itn,
                ITN_IRS_on = 200,
                init_ft = treatment_seeking
            )
            # plot(adm1$t,
            #     adm1$prev,
            #     main = paste("Prevalance With LLINs -", province),
            #     ylim = c(0, 1),
            #     type = "l"
            # )
            prevelance_with_net <- sum(adm1$prev)
            adm1_switching_to_PBO <- run_model(
                init_EIR = eir,
                country = "Ghana",
                admin2 = old_province,
                time = 365 * 4,
                num_int = 3,
                itn_cov = itn_cov,
                irs_cov = irs_cov,
                d_ITN0 = d_PBO_0,
                r_ITN0 = r_PBO_0,
                # r_ITN1 = r_PBO_1,
                itn_half_life = half_life_pbo,
                ITN_IRS_on = 200,
                init_ft = treatment_seeking
            )
            # plot(adm1_switching_to_PBO$t,
            #     adm1_switching_to_PBO$prev,
            #     main = paste("Prevalance Switching to PBO -", province),
            #     ylim = c(0, 1),
            #     type = "l"
            # )
            prevelance_switching_pbo <- sum(adm1_switching_to_PBO$prev)
            n_reduced_cases_net <- total_population *
                (prevelance_with_net - prevelance_switching_pbo)

            adm1 <- c(adm1, province)
            vector_resistance <- c(vector_resistance, r)
            pbo_cov_relative_to_itn <- c(pbo_cov_relative_to_itn, ratio)
            cases_difference <- c(cases_difference, n_reduced_cases_net)
        }
    }
}

output <- data.frame(
    adm1,
    vector_resistance,
    pbo_cov_relative_to_itn,
    cases_difference
)

write.csv(
    output,
    "../../Results/sweat.csv"
)