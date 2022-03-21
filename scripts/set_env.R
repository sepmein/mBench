registerDoParallel(detectCores())
if (.Platform$OS.type == "unix") {
    dir <- "/Users/sepmein/Dropbox/benchmarking/"
} else {
    dir <- "C:\\Users\\zhangc\\Dropbox\\benchmarking\\"
}

setwd(dir)

gha_params <-
    read.csv(here("Data", "GHA", "gha.csv"))
