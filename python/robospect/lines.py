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
from operator import itemgetter
from robospect.flags import Flags


__all__ = ['line', 'sortLines', 'Catalog']


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


class Catalog():
    """A set of lines that will be fit/have been fit.
    """

    def __init__(self):
        self.Data = []
        self.iterVal = 0
        
        self.Ncols = 0
        
        self.values = dict()
        self.units = dict()
        self.index = dict()
        self.header = dict()
        self.defaults = dict()
        
        self._id(name='x0', unit='Angstrom', header='Expected central wavelength.',
                 default=0.0, index=0)
        self._id(name='chi', unit=None, header="Full fit chi^2 value.",
                 default=99e99, index=80)
        self._id(name='chiDof', unit=None, header="Degrees of freedom in chi^2 fit.",
                 default=0, index=81)
        self._id(name='altChi', unit=None, header='Chi^2 value for the alternate model.',
                 default=0, index=82)
        self._id(name='flags', unit=None, header="Line flag values.",
                 default=Flags(), index=99)
        self._id(name='blend', unit=None, header="Blend group of line.",
                 default=0, index=98)
        self._id(name='comment', unit=None, header="Text comment.",
                 default="", index=100)

    @property
    def Nrows(self):
        return len(self.Data)
    
    def __iter__(self):
        return self.Data[self.iterVal]
        pass

    def __next__(self):
        if self.iterVal > self.Nrows:
            return StopIteration
        else:
            self.iterVal += 1

    def _id(self, name=None, unit=None, index=None, header=None, default=None):
        """Append a column id to the catalog schema.
        """
        if name is not None:
            self.units[name] = unit
            self.header[name] = header
            self.defaults[name] = default
            if index is None:
                print(f"{name} {max(self.index.values())}")
                self.index[name] = int(max(self.index.values())) + 1
            else:
                self.index[name] = index

    def pack(self, index, keys):
        """Return a numpy array of values for a given data index.
        """
        keyList = keys.split(',')
        valList = [self.Data[index][key] for key in keyList]
        return np.array(valList)

    def unpack(self, index, keys, values):
        """Save a numpy array of values to a given data index.
        """
        keyList = keys.split(',')
        for key, value in zip(keyList, values):
            self.Data[index][key] = value
        
    def append(self, x0, *args, **kwargs):
        """Add a new empty line entry to the catalog.
        """
        print(x0)
        print(kwargs)
        newValue = dict()
        newValue['x0'] = x0

        for key, val in kwargs.items():
            if key in self.header:
                newValue[key] = val
            else:
                self.log.warn(f"Unknown value keyword: {key}")
        for key, default in self.defaults.items():
            if default in newValue:
                newValue[key] = newValue[default]
            elif key not in newValue:
                newValue[key] = default
        self.Data.append(newValue)
    
    def sort(self):
        """Sort the catalog rows by input wavelength and sort the schema
        columns by index value.
        """
        # Sort by input wavelength center
        self.Data = sorted(self.Data, key=itemgetter('x0'))

        # Sort columns to be safe.
        for key, value in self.index.items():
            if value < 0:
                self.index[key] += float(max(self.index.values()))
                
    def to_ascii(self, filename):
        """Write an ascii file representation of the catalog.
        """
        np.set_printoptions(precision=4, suppress=True)
        with smart_open(filename) as f:
            f.write("## Robospect line catalog v3\n")
            f.write("## Flags:\n")
            if self.Nrows > 0:
                for flagDoc in (self.Data[0]['flags'].doc_flags()):
                    f.write(flagDoc)

            f.write("## Columns:\n")
            colNames = []
            order = np.argsort(self.index.values())
            for key, index in sorted(self.index.items(), key=lambda x: x[1]):
                headDoc = self.header[key]
                unitDoc = self.units[key]
                if unitDoc is None:
                    unitDoc = ''
                if headDoc is None:
                    headDoc = ''
                f.write(f"##{key:>21} {unitDoc:^10} {headDoc:<}\n")
                colNames.append(key.format("% 8s"))

            f.write("## Data:\n")
            f.write("##" + "  ".join(colNames) + "\n")
            np.set_printoptions(formatter={'float': '{: 0.6f}'.format})
            for L in self.Data:
                for key in colNames:
                    f.write(f"{L[key]: <8}  ")
                f.write("\n")


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
        return "Line(%.2f %s %s %s ##%s)" % \
            (self.x0, self.pQ, self.Q, self.flags, self.comment)


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
