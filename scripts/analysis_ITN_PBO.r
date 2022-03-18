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

plot_export_path <- here("Results", "PBO vs LLINs")

cases_reduction_with_net <- c()
cases_reduction_with_pbo_same_coverage <- c()
cases_reduction_with_pbo_same_budget_global_fund <- c()
cases_reduction_with_pbo_same_budget_ellie_2022 <- c()

im_year <- c()
im_adm1 <- c()
im_cases_no_net <- c()
im_cases_net <- c()
im_cases_pbo <- c()
im_cases_pbo_gf <- c()
im_cases_pbo_ellie <- c()

om_year <- c()
om_adm1 <- c()
om_cases_net <- c()
om_cases_pbo <- c()
om_cases_pbo_gf <- c()
om_cases_pbo_ellie <- c()

imperial_plots_list <- list()

for (row in 1:nrow(gha_params)) {
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
  # r_ITN_1 <- gha_params[row, "r_ITN_1"]
  # r_PBO_1 <- gha_params[row, "r_PBO_1"]
  adm1_without_intervention <- run_model(
    init_EIR = eir,
    country = "Ghana",
    admin2 = old_province,
    time = 365 * 4,
    init_ft = treatment_seeking
  )
  # plot(adm1_without_intervention$t,
  #     adm1_without_intervention$prev,
  #     main = paste("Prevalance -", province),
  #     ylim = c(0, 1),
  #     type = "l"
  # )
  prevelance_without_net <- sum(adm1_without_intervention$prev)
  # regular
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

  adm1_switching_to_PBO_same_budget_gf <- run_model(
    init_EIR = eir,
    country = "Ghana",
    admin2 = old_province,
    time = 365 * 4,
    num_int = 3,
    itn_cov = pbo_cov_gf,
    irs_cov = irs_cov,
    d_ITN0 = d_PBO_0,
    r_ITN0 = r_PBO_0,
    # r_ITN1 = r_PBO_1,
    itn_half_life = half_life_pbo,
    ITN_IRS_on = 200,
    init_ft = treatment_seeking
  )
  # plot(adm1_switching_to_PBO_same_budget_gf$t,
  #     adm1_switching_to_PBO_same_budget_gf$prev,
  #     main = paste("Prevalance Switching to PBO SAME budget -", province),
  #     ylim = c(0, 1),
  #     type = "l"
  # )
  prevelance_switching_pbo_same_budget_gf <-
    sum(adm1_switching_to_PBO_same_budget_gf$prev)

  adm1_switching_to_PBO_same_budget_ellie <- run_model(
    init_EIR = eir,
    country = "Ghana",
    admin2 = old_province,
    time = 365 * 4,
    num_int = 3,
    itn_cov = pbo_cov_ellie,
    irs_cov = irs_cov,
    d_ITN0 = d_PBO_0,
    r_ITN0 = r_PBO_0,
    # r_ITN1 = r_PBO_1,
    itn_half_life = half_life_pbo,
    ITN_IRS_on = 200,
    init_ft = treatment_seeking
  )
  # plot(adm1_switching_to_PBO_same_budget_ellie$t,
  #     adm1_switching_to_PBO_same_budget_ellie$prev,
  #     main = paste("Prevalance Switching to PBO SAME budget -", province),
  #     ylim = c(0, 1),
  #     type = "l"
  # )
  prevelance_switching_pbo_same_budget_ellie <-
    sum(adm1_switching_to_PBO_same_budget_ellie$prev)

  # print("different with/without net:")
  # print(prevelance_without_net - prevelance_with_net)
  # print("different with/without PBO:")
  # print(prevelance_without_net - prevelance_switching_pbo)
  n_cases_without_net <- prevelance_without_net * total_population
  n_reduced_cases_net <- total_population *
    (prevelance_without_net - prevelance_with_net)
  cases_reduction_with_net <- c(
    cases_reduction_with_net,
    n_reduced_cases_net
  )
  n_reduced_cases_pbo <- total_population *
    (prevelance_without_net - prevelance_switching_pbo)

  cases_reduction_with_pbo_same_coverage <-
    c(
      cases_reduction_with_pbo_same_coverage,
      n_reduced_cases_pbo
    )
  n_reduced_cases_pbo_same_budget_gf <- total_population *
    (prevelance_without_net - prevelance_switching_pbo_same_budget_gf)
  cases_reduction_with_pbo_same_budget_global_fund <- c(
    cases_reduction_with_pbo_same_budget_global_fund,
    n_reduced_cases_pbo_same_budget_gf
  )
  n_reduced_cases_pbo_same_budget_ellie <- total_population *
    (prevelance_without_net - prevelance_switching_pbo_same_budget_ellie)
  cases_reduction_with_pbo_same_budget_ellie_2022 <- c(
    cases_reduction_with_pbo_same_budget_ellie_2022,
    n_reduced_cases_pbo_same_budget_ellie
  )
  # print("Reduced cases with nets")
  # print(n_reduced_cases_net)
  # print("Reduced cases with PBO")
  # print(n_reduced_cases_pbo)
  # print("Reduced cases with PBO - Same budget as LLINs - global funds")
  # print(n_reduced_cases_pbo_same_budget_gf)
  price_with_net_global_fund <- llins_distributed * 2.17
  price_with_pbo_global_fund <- llins_distributed * 3.09
  price_with_net_ellie_2022 <- llins_distributed * 2.0
  price_with_pbo_ellie_2022 <- llins_distributed * 2.3
  # print("price with net")
  # print(price_with_net)
  # print("price with pbo")
  # print(price_with_pbo)
  # print("$ per averted cases with net")
  # print(price_with_net / n_reduced_cases_net)
  # print("$ per averted cases with pbo")
  # print(price_with_pbo / n_reduced_cases_pbo)
  year <- adm1_without_intervention$t / 365
  without_intervention <- adm1_without_intervention$prev * total_population / 1000000
  with_net <- adm1$prev * total_population / 1000000
  with_pbo <- adm1_switching_to_PBO$prev * total_population / 1000000
  with_pbo_gf <- adm1_switching_to_PBO_same_budget_gf$prev * total_population / 1000000
  with_pbo_ellie <- adm1_switching_to_PBO_same_budget_ellie$prev * total_population / 1000000

  im_year <- append(im_year, year)
  im_adm1 <- append(im_adm1, rep(province, length(year)))
  im_cases_no_net <- append(im_cases_no_net, without_intervention)
  im_cases_net <- append(im_cases_net, with_net)
  im_cases_pbo <- append(im_cases_pbo, with_pbo)
  im_cases_pbo_gf <- append(im_cases_pbo_gf, with_pbo_gf)
  im_cases_pbo_ellie <- append(im_cases_pbo_ellie, with_pbo_ellie)
  prevalance <- data.frame(
    year,
    without_intervention,
    with_net,
    with_pbo,
    with_pbo_gf,
    with_pbo_ellie
  )
  im_plot_adm1 <- ggplot(
    data = prevalance,
    aes(x = year)
  ) +
    geom_line(aes(
      y = without_intervention,
      color = "No Net"
    )) +
    geom_line(aes(
      y = with_net,
      color = "Pyrethroid Only",
      linetype = "dashed"
    )) +
    geom_line(aes(
      y = with_pbo,
      color = "PBO",
      linetype = "dashed"
    )) +
    geom_line(aes(
      y = with_pbo_gf,
      color = "PBO_GF",
      linetype = "twodash"
    )) +
    geom_line(aes(
      y = with_pbo_ellie,
      color = "PBO_E",
      linetype = "twodash"
    )) +
    scale_color_manual(
      name = "Intervention",
      values = c(
        "No Net" = "grey69",
        "Pyrethroid Only" = "darkred",
        "PBO" = "steelblue",
        "PBO_GF" = "#b56d02",
        "PBO_E" = "#099009"
      )
    ) +
    ylab("Cases in Millions") +
    guides(linetype = "none") +
    ggtitle(
      paste(
        "IM - ",
        province,
        "- PBO vs LLINs"
      )
    )
  show(im_plot_adm1)
  ggsave(filename = paste(
    "IM -",
    province,
    ".png"
  ), path = plot_export_path)
  imperial_plots_list <- append(imperial_plots_list, im_plot_adm1)
}

