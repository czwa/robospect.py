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

from robospect import spectra
from robospect import lines

__all__ = ["Flags"]

def Flags():
    OLDLIST = {'MAX_ITER': (1, "Solver hit maximum number of iterations without returning a fit within tolerance."),
               'FIT_FAIL': (2, "Solver returned impossible value and aborted further computation."),
               'FIT_IGNORED': (4, "Line rejected from consideration due to concerns with fit parameters."),
               'FIT_REFUSED': (8, "Line rejected from consideration due to lack of chi^2 improvement."),
               'FIT_LARGE_SHIFT': (16, "Fit mean shifted significantly from expected initial value."),
               'FIT_RECENTER': (32, "Fit mean reset to initial value and refit with fixed mean."),
               'BAD_WAVELENGTH': (64, "Suspected bad wavelength solution around this line."),
               'FIX_WAVELENGTH': (128, "Corrected supplied line peak to fit bad wavelength solution."),
               'FIT_BLEND': (256, "Line believed to be part of a blend."),
               'FIT_DEBLEND': (512, "Line solution based on deblending model."),
               'ALT_REFUSED': (1024, "Alternate line model rejected due to lack of chi^2 improvement."),
               'BAD_ERROR_VAL': (2048, "Error value out of range."),
               'FUNC_GAUSSIAN': (1048576, "Line fit with Gaussian model."),
               'FUNC_LORENTZ': (2097152, "Line fit with Lorentzian model."),
               'FUNC_VOIGHT': (4194304, "Line fit with Voight model."),
               }

    LIST = {'NONE': (0, "No known issue with line."),
            # First four bits: line provenance:
            'SUPPLIED_LINE': (0x10000000, "Line supplied from external list."),
            'DETECTED_LINE': (0x20000000, "Line detected from data."),
            'EXPECTED_LINE': (0x40000000, "Line supplied from internal list."),
            'NOT_USED_0008': (0x80000000, "Flag not used."),
            # Next four bits: continuum/error:
            'CONTINUUM_FIXED': (0x01000000, "Continuum set to fixed value."),
            'CONTINUUM_FIT':   (0x02000000, "Continuum measured from data."),
            'ERROR_SUPPLIED':  (0x04000000, "Pixel error supplied with data."),
            'ERROR_FIT':       (0x08000000, "Pixel error measured from data."),
            # Warnings:
            'FIT_BLENDED':    (0x00100000, "Line believed to be part of a blend."),
            'FIT_DEBLENDED':  (0x00200000, "Line solution based on deblending model."),
            'BAD_WAVELENGTH': (0x00400000, "Line wavelength solution suspect."),
            'FIX_WAVELENGTH': (0x00800000, "Wavelength solution corrected."),
            # Initial fit issues:
            'INIT_FIT_REJECTED': (0x00010000, "Initial fit rejected due to chi^2 issue."),
            'INIT_FIT_IGNORED':  (0x00020000, "Initial fit ignored due to peak ordering."),
            # 
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
        elif flagString in keys(self.LIST):
            return self.LIST[flagString][0]
        else:
            raise RuntimeError(f"Unknown flag string: {flagString}")

    def set_flag_value(self, flagString=None):
        self.value |= self.string_to_value(flagString)

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

