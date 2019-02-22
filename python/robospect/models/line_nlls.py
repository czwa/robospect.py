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
import robospect.spectra as spectra
import robospect.lines as lines
import robospect.models.profile_shapes as profiles

__all__ = ['line_nlls']

class line_nlls(spectra.spectrum):
    modelName = 'nlls'
    modelPhase = 'line'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = kwargs.setdefault('line', dict())
        self.profile = self.config.setdefault('profile', 'gauss')

    def resultFlags(self, status, success):
        if success is True:
            flags = 0x0000
        else:
            flags = 0x0001

        if status == -1:
            flags |= 0x0002

        return flags

    def fit_line(self):
        for line in L:
            optimizeResult = spO.least_squares(self.profile.f, L.Q, jac=self.profile.df,
                                               # loss='soft_l1', ftol=self.tolerance,
                                               # method='lm', args=(L.Q)
                                               )
            L.Q = optimizeResult.x
            L.chi = optimizeResult.cost
            L.flags |= self.resultFlags(optimizeResult.status, optimizeResult.success)
