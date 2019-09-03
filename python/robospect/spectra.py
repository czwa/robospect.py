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
import logging

from robospect import lines
from .models.profile_shapes import profileFromName

__all__ = ['spectrum', 'M_spectrum']

class M_spectrum(type):
    pass

class spectrum(object):
    r"""Class to hold data objects and fitting methods.

    """

    def __init__(self, *args, **kwargs):
        self.x = []
        self.y = []
        self.e0 = []
        self.comment = []
        self.L = []
        self.filename = ""

        self.continuum = np.ones(len(self.x))
        self.lines = np.zeros(len(self.x))
        self.alternate = np.zeros(len(self.x))
        self.error = np.zeros(len(self.x))

        self.profile = None

        self.log = logging.getLogger("robospect.spectra")
        self.log.debug("Input Kwargs: %s" % (kwargs))
        # Things like general tolerances probably should be here too.
        self.fitting_parameters = dict()
        if kwargs:
            self.fitting_parameters = kwargs.get('fitting', dict())
        if self.fitting_parameters is not None:
            self.iteration = self.fitting_parameters.setdefault('iteration', 0)
            self.max_iteration = self.fitting_parameters.setdefault('max_iterations', 1)
            self.profile = profileFromName(self.fitting_parameters.setdefault('profileName', 'gauss'))
        else:
            self.iteration = 0
            self.max_iteration = 1

    def max(self):
        if self.x is not None:
            return self.x[-1]

    def min(self):
        if self.x is not None:
            return self.x[0]

    def length(self):
        if self.x is not None:
            return len(self.x)

    def fit(self, **kwargs):
        r"""Method to perform a single fitting iteration.
        """
        if not kwargs:
            kwargs = self.fitting_parameters
        iteration = kwargs.get('iteration', self.iteration)
        max_iteration = kwargs.get('max_iteration', self.max_iteration)

        if len(self.L) > 0:
            self.fit_continuum(**kwargs)
            self.fit_error(**kwargs)

            self.fit_initial(**kwargs)
            self.line_update(**kwargs, alternate=True)

        while iteration < max_iteration:
            self.log.info("## Iteration %d / %d   %d lines" %
                          (iteration + 1, max_iteration, len(self.L)))

            self.fit_continuum(**kwargs)
            self.fit_error(**kwargs)

            self.fit_detection(**kwargs)

            self.fit_initial(**kwargs)
            self.line_update(**kwargs, alternate=True)

            self.fit_lines(**kwargs)
            self.line_update(**kwargs, alternate=False)

            self.fit_deblend(**kwargs)
            self.fit_repair(**kwargs)

            iteration += 1
            # Write outputs?

    def fit_repair(self, **kwargs):
        """Method to correct spectra for wavelength solution errors and other issues.

        To be implemented by subclasses.
        """
        pass

    def fit_detection(self, **kwargs):
        """Method to scan spectra for peaks that may be unmeasured lines.

        To be implemented by subclasses.
        """
        pass

    def fit_error(self, **kwargs):
        """Method to measure the empirical noise level of the spectrum.

        To be implemented by subclasses.
        """
        pass

    def fit_continuum(self, **kwargs):
        """Method to measure the continuum level of the spectrum.

        To be implemented by subclasses.
        """
        pass

    def fit_initial(self, **kwargs):
        """Method to do initial linear fits to lines in the catalog.

        This method should ideally operate in O(n_lines),

        To be implemented by subclases.
        """
        pass

    def fit_lines(self, **kwargs):
        """Method to do complete fits to lines in the catalog.

        To be implemented by subclasses.
        """
        pass

    def fit_deblend(self, **kwargs):
        """Method to deblend lines from each other.

        To be implemented by subclasses.
        """
        pass

    def line_update(self, **kwargs):
        """Method to update current line model based on line profile parameters.

        Configuration
        -------------
        position_error : `float`
        max_sigma : `float`
        max_flux : `float`
        chi_window : `float`

        Flags
        -----
        FIT_CHISQ :
            Set if chi^2 does not improve with addition of line.
        """

        self.log.debug(f"{kwargs}, {self.fitting_parameters}")
        kwargs.update(self.fitting_parameters)

        position_error = float(kwargs.get("position_error", 5.0))
        max_sigma = float(kwargs.get("max_sigma", 100.0))
        max_flux = float(kwargs.get("max_flux", 2.5))
        chi_window = float(kwargs.get("chi_window", 10.0))
        use_alternate = kwargs.get("alternate", False)

        if use_alternate is False:
            flagString = 'FIT_CHISQ'
        else:
            flagString = 'ALT_CHISQ'

        self.lines = np.zeros_like(self.x)
        for line in self.L:
            line.flags.unset(flagString=flagString)

            start = np.searchsorted(self.x, line.x0 - chi_window, side='left')
            end   = np.searchsorted(self.x, line.x0 + chi_window, side='right')

            F = 0.0
            if use_alternate is False:
                F = self.profile.f(self.x[start:end+1], line.Q)
            else:
                F = self.profile.f(self.x[start:end+1], line.pQ)

            M = self.y[start:end+1] - (self.continuum[start:end+1] +
                                       self.lines[start:end+1])
            E = self.error[start:end+1]
            chiPre = np.sum(M / E)**2
            M = M - F
            chiPost = np.sum(M / E)**2

            if chiPost < chiPre:
                self.log.debug(f"Good chi^2: x0: {line.x0} pre: {chiPre} post: {chiPost} chi_window: {chi_window} alternate_model: {use_alternate}")
                self.lines[start:end+1] = self.lines[start:end+1] + F
                line.R = chiPost / (end + 1 - start)
            else:
                self.log.debug(f"Bad chi^2: x0: {line.x0} pre: {chiPre} post: {chiPost} chi_window: {chi_window} alternate_model: {use_alternate}")
                line.flags.set(flagString=flagString)
                line.R = chiPre / (end + 1 - start)
