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

__all__ = ['Config']

class Config():
    def __init__(self, *args):
        # Internal debug assistance things
        self.command_line = " ".join(args)
        self.version = "dev-201901"

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

    def construct_spectra_class(self):
        inheritance_list = []
        if self.detection_model is not None:
            inheritance_list.append(self.detection_model)
        if self.noise_model is not None:
            inheritance_list.append(self.noise_model)
        if self.continuum_model is not None:
            inhertiance_list.append(self.continuum_model)
        if self.line_model is not None:
            inhertiance_list.append(self.line_model)
        inhertiance_list.append(spectra.spectra)

        inheritance = tuple(inheritance_list)
        class Spectra(*inheritance):
            pass

        return Spectra
