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

__all__ = ['line_nlls']

class line_nlls(spectra.spectrum):
    modelName = 'nlls'
    modelPhase = 'line'

    def __init__(self, *args, **kwargs):
        self.modelName = 'nlls'
        self.modelPhase = 'line'

        super().__init__(*args, **kwargs)
        config = kwargs.get(self.modelPhase, dict())
        self._configLine(**config)

    def _configLine(self, **kwargs):
        if self.profile is None:
            self.profileName = kwargs.get('profileName', 'gauss')
            self.profile = profileFromName(self.profileName)

    def fit_lines(self, **kwargs):
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
        self._configLine(**kwargs)
        logger = logging.getLogger(__name__)
        logger.setLevel(self.verbose)

        for line in self.L:
            line.flags.reset(flagList=["FIT_BOUND", "FIT_FAIL"])

            if line.x0 < self.min() or line.x0 > self.max():
                line.flags.set("FIT_BOUND")
                continue

            start = np.searchsorted(self.x, line.Q[0] - 5.0 * abs(line.Q[1]), side='left')
            end   = np.searchsorted(self.x, line.Q[0] + 5.0 * abs(line.Q[1]), side='right')

            while (end - start < 5):
                end = end + 1
                start = start - 1

            T = self.x[start:end]
            Y = self.y[start:end] - self.continuum[start:end]
            E = self.error[start:end]

            try :
                optimizeResult = spO.curve_fit(self.profile.fO, np.array(T), np.array(Y),
                                               p0=np.array(line.Q),
                                               sigma=np.array(E), absolute_sigma=True,
                                               check_finite=True, method='lm')
                #                              jac=self.profile.dfO)

                # ChiSq check should be done in line_update.

                line.Q = optimizeResult[0]
                line.dQ = np.sqrt(np.diagonal(optimizeResult[1]))
                line.chi = np.trace(optimizeResult[1])
            except RuntimeError:
                line.flags.set("FIT_FAIL")
            except TypeError:
                line.flags.set("FIT_FAIL")
            logger.debug(f"Fit: {line.chi:.3f} {line}")
