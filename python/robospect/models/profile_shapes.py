#
# This file is part of robospect.py.
#
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import numpy as np
import scipy as sp
import robospect.spectra as spectra

__all__ = ['profileFromName', 'profile', 'gaussian', 'voigt', 'lorentzian', 'planck', 'skewgauss']

def profileFromName(name):
    r"""Convert name of profile to a profile class.

    Parameters
    ----------
    name : `str`
        name of profile to select

    Returns
    -------
    profile : `robospect.models.profile_shapes.profile`
        Desired profile.

    Raises
    ------
    RuntimeError :
        Raised if no valid model exists for the requested name.

    Notes
    -----
    There's probably a cleaner way to do this.
    """
    if name == 'gauss':
        return gaussian
    elif name == 'voigt':
        return voigt
    elif name == 'lorentzian':
        return lorentzian
    elif name == 'planck':
        return planck
    elif name == 'skewgauss':
        return skewgauss
    else:
        raise RuntimeError("No such model: %s" % (name))


class profile():
    def __init__(self, **kwargs):
        pass

    def f(self, x, *args, **kwargs): # , x, Q):
        pass

    def df(self, x, *args, **kwargs):
        pass

    def fdf(self, x, Q):
        pass

    def eval(self, x, Q):
        pass

class gaussian(profile):
    def __init__(self, **kwargs):
        self.Nparm = 3

    def f(self, x, *args, **kwargs): #, x, Q):
        print(x)
        print(args)
        print(kwargs)
        if len(args) == 0:
            return 0.0
        (m, s, A) = Q
        z = (x - m) / s
        dfdA = np.exp(-0.5 * z*z)
        f = A * dfdA
        return f

    def df(self, x, *args, **kwargs): # % , x, Q):
        print(x)
        print(args)
        print(kwargs)
        if len(args) == 0:
            return (0.0, 0.0, 0.0)

        (m, s, A) = Q
        z = (x - m) / s
        dfdA = np.exp(-0.5 * z*z)
        f = A * dfdA
        dfdm = f * z / s
        dfds = dfdm * z

        return (dfdm, dfds, dfdA)

    def fdf(self, x, Q):
        (m, s, A) = Q
        z = (x - m) / s
        dfdA = np.exp(-0.5 * z*z)
        f = A * dfdA
        dfdm = f * z / s
        dfds = dfdm * z

        return (f, dfdm, dfds, dfdA)

    def eval(self, x, Q):
        (m, s, A) = Q
        return self.f(x, Q) / (s * np.sqrt(2.0 * np.pi))

