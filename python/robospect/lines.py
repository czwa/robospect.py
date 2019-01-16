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

class line():
    Q = []
    dQ = []
    pQ = []

    chi = 0.0
    Niter = -1

    x0 = 0.0
    comment = ""
    flags = 0xffff
    blend = 0

    def __init__(self, x0=None, comment=None, flags=None, blend=None):
        self.Q  = [0.0, 0.0, 0.0, 0.0]
        self.dQ = [0.0, 0.0, 0.0, 0.0]
        self.pQ = [0.0, 0.0, 0.0, 0.0]

        self.chi = 0.0
        self.Niter = 0

        self.x0 = x0
        self.comment = comment
        self.flags = flags
        self.blend = blend

    def f(self, x):
        y = np.zeros(x.shape())
        return y

    def df(self, x):
        y = np.zeros(x.shape())
        return y

    def eval(self, x):
        y = self.f(x)

