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
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from robospect.spectra import spectrum

__all__ = ['plot_spectrum']

def plot_spectrum(spectrum,
                  min=None, max=None,
                  line=None, width=None,
                  autoscale=False, output=None,
                  errors=False):
    if min is None:
        min = spectrum.x[0]
    if max is None:
        max = spectrum.x[-1]

    if line is not None and width is not None:
        min = spectrum.L[line].x0 - width * spectrum.L[line].Q[1]
        min = spectrum.L[line].x0 + width * spectrum.L[line].Q[1]

    plt.xlim(min, max)
    plt.ylim(0.0, 1.1)
    if autoscale is True:
        ymin, ymax = np.percentile(spectrum.y, [1.0, 99.0])
        plt.ylim(ymin,ymax)

    plt.xlabel("wavelength")
    plt.ylabel("flux")

    if spectrum.L is not None:
        for l in spectrum.L:
            plt.axvline(x=l.x0, color='#FFA500', linewidth=0.1)

    plt.plot(spectrum.x, spectrum.y, color='b')

    if (spectrum.continuum is not None and
        len(spectrum.continuum) == spectrum.length()):
        plt.plot(spectrum.x, spectrum.continuum, color='r')

    if (spectrum.lines is not None and
        len(spectrum.lines) == spectrum.length()):
        plt.plot(spectrum.x, spectrum.lines, color='g')

    if (errors is True and spectrum.error is not None and
        len(spectrum.error) == spectrum.length()):
        plt.plot(spectrum.x, spectrum.continuum + spectrum.error, color='c')
        plt.plot(spectrum.x, spectrum.continuum - spectrum.error, color='c')

    if output is None:
        plt.show()
    elif isinstance(output, PdfPages):
        plt.savefig(output, format="pdf")
    else:
        plt.savefig(output)

def plot_lines(spectrum, width=5.0, all=False, output=None):
    """Plot individual lines as part of a set.

    Parameters
    ----------
    spectrum : `robospect.spectra.spectrum`
        Data to plot.
    width : `float`, optional
        Number of line sigmas to plot on either side.
    all : `bool`, optional
        Plot all lines, or just those that were supplied?
    output : `str`, optional
        Output filename.
    """
    if output is None:
        pass

    np.set_printoptions(precision=2)
    plotN = 1
    with PdfPages(output) as pdf:
        fig = plt.figure(figsize=(8, 10))
        plt.rcParams.update({'font.size': 8})
        plt.ticklabel_format(style='plain', useOffset=False)
        for l in spectrum.L:
            if all is True or l.flags.test("SUPPLIED"):
                if l.flags.test("FIT_FAIL"):
                    continue
                if l.x0 < spectrum.min() or l.x0 > spectrum.max():
                    continue

                print(f"{l}")
                if len(l.Q) > 2 and l.Q[1] > 0 and l.Q[1] < 100:
                    min = l.x0 - width * l.Q[1]
                    max = l.x0 + width * l.Q[1]
                else:
                    min = l.x0 - 0.5
                    max = l.x0 + 0.5
                start, end = subset(spectrum.x, min, max)

                X = spectrum.x[start:end]
                Y = spectrum.y[start:end]
                C = spectrum.continuum[start:end]
                L = spectrum.lines[start:end]
                E = spectrum.error[start:end]

                subplotIndex = plotN % 6
                if subplotIndex == 0:
                    subplotIndex = 6
                plt.subplot(3, 2, subplotIndex)
                plt.xlim(min, max)
                plt.ylim(0.0, 1.1)
                plt.xlabel("wavelength")
                plt.ylabel("flux")
                # plt.text(min, 0.18, f"{l.x0}")
                #                with np.printoptions(precision=2):

                plt.text(min, 0.13, f"chi^2 = {l.chi:.3f}  R = {l.R:.3f}  F = {l.flags}")
                plt.text(min, 0.08, f"fit = {np.array_str(l.Q, precision=2)}")
                plt.text(min, 0.03, f"# {l.x0} {l.comment}")
                plt.axvline(x=l.x0, color='#FFA500', linewidth=0.1)
                plt.plot(X, Y, '+-b')
                plt.plot(X, C, color='r')
                plt.plot(X, C + L, color='g')
                plt.plot(X, C + E, color='c')
                plt.plot(X, C - E, color='c')

                plotN += 1
                if plotN % 6 == 0:
                    pdf.savefig(fig)



def subset(X, xl, xr):
    start = np.searchsorted(X, xl, side='left')
    end   = np.searchsorted(X, xr, side='right')

    if start == end:
        end += 1
    return start, end
