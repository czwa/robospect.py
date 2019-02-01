#!/usr/bin/env python3

import sys
sys.path.append('/home/czw/jhome/robospect.py/python/')

import robospect as RS

print("Read spectrum")
D = RS.read_ascii_spectrum("./data/goodred.spect")
print(D)
print(D.x)
print(D.y)
print(D.continuum)
# RS.plot_spectrum(D, min=5800, max=5900, autoscale=False)
print(RS)

print("")
print("Setup config")
C = RS.Config(filename="./data/goodred.spect")
C.detection_model = RS.detection_naive.detection_naive
C.continuum_model = RS.continuum_boxcar.continuum_boxcar
print(C)

print("")
print("Copy data")
SS = C.construct_spectra_class()
SS.copy_data(D)

print(SS)
print(D)

print("")
print("Do fits")
SS.fit_continuum()
print(SS.continuum)

# RS.plot_spectrum(SS(), min=4860, max=5000, autoscale=False, errors=True)
SS.fit_detection()
for l in SS.L:
    print("%f %s %s" % (l.x0, l.Q, l.comment))
print(len(SS.L))


