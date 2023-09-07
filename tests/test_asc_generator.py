import unittest

import numpy as np

from ascii_grid_generator import AsciiGenerator


class TestAsciiGenerator(unittest.TestCase):
    def test_annual_power_map_generator(self):
        def build_annual_power_map(matrix, asc_headers):
            new_matrix = matrix.copy()
            new_matrix = 0.5 * 1.225 * np.power(matrix, 3) * 24 * 365.25

            new_matrix[matrix == asc_headers["nodata_value"]] = asc_headers["nodata_value"]
            return new_matrix

        asc = AsciiGenerator(file_like=r"tests\data\wind_map.asc")
        asc.generate_new_ascii_grid(
            r"tests\data\annual-energy-map.asc", -9999, single_run_function=build_annual_power_map
        )
