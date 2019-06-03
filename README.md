# robospect.py
Python port of robospect

The current working codebase is on the master branch.  Full
documentation is forthcoming, but a few example run commands are
listed below.

To install the package:
      > python3 ./setup.py install [--user]
or
      > python3 ./setup.py develop [--user]
depending on if code development will be performed.

Tests are not currently complete, but will check that your environment
has robospect configured correctly.  These can be accessed via:

      > python3 ./setup.py test

Example commands:

      > rSpect.py -i 1 ./spectra/input_spectrum.dat -P /tmp/output_base_name

      ## Run a single iteration on `input_spectrum.dat`, producing
      ## output files `/tmp/output_base_name.robospect` (the fit
      ## spectrum, with continuum and line components separated) and
      ## `/tmp/output_base_name.robolines` (the output line catalog).

      > rSpect.py -i 5 ./spectra/input_spectrum.dat -P /tmp/output_base_name -C name null -N name boxcar

      ## As above, this time running five fit iterations.  The
      ## continuum is not fit, and assumed to be equal to unity at all
      ## wavelengths.  The empirical noise estimate still runs, using
      ## the boxcar algorithm.

      > rSpect.py -i 1 ./spectra/input_spectrum.dat -P /tmp/output_base_name --line_list ./spectra/lines.dat

      ## Use default fitting algorithms, but use a list of known lines
      ## to include in the measurements, regardless of their
      ## signal-to-noise.

