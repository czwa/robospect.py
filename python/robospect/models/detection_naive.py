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

import robospect.spectra as spectra
import robospect.lines as lines

__all__ = ['detection_naive']

class detection_naive(spectra.spectrum):
    __metaclass__ = spectra.M_spectrum
    model_type = 'detection'
    model_name = 'naive'

    threshold = 3.0

    def fit_detection(self):
        """Use signal-to-noise threshold to identify potential lines.

        Notes
        -----
        Iterate over the S/N array, identify pixels that are above the
        detection threshold, and make sure they are local maxima.
        """
        signal_to_noise = abs((self.y - self.lines)/self.error)

        in_line = False

        peak_idx = -1
        peak_val = -99

        for idx, SN in enumerate(signal_to_noise):
            if in_line is False and SN > self.threshold:
                in_line = 1
                peak_idx = idx
                peak_val = SN

            else in_line is True:
                if SN > peak_val:
                    peak_val = SN
                    peak_idx = idx
                else:
                    in_line = False
                    self.L.append(lines.line(x0=self.x[peak_idx],
                                             comment="Found by model_detection_naive"))
                    peak_idx = -1
                    peak_val = -99

        self.L.sort(key=lines.sortLines)
