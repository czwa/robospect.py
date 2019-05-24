import unittest
import os
import hashlib
import pickle

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

        self.assertEqual(hash_data_structure(spectrum),
                         "bacd6e9003d7b47e5e0ed57e0cb24f91")

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

    def test_continuum_boxcar(self):
        pass

    def test_detection_naive(self):
        pass

    def test_line_gauss_guess(self):
        pass

    def test_line_nlls(self):
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