im_output <- data.frame(
  im_year,
  im_adm1,
  im_cases_no_net,
  im_cases_net,
  im_cases_pbo,
  im_cases_pbo_gf,
  im_cases_pbo_ellie
)

ggplot(
  data = im_output,
  aes(x = im_year)
) +
  geom_line(aes(
    y = im_cases_no_net,
    color = "No Net"
  )) +
  geom_line(aes(
    y = im_cases_net,
    color = "Pyrethroid Only",
    linetype = "dashed"
  )) +
  geom_line(aes(
    y = im_cases_pbo,
    color = "PBO",
    linetype = "dashed"
  )) +
  geom_line(aes(
    y = im_cases_pbo_gf,
    color = "PBO_GF",
    linetype = "twodash"
  )) +
  geom_line(aes(
    y = im_cases_pbo_ellie,
    color = "PBO_E",
    linetype = "twodash"
  )) +
  scale_color_manual(
    name = "Intervention",
    values = c(
      "No Net" = "grey69",
      "Pyrethroid Only" = "darkred",
      "PBO" = "steelblue",
      "PBO_GF" = "#b56d02",
      "PBO_E" = "#099009"
    )
  ) +
  ylab("Cases in Millions") +
  xlab("Year") +
  guides(linetype = "none") +
  ggtitle(
    "IM - PBO vs LLINs"
  ) +
  facet_wrap(. ~ im_adm1, scales = "free_y", ncol = 4)
