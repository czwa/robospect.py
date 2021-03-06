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
import numpy as np
from robospect import spectra

__all__ = ['continuum_boxcar']

class continuum_boxcar(spectra.spectrum):
    modelName = 'boxcar'
    modelPhase = 'continuum'

    def __init__(self, *args, **kwargs):
        self.modelName = 'boxcar'
        self.modelPhase = 'continuum'

        self.box_size = 40.0
        self.continuum_normalized = True
        super().__init__(*args, **kwargs)
        config = kwargs.get(self.modelPhase, dict())
        self._configContinuum(**config)

    def _configContinuum(self, **kwargs):
        if 'box_size' in kwargs:
            self.box_size = float(kwargs.get('box_size'))
        if 'continuum_normalized' in kwargs:
            self.continuum_normalized = kwargs.get('continuum_normalized', True)

    def fit_continuum(self, **kwargs):
        self._configContinuum(**kwargs)
        logger = logging.getLogger(__name__)
        logger.setLevel(self.verbose)

        temp = self.y - self.lines
        for idx, w in enumerate(self.x):
            start = np.searchsorted(self.x, w - self.box_size / 2.0, side='left')
            end = np.searchsorted(self.x, w + self.box_size / 2.0, side='right')
            if start < 0:
                start = 0
            if end > len(self.x) - 1:
                end = len(self.x) - 1

            self.continuum[idx] = np.median(temp[start:end])

            noise = temp[start:end]
            noise = abs(noise - self.continuum[idx])

            if self.continuum_normalized is True:
                # This should be correct for continuum normalized data.
                self.error[idx] = 1.4826 * np.median(noise) / self.continuum[idx]
            else:
                self.error[idx] = 1.4826 * np.median(noise)

    def fit_error(self, **kwargs):
        logger = logging.getLogger(__name__)
        logger.setLevel(self.verbose)
        pass
