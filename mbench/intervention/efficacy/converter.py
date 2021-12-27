import math

from scipy.special import expit

half_life_itn = 365


def bioassay_to_rds(mortality_pyrethroid_bioassay, species='gambiae'):
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

    # from pyrethroid mortality in bioassay compute mortality in PBO bioassay
    mortality_pbo_bioassay = expit(
        beta1 + beta2 * (mortality_pyrethroid_bioassay - tao) / (1 + beta3 * (mortality_pyrethroid_bioassay - tao)))

    print('mortality regular bioassay:', "{:10.2f}".format(mortality_pyrethroid_bioassay))
    print('mortality pbo bioassay :', "{:10.2f}".format(mortality_pbo_bioassay))
    # from mortality in PBO bioassay to mortality in PBO hut trail
    mortality_PBO_hut_trail = mortality_bioassay_to_hut_trail(mortality_pbo_bioassay)

    print('mortality regular hut:', "{:10.2f}".format(mortality_pyrethroid_hut_trail))
    print('mortality pbo hut:', "{:10.2f}".format(mortality_PBO_hut_trail))

    # m_p
    # from mortality to number of mosquitoes entering hut
    def ratio_of_mosquitoes_entering_hut_to_without_net(mortality_hut_trail):
        return 1 - (
                delta1 +
                delta2 * (mortality_hut_trail - tao) +
                delta3 * (mortality_hut_trail - tao) * (mortality_hut_trail - tao)
        )

    p_entering_regular = ratio_of_mosquitoes_entering_hut_to_without_net(mortality_pyrethroid_hut_trail)
    p_entering_PBO = ratio_of_mosquitoes_entering_hut_to_without_net(mortality_PBO_hut_trail)
    print('p_enter_regular', "{:10.2f}".format(p_entering_regular))
    print('p_enter_PBO', "{:10.2f}".format(p_entering_PBO))


    # k_p
    def proportion_of_mosquitoes_successfully_feed_upon_entering(mortality_hut_trail):
        return theta1 * math.exp(theta2 * (1 - mortality_hut_trail - tao))

    p_feed_regular = proportion_of_mosquitoes_successfully_feed_upon_entering(mortality_pyrethroid_hut_trail)
    p_feed_PBO = proportion_of_mosquitoes_successfully_feed_upon_entering(mortality_PBO_hut_trail)

    # j_p
    def proportion_of_mosquitoes_exiting_without_feeding(p_mortality, p_feed):
        return 1 - p_mortality - p_feed

    p_exiting_regular = proportion_of_mosquitoes_exiting_without_feeding(mortality_pyrethroid_hut_trail, p_feed_regular)
    p_exiting_PBO = proportion_of_mosquitoes_exiting_without_feeding(mortality_PBO_hut_trail, p_feed_PBO)

    # j_p'
    def proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(p_entering, p_exit):
        return p_entering * p_exit + (1 - p_entering)

    p_exit_with_deterrence_regular = proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(
        p_entering_regular, p_exiting_regular
    )
    p_exit_with_deterrence_PBO = proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(
        p_entering_PBO, p_exiting_PBO
    )

    # k_p'
    def proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(p_entering, p_feed):
        return p_entering * p_feed

    p_feed_with_deterrence_regular = proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(
        p_entering_regular,
        p_feed_regular
    )
    p_feed_with_deterrence_PBO = proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(
        p_entering_PBO,
        p_feed_PBO
    )

    # l_p'
    def proportion_of_mosquitoes_dead_accounting_deterrence(p_entering, p_death):
        return p_entering * p_death

    mortality_pyrethroid_hut_trail_with_deterrence = proportion_of_mosquitoes_dead_accounting_deterrence(
        p_entering_regular,
        mortality_pyrethroid_hut_trail
    )
    mortality_PBO_hut_trail_with_deterrence = proportion_of_mosquitoes_dead_accounting_deterrence(
        p_entering_PBO,
        mortality_PBO_hut_trail
    )

    # r_p_0
    k_0 = 0.7

    def repeating(k_p_d, j_p_d, l_p_d, k_0=k_0):
        return (1 - k_p_d / k_0) * (j_p_d / (j_p_d + l_p_d))

    repeating_regular = repeating(
        k_p_d=p_feed_with_deterrence_regular,
        j_p_d=p_exit_with_deterrence_regular,
        l_p_d=mortality_pyrethroid_hut_trail_with_deterrence
    )
    repeating_PBO = repeating(
        k_p_d=p_feed_with_deterrence_PBO,
        j_p_d=p_exit_with_deterrence_PBO,
        l_p_d=mortality_PBO_hut_trail_with_deterrence
    )

    # d_p_0
    def dying(k_p_d, j_p_d, l_p_d):
        return (1 - k_p_d / k_0) * (l_p_d / (j_p_d + l_p_d))

    dying_regular = dying(k_p_d=p_feed_with_deterrence_regular,
                          j_p_d=p_exit_with_deterrence_regular,
                          l_p_d=mortality_pyrethroid_hut_trail_with_deterrence
                          )
    dying_PBO = dying(k_p_d=p_feed_with_deterrence_PBO,
                      j_p_d=p_exit_with_deterrence_PBO,
                      l_p_d=mortality_PBO_hut_trail_with_deterrence
                      )

    # s_p_0
    def feeding(k_p_d):
        return k_p_d / k_0

    feeding_regular = feeding(
        k_p_d=p_feed_with_deterrence_regular
    )
    feeding_PBO = feeding(k_p_d=p_feed_with_deterrence_PBO)

    # decay rate
    # decay parameter rho_p
    def gamma_p(mortality_hut_trail):
        return expit(mu_p + rho_p * (mortality_hut_trail - tao))

    gamma_p_regular = gamma_p(mortality_pyrethroid_hut_trail)
    gamma_p_PBO = gamma_p(mortality_PBO_hut_trail)

    r_m = 0.25

    # r_p repeat rate with decay
    def r_p(r_p_0, gamma_p):
        # suppose life years of itn is 3 year, remind to change this if using other parameters
        return (r_p_0 - r_m) * math.exp(-1 * gamma_p * half_life_itn) + r_m

    repeating_regular_with_decay = r_p(repeating_regular, gamma_p_regular)
    repeating_PBO_with_decay = r_p(repeating_PBO, gamma_p_PBO)

    rds_regular = (repeating_regular, repeating_regular_with_decay, dying_regular, feeding_regular)
    rds_PBO = (repeating_PBO, repeating_PBO_with_decay, dying_PBO, feeding_PBO)
    return rds_regular, rds_PBO
