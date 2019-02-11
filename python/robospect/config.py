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
from robospect import io

__all__ = ['Config']


class Config:
    r"""Configuration handler for ROBOSPECT.

    The current list of parameters are based on the C version, and are
    not guaranteed to be implemented on any dev- version of the code.

    """
    model_phases = ['repair', 'detection', 'noise', 'continuum',
                    'initial', 'line', 'deblend']
    rs_models = dict()

    def __init__(self, *args, **kwargs):
        # Internal debug assistance things
        self.command_line = " ".join(args)
        self.version = "dev-201902"

        # Pack models into dict for access later
        for rsModel in dir(models):
            for modelPhase in self.model_phases:
                if rsModel.startswith(modelPhase):
                    model = getattr(models, rsModel)
                    model = getattr(model, rsModel)
                    modelName = model.modelName
                    self.rs_models.setdefault(modelPhase, dict()).setdefault(modelName, model)

        self.arg_dict = self._parse(*args)
        print(self.arg_dict)
        print(self.rs_models)

        # Model selection setting
        for modelPhase in self.model_phases:
            modelName = self.arg_dict[modelPhase].setdefault("name", None)
            if modelName is None:
                setattr(self, f"{modelPhase}_model", None)
            else:
                setattr(self, f"{modelPhase}_model", self.rs_models[modelPhase][modelName])

        print(dir(self))

        # Set defaults
        if self.continuum_model is None:
            self.continuum_model = self.rs_models["continuum"]["boxcar"]
        if self.detection_model is None:
            self.detection_model = self.rs_models["detection"]["naive"]
        if self.initial_model is None:
            self.initial_model = self.rs_models["line"]["pre"]

        # Handle fitting arguments
        fittingArgs = self.arg_dict["fitting"]
        self.spectrum_file = fittingArgs.setdefault("spectrum_file", None)
        self.line_list = fittingArgs.setdefault("line_list", None)
        self.max_iterations = fittingArgs.setdefault("max_iterations", 1)
        self.tolerance = fittingArgs.setdefault("tolerance", 1e-3)
        self.output = fittingArgs.setdefault("output", "/tmp/rs")
        self.plot_all = fittingArgs.setdefault("plot_all", False)
        self.log = fittingArgs.setdefault("log", "/tmp/rs.log")

        self.iteration = 0
        # Directly parse command line here?
        # C = Config(sys.argv) => returns populated config
        # S = C.read_spectra() => returns correct class with data
        # R = S.run_fit()      => returns results
        # C.write_results(R)   => does output IO?

    def _parse(self, *args):
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
        parser.add_argument('-R', "--repair", nargs=2, action='append')
        parser.add_argument('-D', "--detection", nargs=2, action='append')
        parser.add_argument('-N', "--noise", nargs=2, action='append')
        parser.add_argument('-C', "--continuum", nargs=2, action='append')
        parser.add_argument('-I', "--initial", nargs=2, action='append')
        parser.add_argument('-L', "--line", nargs=2, action='append')
        parser.add_argument('-B', "--deblend", nargs=2, action='append')
        parser.add_argument('-F', "--fitting", nargs=2, action='append')
        parsed, unparsed = parser.parse_known_args(*args)

        arguments = dict()
        for argClass in vars(parsed).keys():
            if vars(parsed)[argClass] is None:
                arguments[argClass] = dict()
            else:
                arguments[argClass] = {t[0]: t[1] for t in vars(parsed)[argClass]}

        return arguments

    def read_spectrum(self, spectrum_file=None):
        S = self.construct_spectra_class(None, **self.arg_dict)
        if spectrum_file is not None:
            self.spectrum_file = spectrum_file
        S = io.read_ascii_spectrum(self.spectrum_file, spectrum=S)
        if self.line_list is not None:
            S.L = io.read_ascii_linelist(self.line_list, lines=None)

        return S

    def construct_spectra_class(self, *args, **kwargs):
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
        if self.initial_model is not None:
            inheritance_list.append(self.initial_model)
        if self.line_model is not None:
            inheritance_list.append(self.line_model)
        inheritance_list.append(spectra.spectrum)

        inheritance = tuple(inheritance_list)
        print(inheritance_list)
        class Spectra(*inheritance):
            def __init__(self, *args, **kwargs):
                print("Spectra init")
                super().__init__(*args, **kwargs)

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

        return Spectra(*args, **kwargs)
