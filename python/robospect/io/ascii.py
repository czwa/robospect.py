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
from robospect.spectra import spectrum
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
                new_line = line(x0=float(tokens[0]))
            else:
                new_line = line(x0=float(tokens[0]),
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
    if spectrum is None:
        spectrum = spectra.spectrum()

    spectrum.input_filename = filename
    spectrum.length = 0
    index = 0
    f = open(spectrum.input_filename, "r")
    for l in f:
        if not l.startswith("#"):
            tokens = l.split()
            Ntok = len(tokens)
            if Ntok >= 2:
                spectrum.x.append(float(tokens[0]))
                spectrum.y.append(float(tokens[1]))
            elif Ntok == 3:
                spectrum.e0.append(float(tokens[2]))
            elif Ntok > 3:
                spectrum.e0.append(float(tokens[2]))
                spectrum.xcomm.append(" ".join([str(x) for x in tokens[3:]]))
            else:
                raise IndexError("Could not find wavelength/flux pair on line %d of file %s" %
                                 (index, filename))
        index += 1

    spectrum.x = np.array(spectrum.x)
    spectrum.y = np.array(spectrum.y)
    spectrum.e0 = np.array(spectrum.e0)

    spectrum.length = index
    spectrum.min = spectrum.x[0]
    spectrum.max = spectrum.x[spectrum.length - 1]
    return spectrum

