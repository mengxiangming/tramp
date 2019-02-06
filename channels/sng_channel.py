import numpy as np
from ..base import Channel
from ..utils.integration import gaussian_measure_2d
from ..utils.misc import norm_cdf, phi_1, phi_2, sigmoid
from scipy.integrate import quad


class SngChannel(Channel):
    def __init__(self):
        self.repr_init()

    def sample(self, Z):
        X = np.sign(Z)
        return X

    def math(self):
        return r"$\mathrm{sng}$"

    def second_moment(self, tau):
        return 1.

    def compute_forward_posterior(self, az, bz, ax, bx):
        # estimate x from x = sng(z)
        x_pos = + bz / np.sqrt(az)
        x_neg = - bz / np.sqrt(az)
        p_pos = norm_cdf(x_pos)
        p_neg = norm_cdf(x_neg)
        eta = bx + 0.5 * np.log(p_pos / p_neg)
        rx = np.tanh(eta)
        v = 1 - rx**2
        vx = np.mean(v)
        return rx, vx

    def compute_backward_posterior(self, az, bz, ax, bx):
        # estimate z from x = sng(z)
        x_pos = + bz / np.sqrt(az)
        x_neg = - bz / np.sqrt(az)
        p_pos = norm_cdf(x_pos)
        p_neg = norm_cdf(x_neg)
        delta = 2 * bx + np.log(p_pos / p_neg)
        sigma_pos = sigmoid(+delta)
        sigma_neg = sigmoid(-delta)
        r_pos = + phi_1(x_pos) / np.sqrt(az) # NB: + phi'(x_pos)
        r_neg = - phi_1(x_neg) / np.sqrt(az) # NB: + phi'(x_pos)
        v_pos = phi_2(x_pos) / az
        v_neg = phi_2(x_neg) / az
        rz = sigma_pos * r_pos + sigma_neg * r_neg
        Dz = (r_pos - r_neg)**2
        v = sigma_pos * sigma_neg * Dz + sigma_pos * v_pos + sigma_neg * v_neg
        vz = np.mean(v)
        return rz, vz

    def beliefs_measure(self, az, ax, tau, f):
        u_eff = np.maximum(0, az * tau - 1)
        s_eff = np.sqrt(az * u_eff)

        def f_pos(bz, bx):
            x_pos = + bz / np.sqrt(az)
            return norm_cdf(x_pos) * f(bz, bx)

        def f_neg(bz, bx):
            x_neg = - bz / np.sqrt(az)
            return norm_cdf(x_neg) * f(bz, bx)

        mu_pos = gaussian_measure_2d(0, s_eff, +ax, np.sqrt(ax), f_pos)
        mu_neg = gaussian_measure_2d(0, s_eff, -ax, np.sqrt(ax), f_neg)
        return mu_pos + mu_neg

    def measure(self, f, zmin, zmax):
        def integrand(z):
            return f(z, np.sign(z))
        return quad(integrand, zmin, zmax)[0]
