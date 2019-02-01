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
    __metaclass__ = spectra.M_spectrum
    box_size = 50.0

    def __init__(self, box_size=None, **kwargs):
        if box_size is not None:
            self.box_size = box_size

#        super().__init__(**kwargs)

    def fit_continuum(self):
        temp = self.y - self.lines
        for idx, w in enumerate(self.x):
            start = np.searchsorted(self.x, w - self.box_size / 2.0, side='left')
            end = np.searchsorted(self.x, w + self.box_size / 2.0, side='right')

            self.continuum[idx] = np.median(temp[start:end])

            noise = temp[start:end]
            noise = abs(noise - self.continuum[idx])
            self.error[idx] = 1.4826 * np.median(noise)

#            print("%d %f %f %f\n" % (idx, self.continuum[idx],
#                                     self.error[idx], np.median(noise)))
    def fit_error(self):
        pass
