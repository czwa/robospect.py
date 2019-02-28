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
from robospect.config import *
from robospect.lines import line
from robospect.spectra import spectrum

__all__ = ['write_ascii_catalog'] # , 'write_fits_catalog', 'write_sqlite_catalog']

def _eqw(F):
    return -1000.0 * F

def write_ascii_catalog(filename, lines):
    """Write list of lines to ascii format
    """
    if filename is None:
        raise RuntimeError("No output catalog file specified")
    if lines is None:
        raise RuntimeError("No lines specified to write")
    np.set_printoptions(precision=4, suppress=True)
    with open(filename, "w") as f:
        f.write ("## Robospect line catalog\n")
        f.write ("## Flags:\n")
        f.write ("## Units\n")
        f.write ("## Headers\n")

        for l in lines:
            f.write ("%.4f %s   %s   %s       %f   %f   %f 0x%x   %d  %s\n" %
                     (l.x0, l.Q, l.dQ, l.pQ,
                      0.0, 0.0,
                      #                      _eqw(l.Q[2]), _eqw(l.dQ[2]),
                      l.chi, l.flags, l.blend, l.comment))

