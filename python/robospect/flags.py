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

class Flags():
    BIT_PADDING = 16

    INFO = {'NONE':            (0x00, "No additional information."),
            'SUPPLIED' :       (0x01, "Line supplied from external list."),
            'DETECTED' :       (0x02, "Line detected from the data."),
            'BLEND' :          (0x04, "Line fit as part of a blend."),
            'CONTINUUM_FIT'  : (0x10, "Continuum measured for this line."),
            'WAVELENGTH_FIT' : (0x20, "Wavelenth solution measured for this line."),
            }

    QUALITY = {'NONE':      (0x00, "No known issue with line fit."),
               'FIT_FAIL':  (0x01, "Solver returned impossible value.  Line ignored."),
               'FIT_CHISQ': (0x02, "Chi^2 did not improve with inclusion of line.  Line ignored."),
               'FIT_DELTA': (0x04, "Large parameter shift between line prior and fit.  Line ignored."),
               'FIT_BOUND': (0x08, "Line parameters exceed allowed bounds.  Line ignored."),
               'FIT_ERROR_ESTIMATED': (0x10, "No error calculated.  Estimated at 10%"),
               }

    def __init__(self):
        self.value = 0

    def __str__(self):
        return hex(self.value)

    def __repr__(self):
        return hex(self.value)

    def string_to_doc(self, flagString=None):
        """Convert a flag name to the documentation string.

        Parameters
        ----------
        flagString : `str`
            Flag name to convert.

        Returns
        -------
        doc : `str`
            Requested flag description.

        Notes
        -----
        """
        if flagString is None:
            return ""
        elif flagString in self.QUALITY.keys():
            return self.QUALITY[flagString][1]
        elif flagString in self.INFO.keys():
            return self.INFO[flagString][1]
        else:
            raise RuntimeError(f"Unknown flag string: {flagString}")

    def string_to_value(self, flagString=None):
        """Convert a flag name to the decimal value.

        Parameters
        ----------
        flagString : `str`
            Flag name to convert.

        Returns
        -------
        value : `int`
            Requested flag value.

        Notes
        -----
        This packs quality flags into the lower 16 bits, and pushes
        info flags into the upper 16.
        """
        if flagString is None:
            return 0
        elif flagString in self.QUALITY.keys():
            return self.QUALITY[flagString][0]
        elif flagString in self.INFO.keys():
            return self.INFO[flagString][0] << self.BIT_PADDING
        else:
            raise RuntimeError(f"Unknown flag string: {flagString}")

    def string_to_reset_value(self, flagList=None):
        """Convert a list of flag names to the decimal value of the inverse of
        the union.

        Parameters
        ----------
        flagList : `list` of `str
            List of flags to convert.

        Returns
        -------
        value : `int`
            Requested inverse value.
        """
        value = 0
        if isinstance(flagList, list) is True and len(flagList) is not None:
            for bit in [self.string_to_value(name) for name in flagList]:
                value |= bit
        return ~value

    def reset(self, flagList=None):

        """Reset this flag to value zero.
        """
        return self.string_to_reset_value(flagList)

    def set(self, flagString=None):
        """Set a the bitmask associated with a given flag.

        Parameters
        ----------
        flagString : `str`
            Flag name to convert.
        """
        self.value |= self.string_to_value(flagString)

    def unset(self, flagString=None):
        """Unset a the bitmask associated with a given flag.

        Parameters
        ----------
        flagString : `str`
            Flag name to convert.
        """
        self.value &= ~(self.string_to_value(flagString))

    def get_flag_values(self):
        """Get list of flags set for this flag.

        Returns
        -------
        flagKeys : `List`
            List of flag names assigned for this flag.
        """
        flagKeys = []
        for key, value, doc in self.LIST.items():
            if self.value & value:
                flagKeys.append(key)
        return flagKeys

    def doc_flags(self):
        """Get text string containing all known flags, listed one per line.

        Returns
        -------
        docString : `str`
            Documentation string for all known flags.
        """
        docString = []

        for key, valueDoc in sorted(self.QUALITY.items(), key=lambda flag: flag[1]):
            value, doc = valueDoc
            value = self.string_to_value(flagString=key)
            doc = self.string_to_doc(flagString=key)
            docString.append("## %20s 0x%08x %-45s\n" % (key, value, doc))
        for key, valueDoc in sorted(self.INFO.items(), key=lambda flag: flag[1]):
            value, doc = valueDoc
            value = self.string_to_value(flagString=key)
            doc = self.string_to_doc(flagString=key)
            docString.append("## %20s 0x%08x %-45s\n" % (key, value, doc))
        return(docString)
