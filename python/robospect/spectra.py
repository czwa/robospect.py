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

from robospect import lines

class spectrum():
    def __init__(self):
        self.x = []
        self.y = []
        self.e0 = []
        self.xcomm = []
        
        self.continuum = []
        self.lines = []
        self.alternate = []
        self.e = []
        
        self.min = 99e99
        self.max = -99e99
        self.N = -1

        self.L = []
        self.O = ""
        
    def fit(self):
        self.fit_detection()
        self.fit_initial()
        self.fit_continuum()
        self.fit_error()
        self.fit_lines()
        
    def fit_detection(self):
        pass
    
    def fit_initial(self):
        pass
    
    def fit_lines(self):
        pass
    
    def fit_continuum(self):
        pass
    
    def fit_error(self):
        pass
