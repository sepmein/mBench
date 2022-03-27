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

source(here("mbench", "scripts", "set_env.R"))
source(here("mbench", "scripts", "get_hut_trail_outcome_by_resistance.R"))

plot_export_path <-
  here("Results", "ITN_PBO_Coverage_Resistance")

rows <- 1:nrow(gha_params)
resistances <- seq(90, 100, by = 1) / 100
pbo_itn_coverage_ratios <- seq(0, 100, by = 2)

output <- foreach(row = rows, .combine = "rbind") %:%
  foreach(ratio = pbo_itn_coverage_ratios, .combine = "rbind") %:%
  foreach(r = resistances, .combine = "rbind") %dopar% {
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

    pbo_cov <- itn_cov * ratio / 100
    hut_trail_outcomes <- get_hut_trail_outcome_by_resistance(r)
    d_itn <- hut_trail_outcomes$d_itn
    d_pbo <- hut_trail_outcomes$d_pbo
    r_itn <- hut_trail_outcomes$r_itn
    r_pbo <- hut_trail_outcomes$r_pbo
    h_itn <- hut_trail_outcomes$h_itn
    h_pbo <- hut_trail_outcomes$h_pbo

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

    output_with_pbo <- run_model(
      init_EIR = eir,
      country = "Ghana",
      admin2 = old_province,
      time = 365 * 4,
      num_int = 3,
      itn_cov = pbo_cov,
      irs_cov = irs_cov,
      d_ITN0 = d_pbo,
      r_ITN0 = r_pbo,
      itn_half_life = h_pbo,
      ITN_IRS_on = 200,
      init_ft = treatment_seeking
    )

    prevalence_switching_pbo <-
      sum(output_with_pbo$prev)
    case_difference <- total_population *
      (prevalence_with_itn - prevalence_switching_pbo)

    return(data.frame(
      adm1 = province,
      vector_resistance = r,
      pbo_cov_relative_to_itn = ratio,
      cases_difference = case_difference,
      total_population = total_population
    ))
  }

write.csv(
  output,
  "~/Dropbox/benchmarking/Results/sweet-finer-resistance-90.csv"
)


sweet <- read.csv(here("Results", "sweet.csv"))
relative_case_differences <- sweet$cases_difference / sweet$total_population / 3
contour_breaks <- c(min(relative_case_differences), 0, max(relative_case_differences))

ggplot(
  data = sweet,
  aes(x = vector_resistance * 100, y = pbo_cov_relative_to_itn)
) +
  geom_contour_filled(aes(z = cases_difference / total_population / 3)) +
  geom_contour(aes(
    z = cases_difference / total_population / 3
  ), breaks = contour_breaks) +
  ylab("PBO coverage relative to ITNs(%)") +
  xlab("Vector Resistance(%)") +
  ggtitle(
    "IM - Cases Averted - Switching to PBO"
  ) +
  guides(
    fill = guide_colorsteps(
      ticks = TRUE,
      barwidth = .5,
      barheight = 20,
      title = "Cases averted / Person / Year",
      title.position = "right",
      # title.vjust = 0.5
    )
  ) +
  theme(legend.title = element_text(angle = -90)) +
  facet_wrap(. ~ adm1, ncol = 4)
ggsave(
  here("Results", "IM_cases_averted_PBO_with_difference_resistance_and_coverage.png"),
  width = 9.22,
  height = 7.12,
  dpi = 600
)
