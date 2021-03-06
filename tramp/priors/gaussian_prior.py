import numpy as np
from .base_prior import Prior
from ..utils.integration import gaussian_measure


class GaussianPrior(Prior):
    def __init__(self, size, mean=0, var=1):
        self.size = size
        self.mean = mean
        self.var = var
        self.repr_init()
        self.sigma = np.sqrt(var)
        self.a = 1 / var
        self.b = mean / var

    def sample(self):
        X = self.mean + self.sigma * np.random.standard_normal(self.size)
        return X

    def math(self):
        return r"$\mathcal{N}$"

    def second_moment(self):
        return self.mean**2 + self.var

    def compute_forward_posterior(self, ax, bx):
        a = ax + self.a
        b = bx + self.b
        rx = b / a
        vx = 1 / a
        return rx, vx

    def compute_forward_error(self, ax):
        a = ax + self.a
        vx = 1 / a
        return vx

    def compute_forward_message(self, ax, bx):
        ax_new = self.a
        bx_new = self.b * np.ones_like(bx)
        return ax_new, bx_new

    def compute_forward_state_evolution(self, ax):
        ax_new = self.a
        return ax_new

    def measure(self, f):
        return gaussian_measure(self.mean, self.sigma, f)

    def compute_log_partition(self, ax, bx):
        a = ax + self.a
        b = bx + self.b
        logZ = 0.5 * np.sum(
            b**2 / a - self.b**2 / self.a + np.log(self.a/a)
        )
        return logZ

    def compute_mutual_information(self, ax):
        a = ax + self.a
        I = 0.5*np.log(a*self.var)
        return I

    def compute_free_energy(self, ax):
        tau_x = self.second_moment()
        I = self.compute_mutual_information(ax)
        A = 0.5*ax*tau_x - I
        return A
