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
from robospect import spectra
from robospect import lines
from robospect import models

__all__ = ['line_gauss_guess']

class line_gauss_guess(spectra.spectrum):
    modelName = 'pre'
    modelPhase = 'initial'
    modelParamN = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = kwargs.pop(self.modelPhase, dict())
        self._configInitial(**self.config)

    def _configInitial(self, **kwargs):
        self.range = kwargs.pop('range', 1.00)

    def _centroid(self, X, Y):
        V = 0.0
        W = 0.0
        for vX, vY in zip(X, Y):
            print("     >> %f %f & %f %f" % (vX, vY, V, W))
            V += vX * vY
            W += vY
        if W == 0.0:
            raise RuntimeError("line_gauss_guess.centroid: division by zero")
        return V/W

    def _interpY(self, X, Y, index, value, side='left'):
        if side == 'left':
            dy = Y[index] - Y[index - 1]
            dx = X[index] - X[index - 1]
        elif side == 'right':
            dy = Y[index] - Y[index - 1]
            dx = X[index] - X[index - 1]

        return(dx / dy * (value - Y[index - 1]) + X[index - 1])

    def fit_initial(self, **kwargs):
        self._configInitial(**kwargs)

        self.lines = np.copy(self.continuum)
        P = models.gaussian()
        temp = (self.y - self.continuum)
        for line in self.L:
            ## 2019-05-23 CZW:
            ## The issues here:
            ##   * searchsorted isn't quite as good as I want, but I think this resolves the issue now.
            ##   * the inputs to _centroid wasn't including the right-most pixel.  fixed?
            ##   * the off-by-one issue hits the F-calculation as well.

            center= np.searchsorted(self.x, line.x0, side='left')
            #            print("%s: %f => %d (%f %f)" % (line.comment, line.x0, center, self.x[center], self.x[center + 1]))

            start = np.searchsorted(self.x, line.x0 - self.range, side='left')
            end   = np.searchsorted(self.x, line.x0 + self.range, side='right')
            #            print("%d %d => %f %f" % (start, end, self.x[start], self.x[end]))
            # mean
            centroidRange = 1
            m = self._centroid(self.x[center - centroidRange:center + centroidRange + 1],
                               temp[center - centroidRange:center + centroidRange + 1])
            # print("%f %f %f %d" % (line.x0, m, 1.0, center))
            #            center= np.searchsorted(self.x, m, side='left') - 1
            F = temp[center]

            print("%f %f [%f %f %f] %d" % (line.x0, m, F, temp[center - 1], temp[center + 1], center))
            ## CZW: ok?

            ## This is truncating the two sides unevenly, I think.  This leads to sigma differences, which are the issue.
            #            print(temp[start: center + 1] / F)
            #            print(self.x[start: center + 1])
            hwhm1, hwqm1, hw3qm1 = (0.0, 0.0, 0.0)
            for idx in range(center, start, -1):
#                print("(%d %f) (%f %f %f)" % (idx, temp[idx] / F, hwhm1, hwqm1, hw3qm1))
#                print("LV (%f %f %f)" % (temp[idx] / F, temp[idx - 1] / F, temp[idx + 1] / F))
                if hw3qm1 == 0.0 and abs(temp[idx - 1] / F) < 0.75:
                    hw3qm1 = self._interpY(self.x, temp, idx, 0.75 * F)
#                    print(" (%d %f) (%f %f %f)" % (idx, temp[idx] / F, hwhm1, hwqm1, hw3qm1))
                if hwhm1 == 0.0 and abs(temp[idx - 1] / F) < 0.5:
                    hwhm1 = self._interpY(self.x, temp, idx, 0.5 * F)
#                    print("  (%d %f) (%f %f %f)" % (idx, temp[idx] / F, hwhm1, hwqm1, hw3qm1))
                if hwqm1 == 0.0 and abs(temp[idx - 1] / F) < 0.25:
                    hwqm1 = self._interpY(self.x, temp, idx, 0.5 * F)
#                    print("   (%d %f) (%f %f %f)" % (idx, temp[idx] / F, hwhm1, hwqm1, hw3qm1))
                    break

            hwhm2, hwqm2, hw3qm2 = (0.0, 0.0, 0.0)
            #            print(temp[center:end + 1] / F)
            #            print(self.x[center:end + 1])
            for idx in range(center , end + 1, 1):
#                print("(%d %f) (%f %f %f)" % (idx, temp[idx] / F, hwhm2, hwqm2, hw3qm2))
#                print("RV (%f %f %f)" % (temp[idx] / F, temp[idx - 1] / F, temp[idx + 1] / F))
                if hw3qm2 == 0.0 and abs(temp[idx + 1] / F) < 0.75:
                    hw3qm2 = self._interpY(self.x, temp, idx, 0.75 * F, side='right')
                if hwhm2 == 0.0 and abs(temp[idx + 1] / F) < 0.5:
                    hwhm2 = self._interpY(self.x, temp, idx, 0.5 * F, side='right')
                if hwqm2 == 0.0 and abs(temp[idx + 1] / F) < 0.25:
                    hwqm2 = self._interpY(self.x, temp, idx, 0.5 * F, side='right')
                    break
            hwhm1 = abs(hwhm1 - m)
            hwhm2 = abs(hwhm2 - m)
            hwqm1 = abs(hwqm1 - m)
            hwqm2 = abs(hwqm2 - m)
            hw3qm1 = abs(hw3qm1 - m)
            hw3qm2 = abs(hw3qm2 - m)

#            print("H: (%f %f) Q: (%f %f) 3: (%f %f)" % (hwhm1, hwhm2, hwqm1, hwqm2, hw3qm1, hw3qm2))
            # sigma
            if (hwhm1 == 0.0 and hwhm2 == 0.0):
                sigma = (hw3qm2 + hw3qm1) / 1.55223
            elif (hwhm1 == 0.0 or hwhm1 > 2.0 * hwhm2):
                sigma = hwhm2 / np.sqrt(2.0 * np.log(2.0))
            elif (hwhm2 == 0.0 or hwhm2 > 2.0 * hwhm1):
                sigma = hwhm1 / np.sqrt(2.0 * np.log(2.0))
            else:
                sigma = (hwhm2 + hwhm1) / (2.0 * np.sqrt(2.0 * np.log(2.0)))
            if sigma == 0.0:
                sigma = self.x[center + 1] - self.x[center]

            # flux
            ### CZW: I think this correction fixes the sigma factor commented out.
            # Attempt to correct flux for peak-vs-sample peak offset.
            F = F * np.exp(0.5 * ((m - self.x[center])/sigma)**2)
            F = -1.0 * F # * (sigma * np.sqrt(2.0 * np.pi))
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
            #            print("    %s" % line.Q)
            for dx in range(start, end):
                self.lines[dx] = self.lines[dx] - P.eval(self.x[dx], line.Q)
            print(line.pQ)
            print(center, F, temp[center], self.lines[center] - self.continuum[center])
