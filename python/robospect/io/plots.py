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

import matplotlib.pyplot as plt

from robospect import spectra

def plot_spectrum(spectrum, pmin=None, pmax=None, line=None, width=None):
    if pmin is None:
        pmin = spectrum.min
    if pmax is None:
        pmax = spectrum.max

    if line is not None and width is not None:
        pmin = spectrum.L[line].x0 - width * spectrum.L[line].w
        pmin = spectrum.L[line].x0 + width * spectrum.L[line].w

    plt.xlim(pmin, pmax)
    plt.ylim(0.0, 1.0)
    plt.plot(spectrum.x, spectrum.y)
    plt.xlabel("wavelength")
    plt.ylabel("flux")
    plt.show()

