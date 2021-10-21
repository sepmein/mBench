library(ICDMM,
    help,
    pos = 2, lib.loc = NULL
)
params <-
    model_param_list_create()
params$eta <- 1 / (21.2 * 365)
params$init_EIR <- 1280 # nolint
ghana <- run_model()
plot(ghana$t, ghana$prev, main = "Prevalance", ylim = c(0, 1), type = "l")

# seasonal data
# resource: 
