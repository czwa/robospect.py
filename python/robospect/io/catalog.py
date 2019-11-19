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

import sys
import contextlib
import numpy as np
from robospect import spectra
from robospect.lines import line, sortLines

__all__ = ['write_ascii_catalog']
#, 'write_fits_catalog']
# 'write_sqlite_catalog', 'write_json_catalog']

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


def _eqw(Q, dQ):
    if len(Q) == 0:
        return 0.0, 0.0
    elif len(Q) < 3:
        return -1000.0 * Q[0], np.abs(1000.0 * dQ[0])
    else:
        W = -1.0 * Q[2] * np.sqrt(2.0 * np.pi * Q[1]**2)
        dW = W * np.sqrt(2.0 * np.pi) * np.sqrt( (dQ[2]/Q[2])**2 + (dQ[1]/Q[1])**2)
        return W, dW


def write_ascii_catalog(filename, lines):
    """Write list of lines to ascii format.

    Parameters
    ----------
    filename : `str`
        Output name to write the line catalog.
    lines : `list` of `robospect.lines.line`
        List of lines to write.

    Returns
    -------

    Raises
    ------
    RuntimeError :
        Raised if no line list is supplied.

    Flags
    -----
    FIT_ERROR_ESTIMATED :
        Set if no error was received for a line.
    """
    if lines is None:
        raise RuntimeError("No lines specified to write")
    np.set_printoptions(precision=4, suppress=True)
    with smart_open(filename) as f:
        f.write ("## Robospect line catalog\n")
        f.write ("## Flags:\n")
        if len(lines) > 0:
            for flagDoc in (lines[0].flags.doc_flags()):
                f.write(flagDoc)

        f.write ("## Units\n")
        if len(lines) != 0 and len(lines[0].Q) == 3:
            f.write("##AA [AA  AA  None]   ")
            f.write("[AA AA None]   ")
            f.write("[AA AA None]   ")
            f.write("mAA mAA  None  None  None None\n")
        elif len(lines) != 0 and len(lines[0].Q) == 4:
            f.write("##AA [AA  AA  None None]   ")
            f.write("[AA AA None]   ")
            f.write("[AA AA None]   ")
            f.write("mAA mAA  None  None  None None\n")

        f.write ("## Headers\n")
        if len(lines) != 0 and len(lines[0].Q) == 3:
            f.write("##wave_0 [gaussianMu  gaussianSigma  gaussianAmp]   ")
            f.write("[uncertaintyMu  uncertaintySigma  uncertaintyAmp]   ")
            f.write("[priorMu  priorSigma  priorAmp]   ")
            f.write("EQW   uncertaintyEQW  chiSqr  flags  blendGroup comment\n")
        elif len(lines) != 0 and len(lines[0].Q) == 4:
            f.write("##wave_0 [gaussianMu  gaussianSigma  gaussianAmp  voigtGamma]   ")
            f.write("[uncertaintyMu  uncertaintySigma  uncertaintyAmp  uncertaintyGamma]   ")
            f.write("[priorMu  priorSigma  priorAmp]   ")
            f.write("EQW   uncertaintyEQW  chiSqr  flags  blendGroup comment\n")

        # This is not a context manager, as that only exists in np 1.16?
        np.set_printoptions(formatter={'float': '{: 0.6f}'.format})
        for L in lines:
            while len(L.Q) < 3:
                L.Q.append(0.0)
            if len(L.dQ) < 2:
                L.dQ = 0.1 * np.array(L.Q)
                L.flags.set("FIT_ERROR_ESTIMATED")

            f.write ("%.4f %s   %s   %s       %f   %f   %f  %s  %d  %s\n" %
                     (L.x0, L.Q, L.dQ, L.pQ,
                      *_eqw(L.Q, L.dQ),
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
