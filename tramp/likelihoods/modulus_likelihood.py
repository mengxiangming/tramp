import numpy as np
from scipy.special import ive
from scipy.integrate import quad
from .base_likelihood import Likelihood
from ..utils.integration import gaussian_measure_2d, gaussian_measure
from ..utils.misc import relu, complex2array, array2complex


def ive_ratio(r):
    """Returns I(r) = ive(1, r) / ive(0, r)

    Notes
    -----
    - I(r) ~ 1 for r >> 1
    """
    cutoff = 1e9
    I = np.ones_like(r)
    ind = (r < cutoff)
    I[ind] = ive(1, r[ind]) / ive(0, r[ind])
    return I


class ModulusLikelihood(Likelihood):
    """Modulus likelihood y = |z|.

    Parameters
    ----------
    - y: array
        observed modulus
    - y_name: str
        name of y for display

    Notes
    -----
    For message passing it is more convenient to represent a complex array x
    as a real array X where X[0] = x.real and X[1] = x.imag

    In particular:
    - input  of sample(): Z array of shape (2, z.shape)
    - message bz, posterior rz: real arrays of shape (2, z.shape)
    """

    def __init__(self, y, y_name="y"):
        self.y_name = y_name
        self.size = self.get_size(y)
        self.repr_init()
        self.y = y

    def sample(self, Z):
        "We assume Z[0] = Z.real and Z[1] = Z.imag"
        Z = array2complex(Z)
        return np.absolute(Z)

    def math(self):
        return r"$|\cdot|$"

    def compute_backward_posterior(self, az, bz, y):
        bz = array2complex(bz)
        b = np.absolute(bz)
        I = ive_ratio(b*y)
        b_normed = np.zeros_like(bz)
        nonzero = (b != 0)
        b_normed[nonzero] = bz[nonzero]/b[nonzero]
        rz = b_normed * y * I
        v = 0.5 * (y**2) * (1 - I**2)
        vz = np.mean(v)
        rz = complex2array(rz)
        return rz, vz

    def beliefs_measure(self, az, tau_z, f):
        u_eff = np.maximum(0, az * tau_z - 1)
        # handling special case az * tau_z = 1 (no integration over b)
        if u_eff == 0:
            def f_scaled_y(xi_y):
                y = xi_y / np.sqrt(az)
                coef_y = np.sqrt(2 * np.pi * az)
                bz = complex2array(np.array(0))
                return coef_y * relu(y) * f(bz, y)
            return gaussian_measure(0, 1, f_scaled_y)
        # typical case u_eff > 0
        sz_eff = np.sqrt(az * u_eff)

        def f_scaled(xi_b, xi_y):
            b = sz_eff * xi_b
            y = b / az + xi_y / np.sqrt(az)
            coef = 2 * np.pi / np.sqrt(u_eff)
            bz = complex2array(np.array(b))
            return coef * relu(b) * relu(y) * ive(0, b * y) * f(bz, y)
        return gaussian_measure_2d(0, 1, 0, 1, f_scaled)

    def measure(self, y, f):
        def polar_f(theta):
            return y * f(y * np.exp(theta * 1j))
        return quad(polar_f, 0, 2 * np.pi)[0]

    def compute_log_partition(self, az, bz, y):
        b = np.absolute(bz)
        I0 = ive(0, b*y)
        logZ = np.sum(
            -0.5*az*(y**2) + np.log(2*np.pi*y*ive(0, b*y)) + b*y
        )
        return logZ
