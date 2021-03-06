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
import logging
import numpy as np
from robospect import spectra
from robospect.models.profile_shapes import profileFromName


__all__ = ['continuum_null', 'error_null', 'detection_null', 'initial_null', 'line_null']


class continuum_null(spectra.spectrum):
    modelName = 'null'
    modelPhase = 'continuum'

    def __init__(self, *args, **kwargs):
        self.modelName = 'null'
        self.modelPhase = 'continuum'

        super().__init__(*args, **kwargs)
        config = kwargs.get(self.modelPhase, dict())

    def fit_continuum(self, **kwargs):
        logger = logging.getLogger(__name__)
        logger.setLevel(self.verbose)

        self.continuum = np.ones_like(self.x)


class error_null(spectra.spectrum):
    modelName = 'null'
    modelPhase = 'noise'

    def __init__(self, *args, **kwargs):
        self.modelName = 'null'
        self.modelPhase = 'noise'
        super().__init__(*args, **kwargs)
        config = kwargs.get(self.modelPhase, dict())

    def fit_error(self, **kwargs):
        logger = logging.getLogger(__name__)
        logger.setLevel(self.verbose)

        self.error = 1e-6 * np.ones_like(self.x)


class detection_null(spectra.spectrum):
    modelName = 'null'
    modelPhase = 'detection'

    def __init__(self, *args, **kwargs):
        self.modelName = 'null'
        self.modelPhase = 'detection'
        super().__init__(*args, **kwargs)
        config = kwargs.get(self.modelPhase, dict())

    def fit_detection(self, **kwargs):
        logger = logging.getLogger(__name__)
        logger.setLevel(self.verbose)

        pass


class initial_null(spectra.spectrum):
    modelName = 'null'
    modelPhase = 'initial'

    def __init__(self, *args, **kwargs):
        self.modelName = 'null'
        self.modelPhase = 'initial'
        super().__init__(*args, **kwargs)
        config = kwargs.get(self.modelPhase, dict())

    def fit_initial(self, **kwargs):
        logger = logging.getLogger(__name__)
        logger.setLevel(self.verbose)

        self.alternate = np.zeros_like(self.x)
        for l in self.L:
            l.Q = np.array([l.x0, 0.0, 0.0])


class line_null(spectra.spectrum):
    modelName = 'null'
    modelPhase = 'line'

    def __init__(self, *args, **kwargs):
        self.modelName = 'null'
        self.modelPhase = 'line'

        self.profileName = 'gauss'
        super().__init__(*args, **kwargs)
        config = kwargs.get(self.modelPhase, dict())
        self._configLine(**kwargs)

    def _configLine(self, **kwargs):
        if 'profileName' in kwargs:
            self.profileName = kwargs.get('profileName')
        self.profile = profileFromName(self.profileName)

    def fit_lines(self, **kwargs):
        logger = logging.getLogger(__name__)
        logger.setLevel(self.verbose)

        self._configLine(**kwargs)
        self.lines = np.zeros_like(self.x)


