library(parallel)
library(foreach)
library(doParallel)
library(ICDMM,
        help,
        pos = 2, lib.loc = NULL)
library(tidyverse)
library(ggplot2)
library(gdata)
library("gridExtra")
library("scales")

registerDoParallel(detectCores())

gha_params <-
  read.csv("/Users/sepmein/Dropbox/benchmarking/Data/GHA/gha.csv")
plot_export_path <-
  "/Users/sepmein/Dropbox/benchmarking/Results/ITN_PBO_Coverage_Resistance/" # nolint
itn_pbo_efficacy_ellie_2022_by_resistance_systematic_review <-
  read.csv(
    "/Users/sepmein/dev/github/Mosquito-Net-Parameters/estimates/best_params_from_systematic_review1.csv"
  )

rows <- 1:nrow(gha_params)
resistances <- seq(0, 100, by = 5) / 100
pbo_itn_coverage_ratios <- seq(70, 80, by = .5)

output <- foreach(row = rows, .combine = 'rbind') %:%
  foreach(r = resistances, .combine = 'rbind') %:%
  foreach(ratio = pbo_itn_coverage_ratios, .combine = 'rbind') %dopar% {
    eta <- gha_params[row, "eta"]
    rho <- gha_params[row, "rho"]
    eir <- gha_params[row, "eir"]
    province <- gha_params[row, "adm1"]
    old_province <- gha_params[row, "old_district_name"]
    itn_cov <- gha_params[row, "itn_cov"]
    pbo_cov_gf <- gha_params[row, "pbo_cov_gf"]
    pbo_cov_ellie <- gha_params[row, "pbo_cov_ellie"]
    irs_cov <- gha_params[row, "irs_cov"]
    treatment_seeking <-
      gha_params[row, "treatment_seeking"]
    total_population <-
      gha_params[row, "total_population"]
    llins_distributed <-
      gha_params[row, "llins_distributed"]

    pbo_cov <- itn_cov * ratio / 100
    df_sub <- subset(itn_pbo_efficacy_ellie_2022_by_resistance_systematic_review,
                     resistance == r)
    d_ITN_0 <- df_sub$d10
    d_PBO_0 <- df_sub$d20
    r_ITN_0 <- df_sub$r10
    r_PBO_0 <- df_sub$r20
    half_life_itn <- df_sub$h10 * 365
    half_life_pbo <- df_sub$h20 * 365
    output_with_net <- run_model(
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

    prevalence_with_net <- sum(output_with_net$prev)
    adm1_switching_to_PBO <- run_model(
      init_EIR = eir,
      country = "Ghana",
      admin2 = old_province,
      time = 365 * 4,
      num_int = 3,
      itn_cov = pbo_cov,
      irs_cov = irs_cov,
      d_ITN0 = d_PBO_0,
      r_ITN0 = r_PBO_0,
      # r_ITN1 = r_PBO_1,
      itn_half_life = half_life_pbo,
      ITN_IRS_on = 200,
      init_ft = treatment_seeking
    )

    prevalence_switching_pbo <-
      sum(adm1_switching_to_PBO$prev)
    n_reduced_cases_net <- total_population *
      (prevalence_with_net - prevalence_switching_pbo)

    return(data.frame(
      adm1=province,
      vector_resistance=r,
      pbo_cov_relative_to_itn=ratio,
      cases_difference=n_reduced_cases_net,
      population=total_population
    ))
  }

write.csv(output,
          "~/Dropbox/benchmarking/Results/sweet-finer-70-80.csv")

output <- read.csv("~/Dropbox/benchmarking/Results/sweet.csv")
ggplot(
  data = output,
  aes(x = vector_resistance*100, y = pbo_cov_relative_to_itn)
) + geom_tile(aes(fill=cases_difference/population))+
  ylab("PBO coverage relative to ITNs(%)") +
  xlab("Vector Resistance(%)") +
  guides(linetype = "none") +
  ggtitle(
    "IM - Influences on Coverage and Resistance on Prevalence"
  ) +
  scale_fill_gradientn(colors = hcl.colors(20, "BrBG"),
                       values = rescale(c(-500, 0, 100))
                       ) +
  coord_fixed() +
  guides(fill=guide_colorbar(barwidth = .5, barheight = 20, title = "Cases")) +
  facet_wrap(. ~ adm1, ncol = 4)
