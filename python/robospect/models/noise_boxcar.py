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

__all__ = ['noise_boxcar']

class noise_boxcar(spectra.spectrum):
    modelName = 'boxcar'
    modelPhase = 'noise'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = kwargs.pop(self.modelPhase, dict())
        self._configNoise(**config)

    def _configNoise(self, **kwargs):
        self.box_size = kwargs.pop('box_size', 40.0)

    def fit_error(self, **kwargs):
        self._configNoise(**kwargs)

        temp = abs(self.y - self.lines - self.continuum)
        for idx, w in enumerate(self.x):
            start = np.searchsorted(self.x, w - self.box_size / 2.0, side='left')
            end = np.searchsorted(self.x, w + self.box_size / 2.0, side='right')

            noise = temp[start:end]
            self.error[idx] = 1.4826 * np.median(noise)
