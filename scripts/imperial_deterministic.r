library(ICDMM,
    help,
    pos = 2, lib.loc = NULL
)
# seasonal data
# resource:
library(gdata)
library(ggplot2)

gha_params <- read.csv("/Users/sepmein/Dropbox/benchmarking/Data/GHA/gha.csv")
gha_params$adm1
for (row in 1:nrow(gha_params)) {
    eta <- gha_params[row, "eta"]
    rho <- gha_params[row, "rho"]
    eir <- gha_params[row, "eir"]
    province <- gha_params[row, "adm1"]
    old_province <- gha_params[row, "old_district_name"]
    # province <- gha_params[row, "adm1"]
    itn_cov <- gha_params[row, "itn_cov"]
    pbo_cov <- gha_params[row, "pbo_cov"]
    irs_cov <- gha_params[row, "irs_cov"]
    treatment_seeking <- gha_params[row, "treatment_seeking"]
    d_ITN_0 <- gha_params[row, "d_ITN_0"]
    d_PBO_0 <- gha_params[row, "d_PBO_0"]
    r_ITN_0 <- gha_params[row, "r_ITN_0"] # nolint
    r_PBO_0 <- gha_params[row, "r_PBO_0"]
    total_population <- gha_params[row, "total_population"]
    llins_distributed <- gha_params[row, "llins_distributed"]
    half_life_itn <- gha_params[row, "h_ITN"]
    half_life_pbo <- gha_params[row, "h_PBO"]
    # r_ITN_1 <- gha_params[row, "r_ITN_1"]
    # r_PBO_1 <- gha_params[row, "r_PBO_1"]
    adm1_without_intervention <- run_model(
        init_EIR = eir,
        country = "Ghana",
        admin2 = province,
        time = 365 * 3 + 200,
        init_ft = treatment_seeking
    )
    plot(adm1_without_intervention$t,
        adm1_without_intervention$prev,
        main = paste("Prevalance -", province),
        ylim = c(0, 1),
        type = "l"
    )
    prevelance_without_net <- sum(adm1_without_intervention$prev)
    # regular
    adm1 <- run_model(
        init_EIR = eir,
        country = "Ghana",
        admin2 = old_province,
        time = 365 * 3 + 200,
        num_int = 3,
        itn_cov = itn_cov,
        irs_cov = irs_cov,
        d_ITN0 = d_ITN_0,
        r_ITN0 = r_ITN_0,
        # r_ITN1 = r_ITN_1,
        # itn_half_life = half_life_itn,
        ITN_IRS_on = 200,
        init_ft = treatment_seeking
    )
    plot(adm1$t,
        adm1$prev,
        main = paste("Prevalance With LLINs -", province),
        ylim = c(0, 1),
        type = "l"
    )
    prevelance_with_net <- sum(adm1$prev)
    adm1_switching_to_PBO <- run_model(
        init_EIR = eir,
        country = "Ghana",
        admin2 = old_province,
        time = 365 * 3 + 200,
        num_int = 3,
        itn_cov = itn_cov,
        irs_cov = irs_cov,
        d_ITN0 = d_PBO_0,
        r_ITN0 = r_PBO_0,
        # r_ITN1 = r_PBO_1,
        # itn_half_life = half_life_pbo,
        ITN_IRS_on = 200,
        init_ft = treatment_seeking
    )
    plot(adm1_switching_to_PBO$t,
        adm1_switching_to_PBO$prev,
        main = paste("Prevalance Switching to PBO -", province),
        ylim = c(0, 1),
        type = "l"
    )
    prevelance_switching_pbo <- sum(adm1_switching_to_PBO$prev)

    adm1_switching_to_PBO_same_budget <- run_model(
        init_EIR = eir,
        country = "Ghana",
        admin2 = old_province,
        time = 365 * 3 + 200,
        num_int = 3,
        itn_cov = pbo_cov,
        irs_cov = irs_cov,
        d_ITN0 = d_PBO_0,
        r_ITN0 = r_PBO_0,
        # r_ITN1 = r_PBO_1,
        # itn_half_life = half_life_pbo,
        ITN_IRS_on = 200,
        init_ft = treatment_seeking
    )
    plot(adm1_switching_to_PBO_same_budget$t,
        adm1_switching_to_PBO_same_budget$prev,
        main = paste("Prevalance Switching to PBO SAME budget -", province),
        ylim = c(0, 1),
        type = "l"
    )
    prevelance_switching_pbo_same_budget <-
        sum(adm1_switching_to_PBO_same_budget$prev)

    print("different with/without net:")
    print(prevelance_without_net - prevelance_with_net)
    print("different with/without PBO:")
    print(prevelance_without_net - prevelance_switching_pbo)
    n_reduced_cases_net <- total_population *
        (prevelance_without_net - prevelance_with_net)
    n_reduced_cases_pbo <- total_population *
        (prevelance_without_net - prevelance_switching_pbo)
    n_reduced_cases_pbo_same_budget <- total_population *
        (prevelance_without_net - prevelance_switching_pbo_same_budget)
    print("Reduced cases with nets")
    print(n_reduced_cases_net)
    print("Reduced cases with PBO")
    print(n_reduced_cases_pbo)
    print("Reduced cases with PBO - Same budget as LLINs")
    print(n_reduced_cases_pbo_same_budget)
    price_with_net <- llins_distributed * 2.17
    price_with_pbo <- llins_distributed * 3.09
    print("price with net")
    print(price_with_net)
    print("price with pbo")
    print(price_with_pbo)
    print("$ per averted cases with net")
    print(price_with_net / n_reduced_cases_net)
    print("$ per averted cases with pbo")
    print(price_with_pbo / n_reduced_cases_pbo)
}