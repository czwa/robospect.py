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

__all__ = ["Flags"]

def Flags():
    BIT_PADDING = 16

    INFO = {'NONE':        (0x0, "No additional information."),
            'SUPPLIED' :       (0x01, "Line supplied from external list."),
            'DETECTED' :       (0x02, "Line detected from the data."),
            'BLEND' :          (0x04, "Line fit as part of a blend."),
            'CONTINUUM_FIT'  : (0x10, "Continuum measured for this line."),
            'WAVELENGTH_FIT' : (0x20, "Wavelenth solution measured for this line."),
            }

    QUALITY = {'NONE':      (0, "No known issue with line fit."),
               'FIT_FAIL':  (1, "Solver returned impossible value.  Line ignored."),
               'FIT_CHISQ': (2, "Chi^2 did not improve with inclusion of line.  Line ignored."),
               'FIT_DELTA': (4, "Large parameter shift between line prior and fit.  Line ignored."),
               'FIT_BOUND': (8, "Line parameters exceed allowed bounds.  Line ignored."),
               }

    def __init__(self):
        self.value = 0

    def __str__(self):
        return hex(self.value)

    def __repr__(self):
        return hex(self.value)

    def string_to_value(self, flagString=None):
        if flagString is None:
            return 0
        elif flagString in keys(self.QUALITY):
            return self.QUALITY[flagString][0]
        elif flagString in keys(self.INFO):
            return self.INFO[flagString][0] << self.BIT_PADDING
        else:
            raise RuntimeError(f"Unknown flag string: {flagString}")

    def reset(self):
        return 0

    def set(self, flagString=None):
        self.value |= self.string_to_value(flagString)

    def unset(self, flagString=None):
        self.value &= ~(self.string_to_value(flagString))

    def get_flag_values(self):
        flagKeys = []
        for key, value, doc in self.LIST.items():
            if self.value & value:
                flagKeys.append(key)
        return flagKeys

    def doc_flags(self):
        docString = ""
        for key, value, doc in self.LIST.items():
            if self.value & value:
                docString += "%20s %10s %48s\n" % (key, hex(value), doc)
        return(docString)

