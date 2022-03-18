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
source(here('mbench', "scripts", "get_prevalence_by_eir.R"))

rows <- 1:nrow(gha_params)
prevalences <- c(0.05, 0.10, 0.20, 0.30)
itn_covs <- c(0.6, 0.8)

plot_export_path <- here("Results", "ITNs_different_levels_of_prevalence")

cases_reduction_with_net <- c()

output <- foreach(row = rows, .combine = "rbind") %:%
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

    prevalence_with_itn <- sum(output_with_itn$prev)

    return(data.frame(
      adm1 = province,
      initial_prevalence = prevalence,
      itn_coverage = itn_cov,
      prevalence_with_itn = prevalence_with_itn,
      total_population = total_population
    ))
  }

write.csv(
  output,
  here("Results", "ITN_with_different_prevalence_level.csv")
)


output <- read.csv(here("Results", "ITN_with_different_prevalence_level.csv"))
itn60 = subset(output, itn_coverage == 0.6)
itn80 = subset(output, itn_coverage == 0.8)
ratio = itn80['prevalence_with_itn'] / itn60['prevalence_with_itn']
itn60['ratio'] = ratio

library(ggstatsplot)

ggwithinstats(
    data= itn60,
    x = initial_prevalence,
    y = ratio,
    xlab = "Initial Prevalence(%)",
    ylab = "Mean Prevalence Ratio(ITN Coverage 80% / 60%)",
)
ggsave(
  here("Results", "IM_prevalence_ratio_between_itn_60_with_itn_80.png"),
  width = 9.22,
  height = 7.12,
  dpi = 600
)

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
  here("Results", "ITN_with_different_prevalence_level_detail.csv")
)

detail_itn_60 <- subset(
    output_detail,
    itn_coverage == 0.6
)
detail_itn_80 <- subset(
    output_detail,
    itn_coverage == 0.8
)
detail_itn_60['prevalence_80'] = detail_itn_80['prevalence']

ggplot(
  data = subset(detail_itn_60, initial_prevalence==5),
  aes(x = date)
) +
  geom_line(
      aes(y = prevalence,
      color = "ITN 60%"
      ),
  ) +
  geom_line(
      aes(y = prevalence_80, 
      color = "ITN 80%"
      ),
  ) +
  ylab("Prevalence") +
  xlab("Time") +
  ggtitle(
        "IM - Initial Prevalence 5% "
  ) +
  scale_color_manual(
    name = "ITN coverage",
    values = c(
      "ITN 60%" = "darkred",
      "ITN 80%" = "steelblue"
    )
  ) +
  theme(legend.title = element_text(angle = -90)) +
  facet_wrap(. ~ adm1, ncol = 4)
ggsave(
    here("Results", "IM_prevalence_ratio_between_itn_60_with_itn_80_detail_prevalence_5.png"),
    width = 9.22,
    height = 7.12,
    dpi = 600
)

ggplot(
  data = subset(detail_itn_60, initial_prevalence==10),
  aes(x = date)
) +
  geom_line(
      aes(y = prevalence,
      color = "ITN 60%"
      ),
  ) +
  geom_line(
      aes(y = prevalence_80, 
      color = "ITN 80%"
      ),
  ) +
  ylab("Prevalence") +
  xlab("Time") +
  ggtitle(
        "IM - Initial Prevalence 10% "
  ) +
  scale_color_manual(
    name = "ITN coverage",
    values = c(
      "ITN 60%" = "darkred",
      "ITN 80%" = "steelblue"
    )
  ) +
  theme(legend.title = element_text(angle = -90)) +
  facet_wrap(. ~ adm1, ncol = 4)

ggsave(
    here("Results", "IM_prevalence_ratio_between_itn_60_with_itn_80_detail_prevalence_10.png"),
    width = 9.22,
    height = 7.12,
    dpi = 600
)

ggplot(
  data = subset(detail_itn_60, initial_prevalence==20),
  aes(x = date)
) +
  geom_line(
      aes(y = prevalence,
      color = "ITN 60%"
      ),
  ) +
  geom_line(
      aes(y = prevalence_80, 
      color = "ITN 80%"
      ),
  ) +
  ylab("Prevalence") +
  xlab("Time") +
  ggtitle(
        "IM - Initial Prevalence 20% "
  ) +
  scale_color_manual(
    name = "ITN coverage",
    values = c(
      "ITN 60%" = "darkred",
      "ITN 80%" = "steelblue"
    )
  ) +
  theme(legend.title = element_text(angle = -90)) +
  facet_wrap(. ~ adm1, ncol = 4)
ggsave(
    here("Results", "IM_prevalence_ratio_between_itn_60_with_itn_80_detail_prevalence_20.png"),
    width = 9.22,
    height = 7.12,
    dpi = 600
)


ggplot(
  data = subset(detail_itn_60, initial_prevalence==30),
  aes(x = date)
) +
  geom_line(
      aes(y = prevalence,
      color = "ITN 60%"
      ),
  ) +
  geom_line(
      aes(y = prevalence_80, 
      color = "ITN 80%"
      ),
  ) +
  ylab("Prevalence") +
  xlab("Time") +
  ggtitle(
        "IM - Initial Prevalence 30% "
  ) +
  scale_color_manual(
    name = "ITN coverage",
    values = c(
      "ITN 60%" = "darkred",
      "ITN 80%" = "steelblue"
    )
  ) +
  theme(legend.title = element_text(angle = -90)) +
  facet_wrap(. ~ adm1, ncol = 4)
ggsave(
    here("Results", "IM_prevalence_ratio_between_itn_60_with_itn_80_detail_prevalence_30.png"),
    width = 9.22,
    height = 7.12,
    dpi = 600
)