ggsave(
  filename = "IM - PBO vs LLINs.png",
  path = plot_export_path
)

output <- data.frame(
  gha_params["adm1"],
  gha_params["total_population"],
  gha_params["MORTALITY_ADJUSTED"],
  cases_reduction_with_net,
  cases_reduction_with_pbo_same_coverage,
  cases_reduction_with_pbo_same_budget_global_fund,
  cases_reduction_with_pbo_same_budget_ellie_2022
)

write.csv(output, "~/Dropbox/benchmarking/Results/imperial.csv")

# cases reduction with PBO same coverage
plot_with_pbo_same_coverage <- ggplot(
  data = output,
  mapping = aes(
    x = adm1,
    y = (
      cases_reduction_with_pbo_same_coverage -
        cases_reduction_with_net
    ) / total_population / 3,
    label = (
      cases_reduction_with_pbo_same_coverage -
        cases_reduction_with_net
    ) / total_population / 3
  )
) +
  geom_col() +
  labs(
    x = "Provinces",
    y = "Cases Averted / Person / Year"
  ) +
  theme(axis.text.x = element_text(
    angle = 90,
    vjust = 0.5,
    hjust = 1
  )) +
  scale_fill_brewer(palette = "Blues") +
  ggtitle("IM - Cases averted - Switch to PBO - Same Coverage")
show(plot_with_pbo_same_coverage)
ggsave(
  filename = "IM - Cases Averted - Switch to PBO - Same Coverage.png",
  path = plot_export_path
)
# cases reduction with PBO same budget
plot_with_pbo_same_budget_ellie_2022 <- ggplot(
  data = output,
  mapping = aes(
    x = adm1,
    y = (
      cases_reduction_with_pbo_same_budget_ellie_2022 -
        cases_reduction_with_net
    ) / total_population / 3,
    label = (
      cases_reduction_with_pbo_same_budget_ellie_2022 -
        cases_reduction_with_net
    ) / total_population / 3
  )
) +
  geom_col() +
  labs(
    x = "Provinces",
    y = "Cases Averted / Person / Year"
  ) +
  theme(axis.text.x = element_text(
    angle = 90,
    vjust = 0.5,
    hjust = 1
  )) +
  scale_fill_brewer(palette = "Blues") +
  ggtitle("IM - Cases averted - Switch to PBO - Same Budget")
