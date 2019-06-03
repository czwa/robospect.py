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

import scipy.optimize as spO
import numpy as np
from robospect import spectra
from robospect.models.profile_shapes import profileFromName

__all__ = ['line_nlls']

class line_nlls(spectra.spectrum):
    modelName = 'nlls'
    modelPhase = 'line'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = kwargs.pop(self.modelPhase, dict())
        self._configLine(**config)

    def _configLine(self, **kwargs):
        self.profileName = kwargs.pop('profileName', 'gauss')
        self.profile = profileFromName(self.profileName)

    def resultFlags(self, status, success):
        if success is True:
            flags = 0x0000
        else:
            flags = 0x0001

        if status == -1:
            flags |= 0x0002

        return flags

    def nlls_F(self, x, *A):
        chi = 0
        R = A[1] - self.profile.f(A[0], x)

        return R

    def nlls_DF(self, x, *A):
        chi = np.zeros_like(x)
        dR = self.profile.df(A[0], x)

        return -1.0 * np.array(dR).transpose()

    def fit_lines(self, **kwargs):
        self._configLine(**kwargs)

        for line in self.L:
            start = np.searchsorted(self.x, line.Q[0] - 5.0 * abs(line.Q[1]), side='left')
            end   = np.searchsorted(self.x, line.Q[0] + 5.0 * abs(line.Q[1]), side='right')

            while (end - start < 5):
                end = end + 1
                start = start - 1

            T = self.x[start:end]
            Y = self.y[start:end] - self.continuum[start:end]
            E = self.error[start:end]

            # optimizeResult = spO.least_squares(self.nlls_F, np.array(line.Q).transpose(), jac=self.nlls_DF,
            #                                    # loss='soft_l1', ftol=self.tolerance,
            #                                    method='lm',
            #                                    args = (T, Y)
            #                                    )
            try :
                optimizeResult = spO.curve_fit(self.profile.fO, np.array(T), np.array(Y),
                                               p0=np.array(line.Q),
                                               sigma=np.array(E), absolute_sigma=True,
                                               check_finite=True, method='lm')
                # jac=self.profile.dfO)
                #            line.Q = optimizeResult.x
                #            line.chi = optimizeResult.cost
                line.Q = optimizeResult[0]
                line.dQ = np.diagonal(optimizeResult[1])
                line.chi = np.trace(optimizeResult[1])
                line.flags = 0x00
            except RuntimeError:
                line.flags = 0xff
                # line.flags |= self.resultFlags(optimizeResult.status, optimizeResult.success)
            except TypeError:
                line.flags = 0xff
