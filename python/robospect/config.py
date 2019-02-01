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

import argparse

from robospect import spectra
from robospect import models

__all__ = ['Config']

class Config:
    r"""Configuration handler for ROBOSPECT.

    The current list of parameters are based on the C version, and are
    not guaranteed to be implemented on any dev- version of the code.

    """
    def __init__(self, *args):
        # Internal debug assistance things
        self.command_line = " ".join(args)
        self.version = "dev-201902"

        self.arg_dict = _parse(args)
        # Input options
        self.spectrum_file = None
        self.line_list = None
        self.spectrum_order = 0
        self.flux_calibrated = False

        # Options that actually belong to a model, but I'm copying here
        # from rs.c for now.
        self.max_iterations = 1
        self.tolerance = 1e-3

        self.radial_velocity = 0.0
        self.rv_range = 300.0
        self.rv_max_error = 1e-2
        self.rv_steps = 100
        self.rv_sigma = 10.0

        self.detection_threshold = 3.0

        self.continuum_box = 40.0
        self.noise_box = 40.0

        self.line_abs_deviation = 10.0
        self.line_rel_deviation = 2.0

        self.deblend_radius = 4.0
        self.deblend_ratio = 0.1
        self.deblend_iterations = 3

        # Output options
        self.path_base = None
        self.save_temp = False
        self.plot_all = False
        self.verbose = 0x00
        self.log = None

        # Model selection stuff
        self.radial_velocity_model = None
        self.detection_model = None
        self.noise_model = None
        self.continuum_model = None
        self.line_model = None
        self.deblend_model = None

        # Directly parse command line here?
        # C = Config(sys.argv) => returns populated config
        # S = C.read_spectra() => returns correct class with data
        # R = S.run_fit()      => returns results
        # C.write_results(R)   => does output IO?

    def _parse(self, args):
        """Parse command line options into appropriate categories.

        Parameters
        ----------
        args : `List` of `str`
            List of command line arguments to parse

        Returns
        -------
        arguments : `dict`
            Dictionary of dictionaries containing parameter/values
            split into categories.

        Notes
        -----

        I haven't fully decided how this should work, but I think my
        current plan is to split arguments into category, instantiate
        the models (arguments['category']['model'] most likely), and
        then pass the argument dict to a parser in that model.  The
        alternate is to have this just append into a list of strings
        for each category, and then have each model call ArgParse to
        split out the parameters.  The alternate has the benefit that
        each model can be more arbitrary in the acceptable parameters.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('-R', "--radial_velocity", nargs=2, action='append')
        parser.add_argument('-D', "--detection", nargs=2, action='append')
        parser.add_argument('-N', "--noise", nargs=2, action='append')
        parser.add_argument('-C', "--continuum", nargs=2, action='append')
        parser.add_argument('-I', "--initial", nargs=2, action='append')
        parser.add_argument('-L', "--line", nargs=2, action='append')
        parser.add_argument('-B', "--deblend", nargs=2, action='append')
        parser.add_argument('-F', "--fitting", nargs=2, action='append')

        arguments = dict()
        parsed = parser.parse_args(args)

        for argClass in vars(parsed).keys():
            arguments[argClass] = {t[0]: t[1] for t in vars(parsed)[argClass]}

        return arguments

    def construct_spectra_class(self):
        r"""Construct the spectra class.

        Using the information in the configuration, construct a
        super-class of the spectra class that implements the various
        fitting methods.

        Notes
        -----

        I would like this to be able to append the correct entries to
        the inheritance list by name, instead of relying on the
        sub-class being set in the configuration class.
        """
        inheritance_list = []
        if self.detection_model is not None:
            inheritance_list.append(self.detection_model)
        if self.noise_model is not None:
            inheritance_list.append(self.noise_model)
        if self.continuum_model is not None:
            inheritance_list.append(self.continuum_model)
        if self.line_model is not None:
            inheritance_list.append(self.line_model)
        inheritance_list.append(spectra.spectrum)

        inheritance = tuple(inheritance_list)
        class Spectra(*inheritance):
#            __metaclass__ = spectra.M_spectrum

            def copy_data(self, spectrum):
                self.x = spectrum.x
                self.y = spectrum.y
                self.e0 = spectrum.e0
                self.comment = spectrum.comment

                self.continuum = spectrum.continuum
                self.lines = spectrum.lines
                self.alternate = spectrum.alternate
                self.error = spectrum.error
                self.L = spectrum.L
                self.filename = spectrum.filename

        return Spectra()
