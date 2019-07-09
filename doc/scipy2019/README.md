# Porting ROBOSPECT to Python:  Removing the Complexity of Software for Scientists

## Goal:

The code was originally designed to measure the equivalent width of
spectral lines in stellar spectra.  Methods tuned to provide accurate
results even when the signal-to-noise ratio was less than optimal.

## What is a "stellar spectrum"?

- Electrons in atoms have fixed transitions governed by quantum mechanics.
- These transitions create or absorb photons with a given wavelength/color.
  - Each element has a unique signature of expected transition wavelengths.
  - This is why neon signs have a characteristic red glow.
- Prisms disperse light (such as from the Sun) into component
  wavelengths.  A spectrum is just a plot of the relative intensity of
  the light at each wavelength.
- By measuring how much light is absorbed at predicted wavelengths,
  the chemical composition of the star can be obtained.
  - The equivalent width is a way to quantify the absorption for lines
    of different profile shapes.
- Other parameters can also be estimated from the same data,
  including the temperature and density of the star.
- One of the primary means of obtaining information about the objects
  in our universe.

## Original version of the code:

- Written in C.
- Designed for speed, with a large number of hand tuned algorithms.
- Base math library immediately had API change.
  - Scientists don't want to fight computers all day.
  - Even though most scientists end up fighting computers all day.
- Although it was initially popular, maintenance (and day jobs)
  prevented wide adoption.

## Why python?

- Standard component of many astronomy grad school programs.
- Easy to use, with a common set of libraries (scipy, numpy, astropy).
- Easy to install and update libraries.
- Easy to develop for:
  - Vector operations: clearer code/fewer loops and iterators.
  - Multiprocessing trivial to do out of the box, making this kind of
    embarassingly parallel problem easy to speed up.
  - Easy to extend, and we already have a list of new features to add:
    - Gaussian process/b-spline continuum levels.
    - FFT-based matched filter detection.
    - Radial velocity measurement from shifts in the spectral lines.
  - Quick visualization and code diagnostics via matplotlib/notebooks.
- Object oriented code allows for easy code modularity.

## Initial release:

- Open source github repository.
- Previous release had little community development, although there
  were numerous feature requests.
- Hope to promote more community interest by making modular features
  easy to include.
- Already have one team anticipating the release.
  - Python will allow them to tie their measurement/analysis codes into
    a single data reduction pipeline.

