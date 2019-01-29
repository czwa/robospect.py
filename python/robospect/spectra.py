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

from robospect import lines

__all__ = ['spectrum']

class spectrum():
    r"""Data, model, and fitting method code.
    """

    x = None
    """`numpy.ndarray` : Spectra wavelength data."""
    y = None
    """`numpy.ndarray` : Spectra intensity data."""
    e0 = None
    """`numpy.ndarray` : Spectra input error."""
    comment = None
    """`List` of `str` : String comments for the measurement line."""

    continuum = None
    """`numpy.ndarray` : Current continuum model at the corresponding wavelength index."""
    lines = None
    """`numpy.ndarray` : Current line model at the corresponding wavelength index."""
    alternate = None
    """`numpy.ndarray` : Current alternate line model at the corresponding wavelength index."""
    e = None
    """`numpy.ndarray` : Current noise estimate at the corresponding wavelength index."""

    L = None
    """`List` of `robospect.lines.line`"""
    filename = None
    """`str` containing the file the spectrum was read from."""

    def __init__(self, x=None, y=None, e0=None, comment=None, L=None, filename=None):
        if x is not None:
            self.x = np.array(x)
        if y is not None:
            self.y = np.array(y)
        if e0 is not None:
            self.e0 = np.array(e0)
        if comment is not None:
            self.comment = comment
        if L is not None:
            self.L = L
        if filename is not None:
            self.filename = filename

        if len(self.x) != len(self.y):
            raise RuntimeError("Spectra does not have the same number of flux and wavelength samples.")

        self.continuum = np.ones(len(self.x))
        self.lines = np.zeros(len(self.x))
        self.alternate = np.zeros(len(self.x))
        self.e = np.zeros(len(self.x))

    def max(self):
        if self.x is not None:
            return self.x[-1]

    def min(self):
        if self.x is not None:
            return self.x[0]

    def length(self):
        if self.x is not None:
            return len(self.x)

    def fit(self):
        r"""Method to perform a single fitting iteration.
        """
        self.fit_detection()
        self.fit_initial()
        self.fit_continuum()
        self.fit_error()
        self.fit_lines()

    def fit_detection(self):
        r"""Method to scan spectra for peaks that may be unmeasured lines.

        To be implemented by subclasses.
        """
        pass

    def fit_initial(self):
        r"""Method to do initial linear fits to lines in the catalog.

        This method should ideally operate in O(n_lines),

        To be implemented by subclases.
        """
        pass

    def fit_lines(self):
        r"""Method to do complete fits to lines in the catalog.

        To be implemented by subclasses.
        """
        pass

    def fit_continuum(self):
        r"""Method to measure the continuum level of the spectrum.

        To be implemented by subclasses.
        """
        pass

    def fit_error(self):
        r"""Method to measure the empirical noise level of the spectrum.

        To be implemented by subclasses.
        """
        pass
