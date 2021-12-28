# Churcher, T. S., Lissenden, N., Griffin, J. T., Worrall, E., & Ranson, H. (2016). The impact of pyrethroid
# resistance on the efficacy and effectiveness of bednets for malaria control in Africa. ELife, 5(AUGUST),
# 1–26. https://doi.org/10.7554/eLife.16090.001

import math

from scipy.special import expit

half_life_itn = 365 * 2.65


def bioassay_to_rds(mortality_pyrethroid_bioassay, species='gambiae', verbose=0):
    # proportion mosquitoes dying in a discriminating dose pyrethroid bioassay
    # mortality_pyrethroid_bioassay

    if species == 'funestus':
        beta1 = 2.53
        beta2 = 0.89
        beta3 = 0.78
    else:
        beta1 = 3.41
        beta2 = 5.88
        beta3 = 0.78

    delta1 = 0.071
    delta2 = 1.26
    delta3 = 1.52

    # formula 1
    alpha1 = .63
    alpha2 = 4.0

    # equation 11
    theta1 = 0.02
    theta2 = 3.32

    # formula 4
    tao = 0.5

    # decay parameters
    mu_p = -2.36
    rho_p = -3.05

    def mortality_bioassay_to_hut_trail(mortality_bioassay):
        return expit(alpha1 + alpha2 * (mortality_bioassay - tao))

    # from pyrethroid mortality in bioassay compute mortality in pyrethroid hut trail using eq 4
    mortality_pyrethroid_hut_trail = mortality_bioassay_to_hut_trail(mortality_pyrethroid_bioassay)

    # from pyrethroid mortality in bioassay compute mortality in pbo bioassay
    mortality_pbo_bioassay = expit(
        beta1 + beta2 * (mortality_pyrethroid_bioassay - tao) / (1 + beta3 * (mortality_pyrethroid_bioassay - tao)))

    # from mortality in pbo bioassay to mortality in pbo hut trail
    mortality_pbo_hut_trail = mortality_bioassay_to_hut_trail(mortality_pbo_bioassay)

    # m_p
    # from mortality to number of mosquitoes entering hut
    def ratio_of_mosquitoes_entering_hut_to_without_net(mortality_hut_trail):
        return 1 - (
                delta1 +
                delta2 * (mortality_hut_trail - tao) +
                delta3 * (mortality_hut_trail - tao) * (mortality_hut_trail - tao)
        )

    p_entering_regular = ratio_of_mosquitoes_entering_hut_to_without_net(mortality_pyrethroid_hut_trail)
    p_entering_pbo = ratio_of_mosquitoes_entering_hut_to_without_net(mortality_pbo_hut_trail)

    # k_p
    def proportion_of_mosquitoes_successfully_feed_upon_entering(mortality_hut_trail):
        return theta1 * math.exp(theta2 * (1 - mortality_hut_trail - tao))

    p_feed_regular = proportion_of_mosquitoes_successfully_feed_upon_entering(mortality_pyrethroid_hut_trail)
    p_feed_pbo = proportion_of_mosquitoes_successfully_feed_upon_entering(mortality_pbo_hut_trail)

    # j_p
    def proportion_of_mosquitoes_exiting_without_feeding(p_mortality, p_feed):
        return 1 - p_mortality - p_feed

    p_exiting_regular = proportion_of_mosquitoes_exiting_without_feeding(mortality_pyrethroid_hut_trail, p_feed_regular)
    p_exiting_pbo = proportion_of_mosquitoes_exiting_without_feeding(mortality_pbo_hut_trail, p_feed_pbo)

    # j_p'
    def proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(p_entering, p_exit):
        return p_entering * p_exit + (1 - p_entering)

    p_exit_with_deterrence_regular = \
        proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(
            p_entering_regular, p_exiting_regular
        )
    p_exit_with_deterrence_pbo = proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(
        p_entering_pbo, p_exiting_pbo
    )

    # k_p'
    def proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(p_entering, p_feed):
        return p_entering * p_feed

    p_feed_with_deterrence_regular = proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(
        p_entering_regular,
        p_feed_regular
    )
    p_feed_with_deterrence_pbo = proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(
        p_entering_pbo,
        p_feed_pbo
    )

    # l_p'
    def proportion_of_mosquitoes_dead_accounting_deterrence(p_entering, p_death):
        return p_entering * p_death

    mortality_pyrethroid_hut_trail_with_deterrence = proportion_of_mosquitoes_dead_accounting_deterrence(
        p_entering_regular,
        mortality_pyrethroid_hut_trail
    )
    mortality_pbo_hut_trail_with_deterrence = proportion_of_mosquitoes_dead_accounting_deterrence(
        p_entering_pbo,
        mortality_pbo_hut_trail
    )

    # r_p_0
    k_0 = 0.7

    def repeating(k_p_d, j_p_d, l_p_d):
        return (1 - k_p_d / k_0) * (j_p_d / (j_p_d + l_p_d))

    repeating_regular = repeating(
        k_p_d=p_feed_with_deterrence_regular,
        j_p_d=p_exit_with_deterrence_regular,
        l_p_d=mortality_pyrethroid_hut_trail_with_deterrence
    )
    repeating_pbo = repeating(
        k_p_d=p_feed_with_deterrence_pbo,
        j_p_d=p_exit_with_deterrence_pbo,
        l_p_d=mortality_pbo_hut_trail_with_deterrence
    )

    # d_p_0
    def dying(k_p_d, j_p_d, l_p_d):
        return (1 - k_p_d / k_0) * (l_p_d / (j_p_d + l_p_d))

    dying_regular = dying(k_p_d=p_feed_with_deterrence_regular,
                          j_p_d=p_exit_with_deterrence_regular,
                          l_p_d=mortality_pyrethroid_hut_trail_with_deterrence
                          )
    dying_pbo = dying(k_p_d=p_feed_with_deterrence_pbo,
                      j_p_d=p_exit_with_deterrence_pbo,
                      l_p_d=mortality_pbo_hut_trail_with_deterrence
                      )

    # s_p_0
    def feeding(k_p_d):
        return k_p_d / k_0

    feeding_regular = feeding(
        k_p_d=p_feed_with_deterrence_regular
    )
    feeding_pbo = feeding(k_p_d=p_feed_with_deterrence_pbo)

    # decay rate
    # decay parameter rho_p
    def gamma_p(mortality_hut_trail):
        return expit(mu_p + rho_p * (mortality_hut_trail - tao))

    gamma_p_regular = gamma_p(mortality_pyrethroid_hut_trail)
    gamma_p_pbo = gamma_p(mortality_pbo_hut_trail)

    r_m = 0.24

    # r_p repeat rate with decay
    def r_p(r_p_0, gamma_p_):
        # suppose life years of itn is 3 year, remind to change this if using other parameters
        return (r_p_0 - r_m) * math.exp(-1 * gamma_p_ * half_life_itn) + r_m

    repeating_regular_with_decay = r_p(repeating_regular, gamma_p_regular)
    repeating_pbo_with_decay = r_p(repeating_pbo, gamma_p_pbo)

    rds_regular = (
        repeating_regular,
        repeating_regular_with_decay,
        dying_regular,
        feeding_regular
    )
    pyrethroid_outputs = (
        mortality_pyrethroid_bioassay,
        mortality_pyrethroid_hut_trail,
        p_entering_regular,
        p_feed_regular,
        p_exiting_regular,
        p_exit_with_deterrence_regular,
        p_feed_with_deterrence_regular,
        mortality_pyrethroid_hut_trail_with_deterrence,
    )
    rds_pbo = (
        repeating_pbo,
        repeating_pbo_with_decay,
        dying_pbo,
        feeding_pbo
    )
    pbo_outputs = (
        mortality_pbo_bioassay,
        mortality_pbo_hut_trail,
        p_entering_pbo,
        p_feed_pbo,
        p_exiting_pbo,
        p_exit_with_deterrence_pbo,
        p_feed_with_deterrence_pbo,
        mortality_pbo_hut_trail_with_deterrence,
    )
    if verbose == 1:
        return rds_regular, rds_pbo, pyrethroid_outputs, pbo_outputs
    elif verbose == 0:
        return rds_regular, rds_pbo
