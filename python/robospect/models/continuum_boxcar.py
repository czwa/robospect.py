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
import robospect.spectra as spectra

__all__ = ['continuum_boxcar']

class continuum_boxcar(spectra.spectrum):
    modelName = 'boxcar'
    modelPhase = 'continuum'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = kwargs.pop(self.modelPhase, dict())
        self._configContinuum(**config)

    def _configContinuum(self, **kwargs):
        self.box_size = kwargs.pop('box_size', 20.0)

    def fit_continuum(self, **kwargs):
        self._configContinuum(**kwargs)

        temp = self.y - self.lines
        for idx, w in enumerate(self.x):
            start = np.searchsorted(self.x, w - self.box_size / 2.0, side='left')
            end = np.searchsorted(self.x, w + self.box_size / 2.0, side='right')

            self.continuum[idx] = np.median(temp[start:end])

            noise = temp[start:end]
            noise = abs(noise - self.continuum[idx])
            self.error[idx] = 1.4826 * np.median(noise)

    def fit_error(self):
        pass
