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
        print("boxcar init")
        super().__init__(*args, **kwargs)
        print("boxcar end super")
        self.config = kwargs.setdefault(self.modelPhase, dict())
        print("%s" % (self.config))
        self._config(**self.config)
        print("%s" % (self.config))
        print("%s" % (self))
        print("boxcar end init")

    def _config(self, **kwargs):
        print("K %s" % (kwargs))
        self.box_size = kwargs.setdefault('box_size', 40.0)
        print("boxsize: %f" % (self.box_size))

    def fit_continuum(self, **kwargs):
        self._config(**kwargs)

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
