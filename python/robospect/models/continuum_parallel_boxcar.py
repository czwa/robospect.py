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
import multiprocessing
import numpy as np
from robospect import spectra

__all__ = ['continuum_parallel_boxcar']

class continuum_parallel_boxcar(spectra.spectrum):
    modelName = 'parbox'
    modelPhase = 'continuum'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = kwargs.pop(self.modelPhase, dict())
        self._configContinuum(**config)

    def _configContinuum(self, **kwargs):
        self.box_size = kwargs.pop('box_size', 40.0)
        self.continuum_normalized = kwargs.pop('continuum_normalized', True)
        self.nParallel = kwargs.pop('parallel', 12)

    def fit_continuum(self, **kwargs):
        self._configContinuum(**kwargs)
        logger = logging.getLogger(__name__)
        logger.setLevel(self.verbose)

        temp = self.y - self.lines
        fitD = []
        for idx, w in enumerate(self.x):
            start = np.searchsorted(self.x, w - self.box_size / 2.0, side='left')
            end = np.searchsorted(self.x, w + self.box_size / 2.0, side='right')
            if start < 0:
                start = 0
            if end > len(self.x) - 1:
                end = len(self.x) - 1

            fitD.append(np.array(temp[start:end]))

        with multiprocessing.Manager() as manager:
            with multiprocessing.Pool(self.nParallel) as pool:
                R = pool.starmap_async(parval, zip(fitD))
                for idx, r in enumerate(R.get()):
                    v, n = r
                    self.continuum[idx] = v
                    if self.continuum_normalized is True:
                        # This should be correct for continuum normalized data.
                        self.error[idx] = n / v
                    else:
                        self.error[idx] = n

    def fit_error(self, **kwargs):
        logger = logging.getLogger(__name__)
        logger.setLevel(self.verbose)
        pass


def parval(data):
    v = np.median(data)
    n = 1.4826 * np.median(abs(data - v))
    return(v, n)