show(plot_with_pbo_same_budget_ellie_2022)
ggsave(
  filename =
    "IM - Cases Averted - Switch to PBO - Same Budget.png",
  path = plot_export_path
)
# relationship with resistance and cases averted
plot_resistance_cases_averted <- ggplot(
  data = output,
  mapping = aes(
    x = MORTALITY_ADJUSTED,
    y = (
      cases_reduction_with_pbo_same_budget_ellie_2022 -
        cases_reduction_with_net
    ) / total_population / 3,
    label = adm1
  )
) +
  geom_point()
show(plot_resistance_cases_averted)

# reading openmalaria output

for (row in 1:nrow(gha_params)) {
  province <- gha_params[row, "adm1"]
  xml_output_df <- read.csv(
    paste0(
      "/Users/sepmein/Dropbox/benchmarking/Data/openmalaria/output_xml/",
      province,
      ".csv"
    )
  )
  xml_output_plot <- ggplot(
    data = xml_output_df,
    aes(x = year)
  ) +
    geom_line(aes(
      y = net,
      color = "Pyrethroid Only",
      linetype = "dashed"
    )) +
    geom_line(aes(
      y = pbo,
      color = "PBO",
      linetype = "dashed"
    )) +
    geom_line(aes(
      y = pbo_gf,
      color = "PBO_GF",
      linetype = "twodash"
    )) +
    geom_line(aes(
      y = pbo_ellie,
      color = "PBO_E",
      linetype = "twodash"
    )) +
    scale_color_manual(
      name = "Intervention",
      values = c(
        "Pyrethroid Only" = "darkred",
        "PBO" = "steelblue",
        "PBO_GF" = "#b56d02", "PBO_E" = "#099009"
      )
    ) +
    ylab("Cases in Millions") +
    guides(linetype = "none") +
    ggtitle(
      paste0(
        "OM - ",
        province,
        "- Switch to PBO"
      )
    )
  show(xml_output_plot)
  ggsave(
    filename = paste(
      "OM -",
      province,
      ".png"
    ),
    path = plot_export_path
  )
  year <- xml_output_df$year
  with_net <- xml_output_df$net
  with_pbo <- xml_output_df$pbo
  with_pbo_gf <- xml_output_df$pbo_gf
  with_pbo_ellie <- xml_output_df$pbo_ellie
  om_year <- append(om_year, year)
  om_adm1 <- append(om_adm1, rep(province, length(year)))
  om_cases_net <- append(om_cases_net, with_net)
  om_cases_pbo <- append(om_cases_pbo, with_pbo)
  om_cases_pbo_gf <- append(om_cases_pbo_gf, with_pbo_gf)
  om_cases_pbo_ellie <- append(om_cases_pbo_ellie, with_pbo_ellie)
}

om_output <- data.frame(
  om_year,
  om_adm1,
  om_cases_net,
  om_cases_pbo,
  om_cases_pbo_gf,
  om_cases_pbo_ellie
)


ggplot(
  data = om_output,
  aes(x = om_year)
) +
  geom_line(aes(
    y = om_cases_net,
    color = "Pyrethroid Only",
    linetype = "dashed"
  )) +
  geom_line(aes(
    y = om_cases_pbo,
    color = "PBO",
    linetype = "dashed"
  )) +
  geom_line(aes(
    y = om_cases_pbo_gf,
    color = "PBO_GF",
    linetype = "twodash"
  )) +
  geom_line(aes(
    y = om_cases_pbo_ellie,
    color = "PBO_E",
    linetype = "twodash"
  )) +
  scale_color_manual(
    name = "Intervention",
    values = c(
      "Pyrethroid Only" = "darkred",
      "PBO" = "steelblue",
      "PBO_GF" = "#b56d02",
      "PBO_E" = "#099009"
    )
  ) +
  ylab("Cases in Millions") +
  xlab("Year") +
  guides(linetype = "none") +
  ggtitle(
    "OM - PBO vs LLINs"
  ) +
  facet_wrap(. ~ om_adm1, scales = "free_y", ncol = 4)
ggsave(
  filename = "OM - PBO vs LLINs.png",
  path = plot_export_path
)
