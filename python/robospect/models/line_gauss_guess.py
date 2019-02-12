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
import robospect.spectra as spectra
import robospect.lines as lines
import robospect.models.profile_shapes as profiles

__all__ = ['line_gauss_guess']

class line_gauss_guess(spectra.spectrum):
    modelName = 'pre'
    modelPhase = 'initial'
    modelParamN = 3

    def __init__(self, *args, **kwargs):
        print("init initial pre: %s", kwargs)
        if "initial" not in kwargs.keys():
            kwargs["initial"] = dict()
        self.range = kwargs["initial"].setdefault("range", 2.50)

        super().__init__(*args, **kwargs)

    def _centroid(self, X, Y):
        V = 0.0
        W = 0.0
        for vX, vY in zip(X, Y):
            V += vX * vY
            W += vY
        if W == 0.0:
            raise RuntimeError("line_gauss_guess.centroid: division by zero")
        return V/W

    def _interpY(self, X, Y, index, value, side='left'):
        if side == 'left':
            dy = Y[index + 1] - Y[index]
            dx = X[index + 1] - X[index]
        elif side == 'right':
            dy = Y[index - 1] - Y[index]
            dx = X[index] - X[index - 1]

        return(value / dy * dx)

    def _eval_interpolant_fraction(self, central_index, value):
        pass

    def fit_initial(self):
        self.lines = np.copy(self.continuum)
        P = profiles.gaussian()
        temp = abs(self.y - self.continuum)
        for line in self.L:
            #           print("%s: %f" % (line.comment, line.x0))
            start = np.searchsorted(self.x, line.x0 - self.range, side='left')
            center= np.searchsorted(self.x, line.x0, side='left')
            end   = np.searchsorted(self.x, line.x0 + self.range, side='right')

            # mean
            m = self._centroid(self.x[center-2:center+2],
                               temp[center-2:center+2])
            #            print("%f %f %f %d" % (line.x0, m, 1.0, center))
            center= np.searchsorted(self.x, m, side='left')
            F = temp[center - 1]

            #            print("%f %f %f %d" % (line.x0, m, F, center))

            hwhm1, hwqm1, hw3qm1 = (0.0, 0.0, 0.0)
            for idx in range(center - 1, start, -1):
                if hw3qm1 == 0.0 and temp[idx] / F < 0.75:
                    hw3qm1 = self._interpY(self.x, temp, idx, 0.75 * F)
                if hwhm1 == 0.0 and temp[idx] / F < 0.5:
                    hwhm1 = self._interpY(self.x, temp, idx, 0.5 * F)
                if hwqm1 == 0.0 and temp[idx] / F < 0.25:
                    hwqm1 = self._interpY(self.x, temp, idx, 0.5 * F)
                    break

            hwhm2, hwqm2, hw3qm2 = (0.0, 0.0, 0.0)
            for idx in range(center - 1, end, 1):
                if hw3qm2 == 0.0 and temp[idx] / F < 0.75:
                    hw3qm2 = self._interpY(self.x, temp, idx, 0.75 * F, side='right')
                if hwhm2 == 0.0 and temp[idx] / F < 0.5:
                    hwhm2 = self._interpY(self.x, temp, idx, 0.5 * F, side='right')
                if hwqm2 == 0.0 and temp[idx] / F < 0.25:
                    hwqm2 = self._interpY(self.x, temp, idx, 0.5 * F, side='right')
                    break

            # sigma
            sigmas = ((np.array([hwhm1, hwqm1, hw3qm1]) +
                       np.array([hwhm2, hwqm1, hw3qm1])) /
                      np.array([2.0 * np.sqrt(2.0 * np.log(2.0)),
                                np.sqrt(2.0),
                                2.0 * np.sqrt(2.0 * (2.0 * np.log(2.0) - np.log(3.0)))]))
            sigma = np.median(sigmas)
            if sigma == 0.0:
                sigma = self.x[center] - self.x[center - 1]

            # flux
            # Attempt to correct flux for peak-vs-sample peak offset.
            F = F * np.exp(0.5 * ((m - self.x[center])/sigma)**2)
            # eta
            line.Q = np.array([m, sigma, F])
            #            if self.nparm >= 4:
            if (hw3qm2 + hw3qm1) == 0:
                hw3qm2 = 1e-3;
            peakiness = (hwhm2 + hwhm1) / (hw3qm2 + hw3qm1)
            if peakiness > 1.68:
                eta = -132.4711 + 79.3913 * peakiness
            else:
                eta = -18.7118 + 11.9942 * peakiness
            if eta < 0.0:
                eta = 0.0
            np.append(line.Q, eta)

            line.pQ = line.Q
            print("    %s" % line.Q)

            for dx in range(start, end):
                self.lines[dx] = self.lines[dx] - P.eval(self.x[dx], line.Q)
