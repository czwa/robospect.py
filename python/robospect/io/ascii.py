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
import contextlib
import sys
import numpy as np
import robospect as RS


__all__ = ['read_ascii_spectrum', 'read_ascii_linelist', 'write_ascii_spectrum']


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

    Flags
    -----
    SUPPLIED :
        Set to note that a line came from a supplied line list.
    """
    if lines is None:
        lines = []
    if filename is None:
        raise RuntimeError("No line list supplied to read.")

    with open(filename, "r") as f:
        for l in f:
            if not l.startswith("#"):
                tokens = l.split()
                Ntok = len(tokens)
                if Ntok < 1:
                    continue
                elif Ntok == 1:
                    new_line = RS.line(float(tokens[0]))
                else:
                    new_line = RS.line(float(tokens[0]),
                                       comment=" ".join([str(x) for x in tokens[1:]]))
                new_line.flags.set("SUPPLIED")
                lines.append(new_line)

    lines.sort(key=RS.sortLines)
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
    RuntimeError
       Raised if no filename is supplied.
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
    if filename is None:
        raise RuntimeError("No spectrum filename specified.")

    x = []
    y = []
    e0 = []
    comment = []
    with open(filename, "r") as f:
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
        spectrum = RS.spectrum()

    spectrum.x = np.array(x)
    spectrum.y = np.array(y)
    if len(e0) > 0:
        spectrum.e0 = np.array(e0)
    if len(comment) > 0:
        spectrum.comment = comment
    spectrum.filename = filename

    spectrum.continuum = np.ones(len(spectrum.x))
    spectrum.lines = np.zeros(len(spectrum.x))
    spectrum.alternate = np.zeros(len(spectrum.x))
    spectrum.error = np.zeros(len(spectrum.x))

    return spectrum


## CZW: This should be in a utilities section
@contextlib.contextmanager
def smart_open(filename=None):
    if filename is not None:
        f = open(filename, "w")
    else:
        f = sys.stdout

    try:
        yield f
    finally:
        if f is not sys.stdout:
            f.close()


def write_ascii_spectrum(filename, spectrum=None):
    if spectrum is None:
        raise RuntimeError("No spectrum specified to print.")
    with smart_open(filename) as f:
        f.write("####### %d\n" % (len(spectrum.x)))
        for x, y, c, e, l, l2 in zip(spectrum.x,
                                     spectrum.y,
                                     spectrum.continuum,
                                     spectrum.error,
                                     spectrum.lines,
                                     spectrum.alternate):
            f.write("%f %f %f %f %f %f %f\n" %
                    (x, y, 0.0, c, e, l, l2))
