
get_hut_trail_outcome_by_resistance <- function(r) {
    itn_pbo_params <-
        read.csv(
            here(
                "github",
                "Mosquito-Net-Parameters", "estimates",
                "best_params_from_systematic_review1.csv"
            )
        )
    g2_params <-
        read.csv(here(
            "github",
            "Mosquito-Net-Parameters",
            "estimates", "g2_itn.csv"
        ))
    r <- round(r, 2)
    itn_pbo_params_by_resistance <-
        subset(itn_pbo_params, resistance == r)
    bioassay_mortality_by_resistance <- round(1 - r, 10)
    g2_params_by_resistance <-
        subset(
            g2_params,
            bioassay_mortality == bioassay_mortality_by_resistance
        )
    d_itn <- itn_pbo_params_by_resistance$d10
    d_pbo <- itn_pbo_params_by_resistance$d20
    d_g2 <- g2_params_by_resistance$dn0_med
    r_itn <- itn_pbo_params_by_resistance$r10
    r_pbo <- itn_pbo_params_by_resistance$r20
    r_g2 <- g2_params_by_resistance$rn0_med
    h_itn <- itn_pbo_params_by_resistance$h10 * 365
    h_pbo <- itn_pbo_params_by_resistance$h20 * 365
    h_g2 <- g2_params_by_resistance$gamman_med * 365

    return(
        data.frame(d_itn, r_itn, h_itn, d_pbo, r_pbo, h_pbo, d_g2, r_g2, h_g2)
    )
}