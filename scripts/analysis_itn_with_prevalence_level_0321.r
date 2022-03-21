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
source(here("mbench", "scripts", "get_prevalence_by_eir.R"))

rows <- 1:1
prevalences <- c(0.03, 0.05, 0.10, 0.20, 0.30, 0.5)
itn_covs <- c(0.6, 0.8)

plot_export_path <- here("Results", "ITNs_different_levels_of_prevalence")

cases_reduction_with_net <- c()

output_detail <- foreach(row = rows, .combine = "rbind") %:%
  foreach(prevalence = prevalences, .combine = "rbind") %:%
  foreach(itn_cov = itn_covs, .combine = "rbind") %dopar% {
    eta <- gha_params[row, "eta"]
    rho <- gha_params[row, "rho"]
    eir <- get_eir_by_prevalence(prevalence)
    province <- gha_params[row, "adm1"]
    old_province <- gha_params[row, "old_district_name"]
    itn_cov <- itn_cov
    treatment_seeking <-
      gha_params[row, "treatment_seeking"]
    total_population <-
      gha_params[row, "total_population"]
    llins_distributed <-
      gha_params[row, "llins_distributed"]
    resistance <- 1 - gha_params[row, "MORTALITY_ADJUSTED"] / 100

    hut_trail_outcomes <- get_hut_trail_outcome_by_resistance(resistance)
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
      time = 365 * 5,
      num_int = 3,
      itn_cov = itn_cov,
      d_ITN0 = d_itn,
      r_ITN0 = r_itn,
      itn_half_life = h_itn,
      ITN_IRS_on = 1,
      ITN_interval = 3 * 365,
      init_ft = treatment_seeking
    )

    return(data.frame(
      adm1 = province,
      date = output_with_itn$t,
      prevalence = output_with_itn$prev,
      initial_prevalence = prevalence,
      itn_coverage = itn_cov,
      total_population = total_population
    ))
  }
write.csv(
  output_detail,
  here("Results", "ITN_with_different_prevalence_level_detail_0321.csv")
)

library(reshape2)
output_detail_short <- output_detail[
  c("date", "prevalence", "initial_prevalence", "itn_coverage")
]
output_detail_wide <- dcast(
  output_detail_short,
  date + itn_coverage ~ initial_prevalence,
  value.var = "prevalence"
)
colnames(output_detail_wide) <- c(
  "date",
  "itn_coverage",
  "p03", "p05", "p10", "p20", "p30", "p50"
)
scaler <- head(subset(output_detail_wide, date == 0), 1)
scaler_03 <- as.numeric(scaler["p03"])
scaler_05 <- as.numeric(scaler["p05"])
scaler_10 <- as.numeric(scaler["p10"])
scaler_20 <- as.numeric(scaler["p20"])
scaler_30 <- as.numeric(scaler["p30"])
scaler_50 <- as.numeric(scaler["p50"])

ggplot(
  data = output_detail_wide,
  aes(x = date / 365)
) +
  geom_line(
    aes(
      y = p03 / scaler_03 * 0.03,
      color = "0.03"
    ),
  ) +
  geom_line(
    aes(
      y = p05 / scaler_05 * 0.05,
      color = "0.05"
    ),
  ) +
  geom_line(
    aes(
      y = p10 / scaler_10 * 0.10,
      color = "0.1"
    ),
  ) +
  geom_line(
    aes(
      y = p20 / scaler_20 * 0.20,
      color = "0.2"
    ),
  ) +
  geom_line(
    aes(
      y = p30 / scaler_30 * 0.30,
      color = "0.3"
    ),
  ) +
  geom_line(
    aes(
      y = p50 / scaler_50 * 0.50,
      color = "0.5"
    ),
  ) +
  ylab("Prevalence") +
  xlab("Year") +
  ggtitle(
    "Prevalences Differences between 60% ITN coverage with 80% ITN coverage"
  ) +
  scale_color_manual(
    name = "Initial Prevalence",
    values = c(
      "0.05" = "darkred",
      "0.03" = "steelblue",
      "0.1" = "#46b462",
      "0.2" = "#b46046",
      "0.3" = "#050505",
      "0.5" = "#b44683"
    )
  ) +
  facet_wrap(.~itn_coverage, ncol=2) +
  theme(legend.title = element_text(angle = -90))

ggsave(
  here("Results",
   "IM_prevalence_ratio_between_itn_60_with_itn_80_detail_prevalence_0321.png"),
  width = 9.22,
  height = 7.12,
  dpi = 600
)
