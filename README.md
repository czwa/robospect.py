# robospect.py
Python port of ROBOSPECT [(Waters & Hollek, 2013, PASP, 125, 1164)](https://www.jstor.org/stable/10.1086/673311).

This program was designed to accurately measure the equivalent widths
of line features in stellar spectra in an automated fashion, removing
the manual decisions necessary in previous methods.  This updated port
of the program builds upon a modern python foundation to improve the
usability and extensibility of the algorithms used in the original
version.


## Installation

We recommend using the most recent release tagged version of the code
from the public github repository: https://github.com/czwa/robospect.py

To install the package:

      > python3 ./setup.py install [--user] [--local-snapshots-ok]

The current set of unit tests will confirm that the code is operational:

      > python3 ./setup.py test

## Running

A future release will ensure all options from the previous version of
ROBOSPECT are functional.  The examples below list some common calls.

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

