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

__all__ = ['deblend_nlls']

class deblend_nlls(spectra.spectrum):
    modelName = 'nlls'
    modelPhase = 'deblend'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = kwargs.pop(self.modelPhase, dict())
        self._configDeblend(**config)

    def _configDeblend(self, **kwargs):
        self.profileName = kwargs.pop('profileName', 'gauss')
        self.profile = profileFromName(self.profileName)
        self.deblendRadius = kwargs.pop('deblendRadius', 3.0)

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
            self.fit_lines_set(lines, xMin, xMax)

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

    def fit_lines_set(self, lineList, xMin, xMax):
        """Use scipy.optimize to fit a non-linear least squares model.
        Flags
        -----
        FIT_BOUND :
            Set if the line to measure falls outside the bounds of the spectrum.
        FIT_FAIL :
            Set if the curve fit code raises an error that is ignored.
        """
        self._configLine(**kwargs)
        logger = logging.getLogger(__name__)
        logger.setLevel(self.verbose)

        start = np.searchsorted(self.x, xMin, side='left')
        end   = np.searchsorted(self.x, xMax, side='right')

        while (end - start < 5):
            end = end + 1
            start = start - 1

        T = self.x[start:end]
        Y = self.y[start:end] - self.continuum[start:end]
        E = self.error[start:end]

        for line in lineList:
            line.flags.reset(flagList=["FIT_BOUND", "FIT_FAIL"])

        ## CZW: Pack current values into single list.
        ## CZW: Update profile function for multiple values.
        try :
            optimizeResult = spO.curve_fit(self.profile.fO, np.array(T), np.array(Y),
                                           p0=np.array(line.Q),
                                           sigma=np.array(E), absolute_sigma=True,
                                           check_finite=True, method='lm')
            #                              jac=self.profile.dfO)

            # ChiSq check should be done in line_update.
            ## CZW: Unpack values into line profile parameters.
            # line.Q = optimizeResult[0]
            # line.dQ = np.sqrt(np.diagonal(optimizeResult[1]))
            # line.chi = np.trace(optimizeResult[1])
        except (RuntimeError, TypeError):
            for line in lineList:
                line.flags.set("FIT_FAIL")

        logger.debug(f"Fit: {line.chi:.3f} {line}")
