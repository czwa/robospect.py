#!/usr/bin/env python3

import sys
sys.path.append('/home/czw/project/2019/robospect.py/python/')
sys.path.append('/home/czw/jhome/robospect.py/python/')

import robospect as RS

print("Setup config")
C = RS.config.Config([ "-R", "value", "400",
                      "-F", "path_base", "/tmp/zzz",
                       "-O", "/tmp/out.spect",
                       "/tmp/in.spect"],
                     repair={'value': 300},
                     deblend={"radius": 2.5},
)

#print("Read spectrum")
#SS = C.read_spectrum("/home/czw/project/2019/robospect.py/tests/data/goodred.spect")

# RS.plot_spectrum(SS, min=4860, max=5000, errors=True,
#                  autoscale=False, output="/tmp/plotA.png")



# print("Do fits")
# SS.fit_continuum()
# SS.fit_continuum(box_size=20.0)
# print(SS.continuum)
# SS.fit_detection()
# SS.fit_initial()

# RS.plot_spectrum(SS, min=5160, max=5180,
#                  autoscale=False, errors=True, output="/tmp/plotB.png")
# RS.write_ascii_catalog("/tmp/catA.dat", SS.L)

