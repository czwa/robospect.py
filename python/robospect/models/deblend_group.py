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
import logging
import scipy.optimize as spO
import numpy as np
from robospect import spectra
from robospect.models.profile_shapes import profileFromName

__all__ = ['deblend_group']

class deblend_group(spectra.spectrum):
    modelName = 'group'
    modelPhase = 'deblend'

    def __init__(self, *args, **kwargs):
        self.modelName = 'group'
        self.modelPhase = 'deblend'

        self.deblendRadius = 3.0

        super().__init__(*args, **kwargs)
        config = kwargs.get(self.modelPhase, dict())
        self._configDeblend(**config)

    def _configDeblend(self, **kwargs):
        if self.profile is None:
            self.profileName = kwargs.get('profileName', 'gauss')
            self.profile = profileFromName(self.profileName)
        if 'deblendRadius' in kwargs:
            self.deblendRadius = float(kwargs.get('deblendRadius', 3.0))


    def fit_deblend(self, **kwargs):
        """Use scipy.optimize to fit a non-linear least squares model.

        Parameters
        ----------

        Returns
        -------

        Raises
        ------

        Flags
        -----
        FIT_BOUND :
            Set if the line to measure falls outside the bounds of the spectrum.
        FIT_FAIL :
            Set if the curve fit code raises an error that is ignored.
        """
        self._configDeblend(**kwargs)
        groupEndPoints = self.set_blend_groups(self.L)

        for b, xMin, xMax in groupEndPoints:
            lines = filter(lambda l:l.blend == b, self.L)


    def set_blend_groups(self, **kwargs):
        def minCalc(i):
            v = self.L[i].Q[0] - self.deblendRadius * self.L[i].Q[1]
            return v
        def maxCalc(i):
            v = self.L[i].Q[0] + self.deblendRadius * self.L[i].Q[1]
            return v

        index = 0
        min_edge = minCalc(0)
        max_edge = maxCalc(0)

        max_group = max(self.L, ind=lambda ind:self.L[ind].blend)
        current_group = max_group if max_group != 0 else 1
        group_indices = []
        groupEndPoints = []
        for j in range(1, len(self.L)):
            min_line = minCalc(j)
            max_line = maxCalc(j)

            if min_line < max_edge:
                max_edge = max_edge
            if max_line > min_edge:
                min_edge = min_line
            if self.L[j].x0 > min_edge and self.L[j].x0 < max_edge:
                group_indices.append(j)
            else:
                if len(group_indices) != 0:
                    self.L[group_indices].blend = current_group
                    group_endPoints.append( (current_group, min_edge, max_edge) )
                    current_group += 1
        return group_endPoints
