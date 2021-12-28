# Churcher, T. S., Lissenden, N., Griffin, J. T., Worrall, E., & Ranson, H. (2016). The impact of pyrethroid
# resistance on the efficacy and effectiveness of bednets for malaria control in Africa. ELife, 5(AUGUST),
# 1–26. https://doi.org/10.7554/eLife.16090.001

import math

from scipy.special import expit


class Converter:
    def __init__(self,
                 species='gambiae',
                 verbose=False
                 ):
        self.half_life_itn = 365 * 2.65
        self.species = ''
        self.verbose = verbose

        if species == 'funestus':
            self.beta1 = 2.53
            self.beta2 = 0.89
            self.beta3 = 0.78
        else:
            self.beta1 = 3.41
            self.beta2 = 5.88
            self.beta3 = 0.78

        self.delta1 = 0.071
        self.delta2 = 1.26
        self.delta3 = 1.52

        # formula 1
        self.alpha1 = .63
        self.alpha2 = 4.0

        # equation 11
        self.theta1 = 0.02
        self.theta2 = 3.32

        # formula 4
        self.tao = 0.5

        # decay parameters
        self.mu_p = -2.36
        self.rho_p = -3.05

        # k_0
        self.k_0 = 0.7

        self.r_m = 0.24

    def mortality_bioassay_to_hut_trail(self, mortality_bioassay):
        return expit(self.alpha1 + self.alpha2 * (mortality_bioassay - self.tao))

    def ratio_of_mosquitoes_entering_hut_to_without_net(self, mortality_hut_trail):
        return 1 - (
                self.delta1 +
                self.delta2 * (mortality_hut_trail - self.tao) +
                self.delta3 * (mortality_hut_trail - self.tao) * (mortality_hut_trail - self.tao)
        )

    def proportion_of_mosquitoes_successfully_feed_upon_entering(self, mortality_hut_trail):
        return self.theta1 * math.exp(self.theta2 * (1 - mortality_hut_trail - self.tao))

    @staticmethod
    def proportion_of_mosquitoes_exiting_without_feeding(p_mortality, p_feed):
        return 1 - p_mortality - p_feed

    @staticmethod
    def proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(p_entering, p_exit):
        return p_entering * p_exit + (1 - p_entering)

    @staticmethod
    def proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(p_entering, p_feed):
        return p_entering * p_feed

    @staticmethod
    def proportion_of_mosquitoes_dead_accounting_deterrence(p_entering, p_death):
        return p_entering * p_death

    def repeating(self, k_p_d, j_p_d, l_p_d):
        return (1 - k_p_d / self.k_0) * (j_p_d / (j_p_d + l_p_d))

    def dying(self, k_p_d, j_p_d, l_p_d):
        return (1 - k_p_d / self.k_0) * (l_p_d / (j_p_d + l_p_d))

    def feeding(self, k_p_d):
        return k_p_d / self.k_0

    def gamma_p(self, mortality_hut_trail):
        return expit(self.mu_p + self.rho_p * (mortality_hut_trail - self.tao))

    def r_p(self, r_p_0, gamma_p_):
        # suppose life years of itn is 3 year, remind to change this if using other parameters
        return (r_p_0 - self.r_m) * math.exp(-1 * gamma_p_ * self.half_life_itn) + self.r_m

    def bioassay_to_rds(self, mortality_pyrethroid_bioassay):
        # proportion mosquitoes dying in a discriminating dose pyrethroid bioassay
        # mortality_pyrethroid_bioassay

        # from pyrethroid mortality in bioassay compute mortality in pyrethroid hut trail using eq 4
        mortality_pyrethroid_hut_trail = self.mortality_bioassay_to_hut_trail(mortality_pyrethroid_bioassay)

        # from pyrethroid mortality in bioassay compute mortality in pbo bioassay
        mortality_pbo_bioassay = expit(
            self.beta1 + self.beta2 * (mortality_pyrethroid_bioassay - self.tao) / (
                    1 + self.beta3 * (mortality_pyrethroid_bioassay - self.tao)))

        # from mortality in pbo bioassay to mortality in pbo hut trail
        mortality_pbo_hut_trail = self.mortality_bioassay_to_hut_trail(mortality_pbo_bioassay)

        # m_p
        # from mortality to number of mosquitoes entering hut
        p_entering_regular = self.ratio_of_mosquitoes_entering_hut_to_without_net(mortality_pyrethroid_hut_trail)
        p_entering_pbo = self.ratio_of_mosquitoes_entering_hut_to_without_net(mortality_pbo_hut_trail)

        # k_p
        p_feed_regular = self.proportion_of_mosquitoes_successfully_feed_upon_entering(mortality_pyrethroid_hut_trail)
        p_feed_pbo = self.proportion_of_mosquitoes_successfully_feed_upon_entering(mortality_pbo_hut_trail)

        # j_p
        p_exiting_regular = self.proportion_of_mosquitoes_exiting_without_feeding(mortality_pyrethroid_hut_trail,
                                                                                  p_feed_regular)
        p_exiting_pbo = self.proportion_of_mosquitoes_exiting_without_feeding(mortality_pbo_hut_trail, p_feed_pbo)

        # j_p'

        p_exit_with_deterrence_regular = \
            self.proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(
                p_entering_regular, p_exiting_regular
            )
        p_exit_with_deterrence_pbo = \
            self.proportion_of_mosquitoes_entering_hut_exiting_without_feeding_accounting_deterrence(
                p_entering_pbo, p_exiting_pbo
            )

        # k_p'

        p_feed_with_deterrence_regular = \
            self.proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(
                p_entering_regular,
                p_feed_regular
            )
        p_feed_with_deterrence_pbo = \
            self.proportion_of_mosquitoes_successfully_feed_upon_entering_accounting_deterrence(
                p_entering_pbo,
                p_feed_pbo
            )

        # l_p'
        mortality_pyrethroid_hut_trail_with_deterrence = self.proportion_of_mosquitoes_dead_accounting_deterrence(
            p_entering_regular,
            mortality_pyrethroid_hut_trail
        )

        mortality_pbo_hut_trail_with_deterrence = self.proportion_of_mosquitoes_dead_accounting_deterrence(
            p_entering_pbo,
            mortality_pbo_hut_trail
        )

        # r_p_0

        repeating_regular = self.repeating(
            k_p_d=p_feed_with_deterrence_regular,
            j_p_d=p_exit_with_deterrence_regular,
            l_p_d=mortality_pyrethroid_hut_trail_with_deterrence
        )
        repeating_pbo = self.repeating(
            k_p_d=p_feed_with_deterrence_pbo,
            j_p_d=p_exit_with_deterrence_pbo,
            l_p_d=mortality_pbo_hut_trail_with_deterrence
        )

        # d_p_0

        dying_regular = self.dying(k_p_d=p_feed_with_deterrence_regular,
                                   j_p_d=p_exit_with_deterrence_regular,
                                   l_p_d=mortality_pyrethroid_hut_trail_with_deterrence
                                   )
        dying_pbo = self.dying(k_p_d=p_feed_with_deterrence_pbo,
                               j_p_d=p_exit_with_deterrence_pbo,
                               l_p_d=mortality_pbo_hut_trail_with_deterrence
                               )

        # s_p_0
        feeding_regular = self.feeding(
            k_p_d=p_feed_with_deterrence_regular
        )
        feeding_pbo = self.feeding(k_p_d=p_feed_with_deterrence_pbo)

        # decay rate
        # decay parameter rho_p

        gamma_p_regular = self.gamma_p(mortality_pyrethroid_hut_trail)
        gamma_p_pbo = self.gamma_p(mortality_pbo_hut_trail)

        # r_p repeat rate with decay
        repeating_regular_with_decay = self.r_p(repeating_regular, gamma_p_regular)
        repeating_pbo_with_decay = self.r_p(repeating_pbo, gamma_p_pbo)

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
        if self.verbose:
            return rds_regular, rds_pbo, pyrethroid_outputs, pbo_outputs
        else:
            return rds_regular, rds_pbo
