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
#for (row in 1:nrow(gha_params)) {
    row <- 1
    eta <- gha_params[row, "eta"]
    rho <- gha_params[row, "rho"]
    eir <- gha_params[row, "eir"]
    province <- gha_params[row, "adm1"]
    old_province <- gha_params[row, "old_district_name"]
    # province <- gha_params[row, "adm1"]
    itn_cov <- gha_params[row, "itn_cov"]
    irs_cov <- gha_params[row, "irs_cov"]
    treatment_seeking <- gha_params[row, "treatment_seeking"]
    d_ITN_0 <- gha_params[row, "d_ITN_0"]
    d_PBO_0 <- gha_params[row, "d_PBO_0"]
    r_ITN_0 <- gha_params[row, "r_ITN_0"] # nolint
    r_PBO_0 <- gha_params[row, "r_PBO_0"]
    r_ITN_1 <- gha_params[row, "r_ITN_1"]
    r_PBO_1 <- gha_params[row, "r_PBO_1"]
    print(d_ITN_0)
    print(d_PBO_0)
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
        r_ITN1 = r_ITN_1,
        ITN_IRS_on = 200,
        init_ft = treatment_seeking
    )
    plot(adm1$t,
        adm1$prev,
        main = paste("Prevalance With LLINs -", province),
        ylim = c(0, 1),
        type = "l"
    )
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
        r_ITN1 = r_PBO_1,
        ITN_IRS_on = 200,
        init_ft = treatment_seeking
    )
    plot(adm1_switching_to_PBO$t,
        adm1_switching_to_PBO$prev,
        main = paste("Prevalance Switching to PBO -", province),
        ylim = c(0, 1),
        type = "l"
    )
}
