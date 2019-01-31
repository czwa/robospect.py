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

import robospect.spectra as spectra
import robospect.lines as lines

__all__ = ['line_gauss_guess']

class line_gauss_guess(spectra.spectrum):
    range = 25.0

    def _centroid(self, X, Y):
        V = 0.0
        W = 0.0
        for vX, vY in zip(X, Y):
            V += vX * vY
            W += vY
        if W == 0.0:
            raise RuntimeError("line_gauss_guess.centroid: division by zero")
        return V/W

    def _eval_interpolant_fraction(self, central_index, value):
        pass
    def fit_initial(self):
        for line in L:
            start = np.searchsorted(self.x, line.x0 - range, side='left')
            center= np.searchsorted(self.x, line.x0, side='right')
            end   = np.searchsorted(self.x, line.x0 + range, side='right')

            m = self._centroid(self.x[center-2:center+2],
                               self.y[center-2:center+2] -
                               self.continuum[center-2:center+2])
            F = abs(self.y[center] - self.continuum[center])

            subX = self.x[start:end]
            subY = abs(self.y[start:end] - self.continuum[start:end])

            prior = F + 1
            for dx in range(center, start):
                if subY[dx] < prior and subY[dx] > 0.25 F:
                    prior = subY[dx]
                else:
                    start = dx - 1
                    break
            prior = F + 1
            for dx in range(center, end):
                if subY[dx] < prior and subY[dx] > 0.25 F:
                    prior = subY[dx]
                else:
                    end = dx + 1
                    break

            subX = self.x[start:center]
            subY = abs(self.y[start:center] - self.continuum[start:center])
            hwhm1, hwqm1, hw3qm1 = np.interp([0.25 * F, 0.5 * F, 0.75 * F],
                                             subY, subX)

            subX = self.x[center:end]
            subY = abs(self.y[center:end] - self.continuum[center:end])
            hwhm2, hwqm2, hw3qm2 = np.interp([0.25 * F, 0.5 * F, 0.75 * F],
                                             subY, subX)

        # sigma

        # flux
        pass