# https://en.wikipedia.org/wiki/Voigt_profile
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.wofz.html#scipy.special.wofz
class voigt(profile):
    def __init__(self, **kwargs):
        self.Nparm = 4

    def f(self, x, Q):
        (m, s, A, eta) = Q
        zR = (x - m) / s
        zI = eta / s
        z = np.sqrt(0.5) * (zR + zI*1j)

        f = A * (sp.wofz(z).real)/(s * np.sqrt(2.0 * sp.pi))
        return f

    def df(self, x, Q):
        r"""
        Notes
        -----
        zR = (x - m) / s
        zI = eta / s
        z = np.sqrt(0.5) * (zR + zI*I)

        dz/dm = -np.sqrt(0.5) / s
        dz/ds = -np.sqrt(0.5) / s^2 ( (x-m) + eta I)
        dz/deta = np.sqrt(0.5) I / s

        f = W(z) / ks
        df/dm = 1/ks * dW/dz * dzdm
        df/ds = 1/k * (dW/dz * dzds * s - W(z)) / s^2
        dfdeta = 1/ks * dW/dz * dzdeta

        W = np.exp(-z^2) * erfc(-i*z)
        dW/dz = d(np.exp)/dz * erfc(-i*z) + np.exp(-z^2) * d(erfc)/dz
        dnp.expdz = -2 * z * np.exp(-z^2)
        derfdz = 2i / pi * np.exp(-z^2)

        dW/dz = -2 * z * W(z) + 2 * i / pi * np.exp(-z^2) * np.exp(-z^2)
        """
        (m, s, A, eta) = Q
        zR = (x - m) / s
        zI = eta / s
        z = np.sqrt(0.5) * (zR + zI*1j)

        dfdA = (sp.wofz(z).real)/(s * np.sqrt(2.0 * sp.pi))
        dWdz = -2 * (z * sp.wofz(z) +
                     1j / sp.pi * np.exp(-2 * z**2))
        dzdm = -np.sqrt(0.5) / s
        dzds = -z / s
        dzdeta = np.sqrt(0.5) * 1j / s

        dfdm = A/(s * np.sqrt(2.0) * sp.pi) * dWdz.real * dzdm
        dfds = -A/(s * np.sqrt(2.0) * sp.pi) * (dWdz.real * z + sp.wofz(z).real) / s
        dfdeta = A/(s * np.sqrt(2.0) * sp.pi) * dWdz.imag / s * -np.sqrt(0.5)

        return (dfdm, dfds, dfdA, dfdeta)

    def fdf(self, x, Q):
        (m, s, A, eta) = Q
        zR = (x - m) / s
        zI = eta / s
        z = np.sqrt(0.5) * (zR + zI*1j)

        f = A * (sp.wofz(z).real)/(s * np.sqrt(2.0 * sp.pi))
        return (f, 0, 0, 0)

class skewgauss(profile):
    def __init__(self, **kwargs):
        self.Nparm = 4

    def gamma(eta):
        delta = eta / np.sqrt(1 + eta*eta)
        gamma = (2.0 - sp.pi/2.0) * (delta * np.sqrt(2/sp.pi))**3 / (1 - (2 / sp.pi) * delta*delta)**1.5
        return gamma

    def f(self, x, Q):
        (m, s, A, eta) = Q
        z = (x - m)/s
        G = np.exp(-0.5 * z*z)

        f = A * G * (1.0 * sp.erf(eta * z * np.sqrt(0.5)))

        return f

    def fdf(self, x, Q):
        (m, s, A, eta) = Q
        z = (x - m)/s
        G = np.exp(-0.5 * z*z)

        dfdA = G * (1.0 * sp.erf(eta * z * np.sqrt(0.5)))
        f = dfdA * A
        dfdeta = A / np.sqrt(0.5 * sp.pi) * z * G * np.exp(-0.5 * eta*eta * z*z)
        dfdm = f * z / s - dfdeta * eta * s / z
        dfds = f * z*z / s - dfdeta * eta / s

        return (f, dfdm, dfds, dfdA, dfdeta)

    def eval(self, x, Q):
        (f, dfdm, dfds, dfdA, dfdeta) = self.fdf(x,Q)
        return(f)

class lorentzian(profile):
    def __init__(self, **kwargs):
        self.Nparm = 3

    def fdf(self, x, Q):
        (m, s, A) = Q
        z = 1 / ((x-m)**2 + 0.25 * s**2)
        dfdA = 0.5 * (s / sp.pi) * z
        f = A * dfdA
        dfdm = A * (s / sp.pi) * z * (x - m)
        dfds = f * (1.0 - 0.5 * (s**2 * z))

        return (f, dfdm, dfds, dfdA)

    def eval(self, x, Q):
        (f, dfdm, dfds, dfdA, dfdeta) = self.fdf(x,Q)
        return(f / (s * np.sqrt(2 * sp.pi)))

class planck(profile):
    def __init__(self, **kwargs):
        self.Nparm = 1

    def fdf(self, x, Q):
        (T) = Q
        E = np.exp(1 / (T * x))
        dfdA = x**-5 / (E - 1)
        f = A * dfdA
        dfdT = f / x * E / (E - 1) * T**-2
        return(f, dfdT, dfdA)

