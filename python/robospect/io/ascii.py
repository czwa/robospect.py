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
from robospect.lines import line, sortLines

__all__ = ['read_ascii_spectrum']

def read_ascii_linelist(filename, lines=None):
    """Read list of lines to fit stored in ascii format.

    Parameters
    ----------
    filename : str
        Filename containing the line data.
    lines : List of `robospect.lines.line`, optional
        An optional list of lines to incorporate into output

    Returns
    -------
    lines : List of `robospect.lines.line`
        List of lines read.
    """
    if lines is None:
        lines = []

    f = open(filename, "r")
    for l in f:
        if not l.startswith("#"):
            tokens = l.split()
            Ntok = len(tokens)
            if Ntok == 1:
                new_line = line(float(tokens[0]))
            else:
                new_line = line(float(tokens[0]),
                                comment=" ".join([str(x) for x in tokens[1:]]))
            lines.append(new_line)

    lines.sort(key=sortLines)

    return(lines)


def read_ascii_spectrum(filename, spectrum=None):
    """Read spectrum data stored in ascii format.

    Parameters
    ----------
    filename : str
        Filename containing the spectrum data.
    spectrum : `robospect.spectra`, optional
        An optional spectrum class containing option settings.

    Returns
    -------
    spectrum : `robospect.spectra`
        The spectrum object.

    Raises
    ------
    IndexError
       Raised if a line of the input file does not contain two entries
       (wavelength and flux).

    Notes
    -----

    The input file is assumed to be formatted in space-delineated
    columns containing the wavelength (column 1), the flux (column 2;
    normalized or not), and an optional error value (column 3).  All
    other columns are stored as a string and returned in the output
    spectrum model.

    """

    index = 0
    f = open(filename, "r")
    x = []
    y = []
    e0 = []
    comment = []
    for l in f:
        if not l.startswith("#"):
            tokens = l.split()
            Ntok = len(tokens)
            if Ntok >= 2:
                x.append(float(tokens[0]))
                y.append(float(tokens[1]))
            elif Ntok == 3:
                e0.append(float(tokens[2]))
            elif Ntok > 3:
                e0.append(float(tokens[2]))
                comment.append(" ".join([str(x) for x in tokens[3:]]))
            else:
                raise IndexError("Could not find wavelength/flux pair on line %d of file %s" %
                                 (index, filename))
        index += 1

    if spectrum is None:
        spectrum = spectra.spectrum(x, y, e0=e0, comment=comment, filename=filename)
    else:
        spectrum.x = np.array(x)
        spectrum.y = np.array(y)
        if len(e0) > 0:
            spectrum.e0 = np.array(e0)
        if len(comment) > 0:
            spectrum.comment = comment
        spectrum.filename = filename

    return spectrum

