#!/usr/bin/env python3

import sys
sys.path.append('/home/czw/project/2019/robospect.py/python/')

import robospect as RS

print("Setup config")
C = RS.config.Config()
print("Read spectrum")
SS = C.read_spectrum("/home/czw/project/2019/robospect.py/tests/data/goodred.spect")

RS.plot_spectrum(SS, min=4860, max=5000, errors=True,
                 autoscale=False, output="/tmp/plotA.png")



print("Do fits")
SS.fit_continuum()
print(SS.continuum)
SS.fit_detection()
SS.fit_initial()

RS.plot_spectrum(SS, min=5160, max=5180,
                 autoscale=False, errors=True, output="/tmp/plotB.png")
RS.write_ascii_catalog("/tmp/catA.dat", SS.L)

