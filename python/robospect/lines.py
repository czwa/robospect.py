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
from robospect.flags import Flags


__all__ = ['line', 'sortLines']


class line():
    r"""An object representing a single line fit.

    Parameters
    ----------
    x0 : `float`
        Expected central wavelength of the line to be fit.
    Nparam : `int`, optional
        Number of parameters to use in the fitting process.
    comment : `str`, optional
        Comment describing the line.
    flags : `int`, optional
        Initial flag settings for the line.
    blend : `int`, optional
        Index of the blend group this line belongs to.
    """
    x0 = 0.0

    Q = []
    dQ = []
    pQ = []

    chi = 0.0
    R = 0.0
    Niter = -1

    comment = ""
    flags = Flags()
    blend = 0

    def __init__(self, x0, Nparam=None, comment=None, flags=None, blend=None, Q=None):
        self.x0 = x0

        if Nparam is not None:
            self.Nparam = Nparam
            self.Q  = np.zeros(Nparam)
            self.dQ = np.zeros(Nparam)
            self.pQ = np.zeros(Nparam)

        self.chi = 0.0
        self.Niter = 0

        self.comment = comment  if comment is not None else ""
        self.flags = flags      if flags is not None else Flags()
        self.blend = blend      if blend is not None else 0
        self.Q = Q              if Q is not None else []

    def __repr__(self):
        return "Line(%.2f %s %s %s ##%s)" % (self.x0, self.pQ, self.Q, self.flags, self.comment)

    def f(self, x):
        r"""Evaluate the function of this line for the input wavelength.

        To be implemented by subclass.

        CZW: To be removed?
        """
        return np.zeros(x.shape())

    def df(self, x):
        r"""Evaluate the derivative of this line for the input wavelength.

        To be implemented by subclass.

        CZW: To be removed?
        """
        return np.zeros(x.shape())


def sortLines(line):
    """Sorting function for line lists.

    Parameters
    ----------
    line : `robospect.lines.line`
        Line data to compare.

    Returns
    -------
    x0 : float
        Line center

    Notes
    -----
    This function allows lists of lines to be sorted directly, using
    `list_of_lines.sort(key=sortLines)`.
    """
    return line.x0
