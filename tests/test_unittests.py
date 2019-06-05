import unittest
import os
import hashlib
import pickle
import numpy as np

import robospect as RS

TestDir = os.path.dirname(__file__)

def hash_data_structure(data):
    pkl = pickle.dumps(data)
    return hashlib.md5(pkl).hexdigest()

class Test_Config_Methods(unittest.TestCase):

    def test_init(self):
        pass

    def test_parse(self):
        pass

    def test_read_spectrum(self):
        pass

    def test_write_results(self):
        pass

    def test_construct_spectra_class(self):
        pass


class Test_IO_Methods(unittest.TestCase):

    def test_read_ascii_linelist(self):
        lines = RS.read_ascii_linelist(f"{TestDir}/data/linelistjkh.in")

        self.assertEqual(hash_data_structure(lines),
                         "bcc382ffdff91bd320f503819f6e4047")

    def test_read_ascii_spectrum(self):
        spectrum = RS.read_ascii_spectrum(f"{TestDir}/data/goodblue.spect")

        spectrum.log = None  # log is unpickleable.

        print(hash_data_structure(spectrum))
        self.assertIsInstance(spectrum, RS.spectra.spectrum)

    def test_write_ascii_spectrum(self):
        pass

    def test_write_ascii_catalog(self):
        pass


class Test_Lines(unittest.TestCase):

    def test_init(self):
        pass

    def test_fdf(self):
        pass

    def test_sortLines(self):
        pass

class Test_Flags(unittest.TestCase):

    def test_init(self):
        pass

    def test_values(self):
        pass

    def test_doc(self):
        pass


class Test_Spectra(unittest.TestCase):

    def test_init(self):
        pass

    def test_fit(self):
        pass

    def test_update(self):
        pass


class Test_Model_Methods(unittest.TestCase):

    def spectrum_sim(self, min_wavelength=4900, max_wavelength = 5000, resolution=0.01,
                     noise=0.01, lines=None, func=None):
        C = RS.Config()
        S = C.construct_spectra_class()

        S.x = np.arange(min_wavelength, max_wavelength, resolution)
        S.y = np.ones_like(S.x) + np.random.normal(loc=0.0, scale=noise, size=S.x.size)
        S.e0 = np.zeros_like(S.x)

        S.continuum = np.ones_like(S.x)
        S.lines = np.zeros_like(S.x)
        S.alternate = np.zeros_like(S.x)
        S.error = np.ones_like(S.x)

        S.comment = []
        S.filename = "SIM"

        if lines is not None and func is not None:
            for l in lines:
                S.y += func(S.x, l.Q)
        C.path_base = "/tmp/czw_utX"
        C.write_results(S)
        return S

    def test_continuum_boxcar(self):
        S = self.spectrum_sim()

        S.fit_continuum()
        z_deviation = (S.y - np.ones_like(S.y)) / S.error

        print(z_deviation)
        pass
#        self.assertLess(np.nanmean(z_deviation), 1.0)

    def test_detection_naive(self):
        L_truth = []
        L_truth.append( RS.line(4925.0, 3, Q=np.array([4925.03, 0.05, -.15])) )
        L_truth.append( RS.line(4935.0, 3, Q=np.array([4935.03, 0.06, -.10])) )
        L_truth.append( RS.line(4945.0, 3, Q=np.array([4945.03, 0.07, -.17])) )
        L_truth.append( RS.line(4955.0, 3, Q=np.array([4955.03, 0.08, -.12])) )

        G = RS.profile_shapes.gaussian()
        S = self.spectrum_sim(lines=L_truth, func=G)

        S.fit_detection()
        for l in S.L:
            print(l)
        pass

    def test_line_gauss_guess(self):
        L_truth = []
        L_truth.append( RS.line(4925.0, 3, Q=np.array([4925.03, 0.05, -.15])) )
        L_truth.append( RS.line(4935.0, 3, Q=np.array([4935.03, 0.06, -.10])) )
        L_truth.append( RS.line(4945.0, 3, Q=np.array([4945.03, 0.07, -.17])) )
        L_truth.append( RS.line(4955.0, 3, Q=np.array([4955.03, 0.08, -.12])) )

        L_init = []
        L_init.append( RS.line(4925.0, 3) )
        L_init.append( RS.line(4935.0, 3) )
        L_init.append( RS.line(4945.0, 3) )
        L_init.append( RS.line(4955.0, 3) )

        G = RS.profile_shapes.gaussian()
        S = self.spectrum_sim(lines=L_truth, func=G)
        S.L = L_init
        S.fit_initial()
        S.line_update()

        for l in S.L:
            print(l)
        pass

    def test_line_nlls(self):
        L_truth = []
        L_truth.append( RS.line(4925.0, 3, Q=np.array([4925.03, 0.05, -.15])) )
        L_truth.append( RS.line(4935.0, 3, Q=np.array([4935.03, 0.06, -.10])) )
        L_truth.append( RS.line(4945.0, 3, Q=np.array([4945.03, 0.07, -.17])) )
        L_truth.append( RS.line(4955.0, 3, Q=np.array([4955.03, 0.08, -.12])) )

        L_init = []
        L_init.append( RS.line(4925.0, 3) )
        L_init.append( RS.line(4935.0, 3) )
        L_init.append( RS.line(4945.0, 3) )
        L_init.append( RS.line(4955.0, 3) )

        G = RS.profile_shapes.gaussian()
        S = self.spectrum_sim(lines=L_truth, func=G)
        S.L = L_init
        S.fit_initial()
        S.line_update()
        S.fit_lines()

        for l in S.L:
            print(l)
        pass

    def test_noise_boxcar(self):
        pass


class Test_Profile_Methods(unittest.TestCase):

    def test_profileFromName(self):
        pass

    def test_profile(self):
        pass

    def test_gaussian(self):
        pass

    def test_voigt(self):
        pass

    def test_skewgauss(self):
        pass

    def test_lorentzian(self):
        pass

    def test_planck(self):
        pass


if __name__ == '__main__':
    unittest.main()
