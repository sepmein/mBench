library(ICDMM,
    help,
    pos = 2, lib.loc = NULL
)
# seasonal data
# resource:
library(gdata)

gha_params <- read.csv("./Data/GHA/gha.csv")
gha_params$adm1
for (row in 1:nrow(gha_params)) {
    eta <- gha_params[row, "eta"]
    rho <- gha_params[row, "rho"]
    eir <- gha_params[row, "eir"]
    province <- gha_params[row, "adm1"]
    itn_cov <- gha_params[row, 'itn_cov']
    irs_cov <- gha_params[row, 'irs_cov']
    treatment_seeking <- gha_params[row, "treatment_seeking"]
    # TODO
    adm1 <- run_model(
        init_EIR = eir,
        country = "Ghana",
        admin2 = province,
        time = 365 * 3,
        num_int = 2,
        itn_cov = itn_cov,
        irs_cov = irs_cov,
        ITN_IRS_on = 200,
        init_ft = treatment_seeking
    )
    plot(adm1$t,
        adm1$prev,
        main = "Prevalance",
        ylim = c(0, 1),
        type = "l"
    )
}