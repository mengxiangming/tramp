import numpy as np
from scipy.special import erf, erfcx
import warnings


def relu(x):
    return np.maximum(0, x)

def norm_cdf(x):
    "Computes Phi(x)"
    return 0.5*(1 + erf(x / np.sqrt(2)))

def log_norm_cdf_prime(x):
    "Computes (log Phi)'(x) = N(x)/Phi(x)"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        d = np.sqrt(2 * np.pi) * 0.5 * erfcx(-x / np.sqrt(2))
    return 1./d

def phi_0(x):
    "Computes phi(x) = x**2 / 2 + log Phi"
    return 0.5 * (x**2) + np.log(norm_cdf(x))

def phi_1(x):
    "Computes phi'(x) = x + N/Phi"
    y = log_norm_cdf_prime(x)
    return x + y

def phi_2(x):
    "Computes phi''(x) = 1 - N/Phi * (x + N/Phi)"
    y = log_norm_cdf_prime(x)
    return 1 - y * (x + y)

def sigmoid(x):
    return 1/ (1 + np.exp(-x))