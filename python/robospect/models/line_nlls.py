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
import robospect.spectra as spectra
import robospect.lines as lines
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
        print(self.profile)
        print(dir(self.profile))

    def resultFlags(self, status, success):
        if success is True:
            flags = 0x0000
        else:
            flags = 0x0001

        if status == -1:
            flags |= 0x0002

        return flags


    def fit_line(self, **kwargs):
        self._configLine(**kwargs)

        def F(x, *A, **K):
            print(x)
            print(*A)
            print(**K)
            return self.profile.f(x, A, K)

        def DF(x, *A, **K):
            return self.profile.df(x, A, K)

        for line in self.L:
            print(line.Q)
            optimizeResult = spO.least_squares(F, np.array(line.Q).transpose(), jac=DF,
                                               # loss='soft_l1', ftol=self.tolerance,
                                               # method='lm', args=(L.Q)
                                               )
            line.Q = optimizeResult.x
            line.chi = optimizeResult.cost
            line.flags |= self.resultFlags(optimizeResult.status, optimizeResult.success)
