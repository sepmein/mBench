 
library(parallel)
library(foreach)
library(doParallel)
library(ICDMM,
  help,
  pos = 2, lib.loc = NULL
)
 library(tidyverse)
library(ggplot2)
library(gdata)
library("gridExtra")
library("scales")
library("here")

registerDoParallel(detectCores())
if (.Platform$OS.type == "unix") {
  dir <- "/Users/sepmein/Dropbox/benchmarking/"
} else {
  dir <- "C:\\Users\\zhangc\\Dropbox\\benchmarking\\"
}

setwd(dir)

gha_params <-
  read.csv(here("Data", "GHA", "gha.csv"))
 
get_hut_trail_outcome_by_resistance <- function(r) {
  itn_pbo_params <-
    read.csv(
       here(
        "github",
        "Mosquito-Net-Parameters", "estimates",
        "best_params_from_systematic_review1.csv"
      )
    )
  g2_params <-
    read.csv(here(
      "github",
      "Mosquito-Net-Parameters",
      "estimates", "g2_itn.csv"
    ))
   itn_pbo_params_by_resistance <-
    subset(itn_pbo_params, resistance == r)
  g2_params_by_resistance <-
    subset(g2_params, bioassay_mortality == 1 - r)
  d_itn <- itn_pbo_params_by_resistance$d10
  d_pbo <- itn_pbo_params_by_resistance$d20
  d_g2 <- g2_params_by_resistance$dn0_med
  r_itn <- itn_pbo_params_by_resistance$r10
  r_pbo <- itn_pbo_params_by_resistance$r20
  r_g2 <- g2_params_by_resistance$rn0_med
  h_itn <- itn_pbo_params_by_resistance$h10 * 365
  h_pbo <- itn_pbo_params_by_resistance$h20 * 365
  h_g2 <- g2_params_by_resistance$gamman_med * 365
 
  return(data.frame(d_itn, r_itn, h_itn, d_pbo, r_pbo, h_pbo, d_g2, r_g2, h_g2))
}


rows <- 1:nrow(gha_params)
resistances <- seq(0, 100, by = 2) / 100
coverage_ratios <- seq(70.2, 80.2, by = .2)

output <- foreach(row = rows, .combine = "rbind") %:%
  foreach(r = resistances, .combine = "rbind") %:%
  foreach(
    ratio = coverage_ratios,
    .combine = "rbind",
    .packages = c("here", "ICDMM"),
  ) %dopar% {
     eta <- gha_params[row, "eta"]
    rho <- gha_params[row, "rho"]
    eir <- gha_params[row, "eir"]
    province <- gha_params[row, "adm1"]
    old_province <- gha_params[row, "old_district_name"]
    itn_cov <- gha_params[row, "itn_cov"]
    irs_cov <- gha_params[row, "irs_cov"]
    treatment_seeking <-
      gha_params[row, "treatment_seeking"]
    total_population <-
      gha_params[row, "total_population"]
    llins_distributed <-
      gha_params[row, "llins_distributed"]

    g2_cov <- itn_cov * ratio / 100

    hut_trail_outcomes <- get_hut_trail_outcome_by_resistance(r)
    d_itn <- hut_trail_outcomes$d_itn
    d_g2 <- hut_trail_outcomes$d_g2
    r_itn <- hut_trail_outcomes$r_itn
    r_g2 <- hut_trail_outcomes$r_g2
    h_itn <- hut_trail_outcomes$h_itn
    h_g2 <- hut_trail_outcomes$h_g2

    output_with_itn <- run_model(
      init_EIR = eir,
      country = "Ghana",
      admin2 = old_province,
      time = 365 * 4,
      num_int = 3,
      itn_cov = itn_cov,
      irs_cov = irs_cov,
      d_ITN0 = d_itn,
      r_ITN0 = r_itn,
      itn_half_life = h_itn,
      ITN_IRS_on = 200,
      init_ft = treatment_seeking
    )

    prevalence_with_itn <- sum(output_with_itn$prev)


    output_with_g2 <- run_model(
      init_EIR = eir,
      country = "Ghana",
      admin2 = old_province,
      time = 365 * 4,
      num_int = 3,
      itn_cov = g2_cov,
      irs_cov = irs_cov,
      d_ITN0 = d_g2,
      r_ITN0 = r_g2,
      itn_half_life = h_g2,
      ITN_IRS_on = 200,
      init_ft = treatment_seeking
    )

    prevalence_switching_g2 <-
      sum(output_with_g2$prev)
    n_reduced_cases_net <- total_population *
      (prevalence_with_itn - prevalence_switching_g2)

    setwd(dir)
    write.table(
      data.frame(
        adm1 = province,
        vector_resistance = r,
        g2_cov_relative_to_itn = ratio,
        cases_difference = n_reduced_cases_net,
        total_population = total_population
      ),
      here("Results", "sweet-g2-windows.csv"),
      sep = ",",
      append = TRUE,
      col.names = FALSE
    )
    # return(data.frame(
    #   adm1 = province,
    #   vector_resistance = r,
    #   g2_cov_relative_to_itn = ratio,
    #   cases_difference = n_reduced_cases_net,
    #   total_population = total_population
    # ))
  }


sweet_g2 <- read.csv(here("Results", "sweet-g2.csv"))
relative_cases_diffences <- sweet_g2$cases_difference / sweet_g2$total_population
contour_breaks <- c(min(relative_cases_diffences), 0, max(relative_cases_diffences))
ggplot(
  data = sweet_g2,
  aes(x = vector_resistance * 100, y = g2_cov_relative_to_itn)
) +
  geom_contour_filled(aes(
    z =
      cases_difference / total_population
  )) +
  geom_contour(aes(
    z = cases_difference / total_population
  ), breaks = contour_breaks) +
  ylab("G2 coverage relative to ITNs(%)") +
  xlab("Vector Resistance(%)") +
  ggtitle("IM - G2 Influences on Coverage and Resistance on Prevalence") +
  # scale_fill_distiller(palette = "BrBG",
  #       values = rescale(c(-500., 0., 100.))
  #      ) +
  # coord_fixed() +
  # guides(fill=guide_colorbar(barwidth = .5, barheight = 20, title = "Cases")) +
  facet_wrap(. ~ adm1, ncol = 4)
