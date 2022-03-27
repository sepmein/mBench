library("here")

registerDoParallel(detectCores())
if (.Platform$OS.type == "unix") {
    dir <- "/Users/sepmein/Dropbox/benchmarking/"
} else {
    dir <- "C:\\Users\\zhangc\\Dropbox\\benchmarking\\"
}

if (Sys.info()["nodename"] == "PowerHouse") {
    dir <- "/mnt/d/Dropbox/benchmarking"
}

setwd(dir)

gha_params <-
    read.csv(here("Data", "GHA", "gha.csv"))