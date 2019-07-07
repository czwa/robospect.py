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
import logging

from . import spectra
from . import models
from . import io

__all__ = ['Config', 'VERSION']

VERSION = 'dev-201906'

class Config:
    """Configuration handler for ROBOSPECT.

    This class is designed to handle three main tasks:

        1) Read the configuration from either a list of args (assumed
           to be command line arguments), or by directly setting the
           configuration dictionaries from kwargs.
        2) Construct a valid Spectra object based on the model names
           for each phase (or from the defaults).
        3) Handle simple IO to read an input spectra and write output
           results.
    """
    model_phases = ['repair', 'detection', 'noise', 'continuum',
                    'initial', 'line', 'deblend']
    rs_models = dict()

    def __init__(self, *args, **kwargs):
        # Initialize logging code.
        logging.basicConfig(format='%(asctime)s %(name)-10s %(levelname) 8s %(message)s',
                            datefmt="%Y-%m-%d %H:%M:%S",
                            level=logging.INFO)
        self.mainLog = logging.getLogger("robospect")
        self.log = logging.getLogger("robospect.config")

        # Parse command line/input configuration dicts to generate new conf parameters.
        if isinstance(args, tuple) and len(args) > 0:
            argument_list = args[0]
        else:
            argument_list = args
        self.arg_dict = self._parse(*args, **kwargs)

        # Internal assistance parameters.
        self.command_line = " ".join(argument_list)
        self.log.info(f"command line: {self.command_line}")
        self.version = VERSION
        self.log.info(f"code version: {self.version}")

        # Pack models into dict for access later
        for rsModel in (dir(models)):
            for modelPhase in self.model_phases:
                if rsModel.startswith(modelPhase):
                    model = getattr(models, rsModel)
                    modelName = model.modelName
                    self.rs_models.setdefault(modelPhase,
                                              dict()).setdefault(modelName, model)
                    self.log.debug("init: name: %s phase: %s" %
                                   (modelName, modelPhase))

        # Model selection setting
        for modelPhase in self.model_phases:
            modelName = self.arg_dict[modelPhase].pop("name", None)
            if modelName is None:
                setattr(self, f"{modelPhase}_model", None)
            else:
                setattr(self, f"{modelPhase}_model",
                        self.rs_models[modelPhase][modelName])

        # This almost certainly needs to be fixed and updated.
        # Set defaults
        if self.continuum_model is None:
            self.continuum_model = self.rs_models["continuum"]["boxcar"]
        if self.detection_model is None:
            self.detection_model = self.rs_models["detection"]["naive"]
        if self.initial_model is None:
            self.initial_model = self.rs_models["line"]["pre"]
        if self.line_model is None:
            self.line_model = self.rs_models["line"]["mp_nlls"]

        # Handle fitting arguments
        fittingArgs = self.arg_dict["fitting"]
        self.spectrum_file = fittingArgs.setdefault("spectrum_file", None)
        self.line_list = fittingArgs.setdefault("line_list", None)
        self.path_base = fittingArgs.setdefault("path_base", None)
        self.max_iterations = fittingArgs.setdefault("max_iterations", 1)
        self.tolerance = fittingArgs.setdefault("tolerance", 1e-3)
        self.output = fittingArgs.setdefault("output", "/tmp/rs")
        self.plot_all = fittingArgs.setdefault("plot_all", False)

        self.iteration = 0

    def _parse(self, *args, **kwargs):
        """Parse command line options into appropriate categories.

        Parameters
        ----------
        args : `List` of `str`
            List of command line arguments to parse
        kwargs : `Dict` of `Dicts`
            Pre-defined configuration dicts.  These are overridden
            by the `args`.

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
        parser.add_argument('-R', "--repair", nargs=2, action='append',
                            help="Conf values for spectrum repair.")
        parser.add_argument('-D', "--detection", nargs=2, action='append',
                            help="Conf values for line detection.")
        parser.add_argument('-N', "--noise", nargs=2, action='append',
                            help="Conf values for spectrum noise modeling.")
        parser.add_argument('-C', "--continuum", nargs=2, action='append',
                            help="Conf values for spectrum continuum modeling.")
        parser.add_argument('-I', "--initial", nargs=2, action='append',
                            help="Conf values for initial line fitting (pre-fitting).")
        parser.add_argument('-L', "--line", nargs=2, action='append',
                            help="Conf values for line modeling.")
        parser.add_argument('-B', "--deblend", nargs=2, action='append',
                            help="Conf values for line deblending.")
        parser.add_argument('-F', "--fitting", nargs=2, action='append',
                            help="General conf values for fitting.")
        parsed, unparsed = parser.parse_known_args(*args)

        # Set defaults from kwargs
        arguments = dict()
        if kwargs is not None:
            for kw in kwargs.keys():
                arguments[kw] = dict(kwargs[kw])

        for argClass in vars(parsed).keys():
            # Create dicts if they do not exist.
            if argClass not in arguments.keys():
                arguments[argClass] = dict()

            # Pack data from the parsed list.
            if arguments[argClass].keys() is None:
                arguments[argClass] = {t[0]: t[1] for t in vars(parsed)[argClass]}
            elif vars(parsed)[argClass] is not None:
                for t in vars(parsed)[argClass]:
                    arguments[argClass][t[0]] = t[1]

        backwardsCompatParser = argparse.ArgumentParser()
        backwardsCompatParser.add_argument('-v', "--verbose", action='count', default=0)
        backwardsCompatParser.add_argument('-V', "--continuum_box",
                                           default=50.0, type=float,
                                           help="Width (in AA) for continuum/noise box")
        backwardsCompatParser.add_argument('-i', "--iterations",
                                           default=1, type=int,
                                           help="Number of iterations for fit.")
        backwardsCompatParser.add_argument('-T', "--tolerance",
                                           default=1e-3, type=float,
                                           help="Fitting tolerance to use.")
        backwardsCompatParser.add_argument("--line_list",
                                           help="List of lines to always attempt fits.")
        backwardsCompatParser.add_argument('-P', "--path_base",
                                           help="Output file path and file prefix.")
        backwardsCompatParser.add_argument('-O', "--output",
                                           help="Output filename.")
        # backwardsCompatParser.add_argument('-I', "--save_temp", )
        # backwardsCompatParser.add_argument('-A', "--plot_all", )
        # backwardsCompatParser.add_argument('', "--flux_calibrated", )
        # backwardsCompatParser.add_argument('-r', "--deblend_radius", nargs=1)
        # backwardsCompatParser.add_argument('', "--deblend_ratio", nargs=1)
        # backwardsCompatParser.add_argument('-d', "--deblend_iterations", nargs=1)
        # backwardsCompatParser.add_argument('', "--naive_find_lines", )
        # backwardsCompatParser.add_argument('-f', "--find_sigma", nargs=1)
        # backwardsCompatParser.add_argument('', "--wavelength_min_error", nargs=1)
        # backwardsCompatParser.add_argument('', "--wavelength_max_error", nargs=1)
        # backwardsCompatParser.add_argument('', "--wavelength_limit", nargs=1)
        # backwardsCompatParser.add_argument('', "--radial_velocity", nargs=1)
        # backwardsCompatParser.add_argument('', "--measure_radial_velocity", nargs=1)
        # backwardsCompatParser.add_argument('', "--radial_velocity_range", nargs=1)
        # backwardsCompatParser.add_argument('', "--radial_velocity_error", nargs=1)
        # backwardsCompatParser.add_argument('', "--radial_velocity_step", nargs=1)
        # backwardsCompatParser.add_argument('', "--radial_velocity_sigma", nargs=1)
        # backwardsCompatParser.add_argument('', "--loosen", )
        # backwardsCompatParser.add_argument('', "--strict_center", )
        # backwardsCompatParser.add_argument('', "--strict_width", )
        # backwardsCompatParser.add_argument('', "--strict_flux", )
        # backwardsCompatParser.add_argument('', "--fits_row", nargs=1)
        BCparsed, unparsed = backwardsCompatParser.parse_known_args(unparsed)
        if "verbose" in vars(BCparsed).keys():
            verboseLevels = {0: logging.CRITICAL,
                             1: logging.ERROR,
                             2: logging.WARNING,
                             3: logging.INFO,
                             4: logging.DEBUG,
                             5: logging.NOTSET}
            try:
                self.verbose = verboseLevels[BCparsed.verbose]
            except KeyError:
                # Assume you pounded the "v" key infinity times.
                self.verbose = logging.NOTSET
            self.log.setLevel(self.verbose)
        if "path_base" in vars(BCparsed).keys():
            arguments['fitting']['path_base'] = BCparsed.path_base
            if BCparsed.path_base is not None:
                logfile = logging.FileHandler(filename=BCparsed.path_base + ".log", mode="w")
                # This is an ugly hack.
                logfile.setFormatter(self.mainLog.root.handlers[0].formatter)
                self.mainLog.addHandler(logfile)
        if "continuum_box" in vars(BCparsed).keys():
            arguments['continuum']['box_size'] = BCparsed.continuum_box
        if "iterations" in vars(BCparsed).keys():
            arguments['fitting']['max_iterations'] = BCparsed.iterations
        if "tolerance" in vars(BCparsed).keys():
            arguments['fitting']['tolerance'] = BCparsed.tolerance
        if "line_list" in vars(BCparsed).keys():
            arguments['fitting']['line_list'] = BCparsed.line_list
        if "output" in vars(BCparsed).keys():
            arguments['fitting']['output'] = BCparsed.output

        if len(unparsed) > 0:
            arguments['fitting']['spectrum_file'] = unparsed.pop(0)
        if len(unparsed) > 0:
            self.log.warning(f"Unparsed arguments: {unparsed}")

        return arguments

    def read_spectrum(self, spectrum_file=None):
        S = self.construct_spectra_class(None, **self.arg_dict)

        if spectrum_file is not None:
            self.spectrum_file = spectrum_file
        S = io.read_ascii_spectrum(self.spectrum_file, spectrum=S)
        S.L = io.read_ascii_linelist(self.line_list, lines=None) if self.line_list is not None else []
        S.log.debug(f"spectrum structure: {dir(S)}")

        return S

    def write_results(self, spectrum):
        if spectrum is None:
            raise RuntimeError("No spectrum supplied for writing.")
        if self.path_base is None:
            outfile = None
            outfile2 = None
        else:
            if self.iteration < self.max_iterations - 1 and False:
                outfile = ("%s.iter%d.robolines" % (self.path_base, self.iteration))
                outfile2 = ("%s.iter%d.robospect" % (self.path_base, self.iteration))
            else:
                outfile = ("%s.robolines" % (self.path_base))
                outfile2 = ("%s.robospect" % (self.path_base))
        io.write_ascii_catalog(outfile, spectrum.L)
        io.write_ascii_spectrum(outfile2, spectrum)

        io.plots.plot_lines(spectrum, output=f"{self.path_base}.pdf",
                            width=5.0, all=False)

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
        for i in inheritance_list:
            self.log.debug(i)

        class Spectra(*inheritance):
            def __init__(self, *args, **kwargs):
                if "verbose" in kwargs.keys():
                    self.verbose = kwargs["verbose"]
                    self.log = logging.getLogger("robospect.spectra")
                    self.log.setLevel(self.verbose)
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

        return Spectra(*args, **kwargs, verbose=self.verbose)
