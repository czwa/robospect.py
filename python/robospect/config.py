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

from robospect import spectra
from robospect import models


# If I understand correctly, this should largely do what I want to construct
# the spectra class with all appropriate methods in place.  As we parse the
# configuration, construct a list of models to use:
#    modelClasses = [continuumA, detectionB, noiseA, lineC]
# and then pass it here.  I suspect I don't need to have spectra as an
# argument if I'm always working on it, but I won't know until I test things.
# source: http://alexgaudio.com/2011/10/07/dynamic-inheritance-python.html

def constructSpectraClass(spectra, modelClasses):
    for model in modelClasses:
        if model not in spectra.__bases__:
            spectra.__bases__ = model + spectra.__bases__
        else:
            print("Cannot add %s to %s" % (model, spectra))
    return spectra

