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
from robospect import spectra
from robospect.lines import line, sortLines

__all__ = ['write_ascii_catalog', 'write_fits_catalog'] # 'write_sqlite_catalog', 'write_json_catalog']

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

        with np.printoptions(formatter={'float': '{: 0.6f}'.format}):
            for L in lines:
                if len(L.dQ) < 2:
                    L.dQ = 0.1 * L.Q
                    L.flags = L.flags | 0x8000

                f.write ("%.4f %s   %s   %s       %f   %f   %f 0x%x   %d  %s\n" %
                         (L.x0, L.Q, L.dQ, L.pQ,
                          _eqw(L.Q[2]), _eqw(L.dQ[2]),
                          L.chi, L.flags, L.blend, L.comment))


try:
    import astropy.io.fits as F

    def write_fits_catalog(filename, lines):
        arr_x0 = np.array([])
        arr_chi = np.array([])
        arr_flags = np.array([])
        arr_blend = np.array([])
        arr_comment = []
        arr_Q = np.array([])
        arr_dQ = np.array([])
        arr_pQ = np.array([])

        for L in lines:
            arr_x0.append(L.x0)
            arr_chi.append(L.chi)
            arr_flags.append(L.flags)
            arr_blend.append(L.blend)
            arr_comment.append(L.comment)
            # CZW: etc.

        col_x0 = F.Column(name='line_center', format='D', unit='Angstroms', array=arr_x0)
        col_Q  = F.Column(name='solution', format='3E', unit='', array=arr_Q)
        col_flags = F.Column(name='fit_flags', format='K', unit='', array=arr_flags)
        # CZW: etc.

        hdu = F.BinTableHDU.from_columns([col_x0, col_Q, col_flags])

        out = F.HDUList()
        out.append(hdu)
        out.writeto(filename, overwrite=False)
        out.close()

except ImportError:
    def write_fits_catalog(filename, lines):
        warn("Cannot find astropy.io.fits library.")
        return(write_ascii_catalog(filename, lines))
