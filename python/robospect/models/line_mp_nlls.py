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
import itertools
import logging
import multiprocessing
import scipy.optimize as spO
import numpy as np
from robospect import spectra
from robospect.models.profile_shapes import profileFromName

__all__ = ['line_mp_nlls']

class line_mp_nlls(spectra.spectrum):
    modelName = 'mp_nlls'
    modelPhase = 'line'

    def __init__(self, *args, **kwargs):
        self.modelName = 'mp_nlls'
        self.modelPhase = 'line'

        self.nParallel = 12

        super().__init__(*args, **kwargs)
        config = kwargs.get(self.modelPhase, dict())
        self._configLine(**config)

    def _configLine(self, **kwargs):
        if 'nProc' in kwargs:
            self.nParallel = int(kwargs.get('nProc', 12))
        if 'parallel' in kwargs:
            self.nParallel = int(kwargs.get('parallel', 12))
        if self.profile is None:
            self.profileName = kwargs.get('profileName', 'gauss')
            self.profile = profileFromName(self.profileName)

    def _fit_one(self, Q, T, Y, E):
        try:
            result = spO.curve_fit(self.profile.fO, np.array(T), np.array(Y),
                               p0=np.array(Q),
                               sigma=np.array(E), absolute_sigma=True,
                               check_finite=True, method='lm')
            flag = "NONE"
        except RuntimeError:
            flag = "FIT_FAIL"
        except TypeError:
            flag = "FIT_FAIL"
        return flag, result[0], np.sqrt(np.diagonal(optimizeResult[1])), np.trace(optimizeResult[1])

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

        vecQ = []
        vecT = []
        vecY = []
        vecE = []
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

            vecQ.append(np.array(line.Q))
            vecT.append(np.array(self.x[start:end]))
            vecY.append(np.array(self.y[start:end] - self.continuum[start:end]))
            vecE.append(np.array(self.error[start:end]))

        with multiprocessing.Manager() as manager:
            with multiprocessing.Pool(self.nParallel) as pool:
                R = pool.starmap_async(indep_fit_one, zip(vecQ, vecT, vecY, vecE,
                                                          itertools.repeat(self.profile.fO)))

                for r, l in zip(R.get(), self.L):
                    flag, Q, dQ, chi = r
                    if flag == "NONE":
                        l.flags.set(flag)
                        l.Q = Q
                        l.dQ = dQ
                        l.chi = chi
                    else:
                        l.flags.set(flag)
                    logger.debug(f"Fit: {l.chi:.3f} {l}")



def indep_fit_one(Q, T, Y, E, fO):
    try:
        result = spO.curve_fit(fO, np.array(T), np.array(Y),
                               p0=np.array(Q),
                               sigma=np.array(E), absolute_sigma=True,
                               check_finite=True, method='lm')
        flag = "NONE"
        return flag, result[0], np.sqrt(np.diagonal(result[1])), np.trace(result[1])
    except (RuntimeError, TypeError) as e:
        print(e)
        flag = "FIT_FAIL"
        return flag, Q, 0.1 * Q, 10000.0


