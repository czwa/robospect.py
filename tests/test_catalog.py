import unittest
import os
import hashlib
import pickle
import numpy as np
import robospect as RS

TestDir = os.path.dirname(__file__)

class Test_Catalog(unittest.TestCase):

    def test_init(self):
        C = RS.Catalog()

    def test_fields(self):
        C = RS.Catalog()

        C._id(name="testField", unit="mm", index=None, header="Test Field", default=21.2121)

    def test_rows(self):
        C = RS.Catalog()

        Values = {'chi': 100.0, 'altChi': 200.0, 'chiDof': 33,
                  'comment': "A test value 1."}
        C.append(1300.0, **Values)

        Values = {'chi': 150.0, 'altChi': 250.0, 'chiDof': 66,
                  'comment': "A test value 2."}
        C.append(200.0, **Values)

        C.to_ascii("/tmp/asdf_unittest.rs")

        C.sort()
        C.to_ascii("/tmp/sort_unittest.rs")

