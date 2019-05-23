import unittest
import os
import numpy as np
import matplotlib.pyplot as plt

import robospect as RS

TestDir = os.path.dirname(__file__)


def read_spect(path_base):
    # Read previous file
    file_x = []
    file_y = []
    file_e = []
    file_c = []
    file_l = []
    filename = path_base + ".robospect"
    with open(filename, "r") as f:
        for entry in f:
            if not entry.startswith("#"):
                wavelength, flux, error, continuum, lines, model, ff = entry.split()
                file_x.append(float(wavelength))
                file_y.append(float(flux))
                file_e.append(float(error))
                file_c.append(float(continuum))
                file_l.append(float(lines))
    return file_x, file_y, file_e, file_c, file_l

def read_lines(path_base):
    filename = path_base + ".robolines"
    lines = []

    with open(filename, "r") as f:
        for entry in f:
            if not entry.startswith("#"):
                t = entry.split()
                L = RS.line(float(t[0]), Nparam=4, comment=t[17], flags=t[15], blend=t[16])
                L.Q = (float(t[1]), float(t[2]), float(t[3]), float(t[4]))
                L.dQ = (float(t[5]), float(t[6]), float(t[7]), float(t[8]))
                L.pQ = (float(t[9]), float(t[10]), float(t[11]), 0.0)
                lines.append(L)
    return lines

def run_current(path_base, *args):
    filename = path_base + ".robospect"
    rs_args = list(args)
    rs_args.append(filename)

    C = RS.config.Config(rs_args)
    S = C.read_spectrum()
    S.fit()
    C.path_base = "/tmp/czw_test"
    C.write_results(spectrum=S)
    return S.x, S.y, S.error, S.continuum, S.lines, S.L

def lines_compare(plot_key, pre_key, l1, l2):
    if plot_key is None:
        plot_key = ""

    l1.sort(key=RS.sortLines)
    l2.sort(key=RS.sortLines)

    x  = []
    dm = []
    ds = []
    dF = []

    j = 0
    R = 1e-3
    for i, ll1 in enumerate(l1):
        R = 1e-3
        jt = -1
        for j, ll2 in enumerate(l2):
            # Yes, but I'm hungry, so I'm sucking up the O(N*M) for today.
            Rt = np.abs(float(ll1.x0) - float(ll2.x0))
            if Rt < R:
                R = Rt
                jt = j
        if jt != -1:
            ll2 = l2[jt]

            x.append(ll1.x0)

            if pre_key is True:
                dm.append(ll1.pQ[0] - ll2.pQ[0])
                ds.append(ll1.pQ[1] - ll2.pQ[2])
                dF.append(ll1.pQ[2] - ll2.pQ[2])
            else:
                dm.append(ll1.Q[0] - ll2.Q[0])
                ds.append(ll1.Q[1] - ll2.Q[2])
                dF.append(ll1.Q[2] - ll2.Q[2])
    # Close matching loop
    plt.xlim(x[0], x[-1])
    plt.ylim(-0.2, 0.2)
    plt.xlabel("wavelength")
    plt.ylabel(f"ref - fit")
    plt.title(f"line comparison")

    plt.plot(x, dm, 'ro', ms=5, label="mean")
    plt.plot(x, ds, 'bs', ms=5, label="sigma")
    plt.plot(x, dF, 'g^', ms=5, label="flux")
    plt.legend(loc="upper left")
    plt.savefig(f"/tmp/test_{plot_key}_lineParam.png")
    plt.clf()


def spect_compare(plot_key, path_base, *args):
    if plot_key is None:
        plot_key = ""

    file_x, file_y, file_e, file_c, file_l = read_spect(path_base)
    file_Lines = read_lines(path_base)
    current_x, current_y, current_e, current_c, current_l, current_Lines = run_current(path_base, *args)

    if len(file_x) != len(current_x):
        raise RuntimeError("Did not recieve arrays of the same length!")

    # lines is defined differently now.
    current_l = current_c - current_l
    diff_l = file_l - current_l
    diff_e = file_e - current_e
    diff_c = file_c - current_c

    plt.xlim(file_x[0], file_x[-1])
    plt.xlabel("wavelength")

    for p1, p2, name in zip([file_l, file_e, file_c],
                            [current_l, current_e, current_c],
                            ["model", "errors", "continuum"]):
        ymin, ymax = np.percentile(p1, [0.0, 100.0])
        plt.ylim(ymin - 0.1, ymax + 0.1)
        plt.title(f"{plot_key}")
        plt.ylabel(f"{name}")
        plt.plot(file_x, p1, color='r', label="v2.14")
        plt.plot(file_x, p2, color='b', label="current")
        plt.legend(loc="upper left")
        plt.savefig(f"/tmp/test_{plot_key}_{name}.png")
        plt.clf()

    outF = open(f"/tmp/{plot_key}.dat", "w")
    for compare, name in zip([diff_l, diff_e, diff_c],
                             ["model", "errors", "continuum"]):
        ymin, ymax = np.percentile(compare, [0.0, 100.0])
        plt.ylim(ymin - 0.1, ymax + 0.1)
        plt.title(f"{plot_key}")
        plt.ylabel(f"diff {name}")
        plt.plot(file_x, compare, color='k')
        plt.savefig(f"/tmp/test_{plot_key}_diff_{name}.png")
        plt.clf()

        P = np.percentile(compare, [16.0, 25.0, 50.0, 75.0, 84.0])
        outF.write("%10s  %f %f %f %f\n            %f %f %f %f %f\n" %
                   (name,
                    np.mean(compare), np.std(compare),
                    np.min(compare), np.max(compare),
                    P[0], P[1], P[2], P[3], P[4]))
    outF.write("LINES:  %d %d\n" % (len(file_Lines), len(current_Lines)))
    lines_compare(plot_key, True, file_Lines, current_Lines)


def test_blue():
   spect_compare("blue", f"{TestDir}/v2.14run/blue.out_iter1")

def test_red():
    spect_compare("red", f"{TestDir}/v2.14run/red.out_iter1")


if __name__ == "__main__":
    test_red()
    unittest.main()


