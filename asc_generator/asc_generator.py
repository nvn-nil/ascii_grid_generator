import os

import numpy as np

REQUIRED_HEADERS = ["ncols", "nrows", "xllcorner", "yllcorner", "cellsize", "nodata_value"]


def read_ascii_grid_headers(file_path):
    """Returns the ascii grid (.asc) file's headers.

    :param file_obj: Filename of an ascii grid file
    :type file_obj: FieldFile
    :return : ascii grid file headers
    :rtype  : dict
    :raises TypeError: When there is an issue reading and processing the file headers
    """
    headers = {}

    with open(file_path, "r", encoding="UTF-8") as fi:
        for line_num in range(6):
            try:
                header_line = fi.readline().strip()
                header_key, value = header_line.split()

                header_key = header_key.lower()
                value = int(value) if float(value).is_integer() else float(value)

                headers[header_key] = value
            except Exception:
                print("Error reading header line", line_num + 1)
                raise

    if not all(key in headers for key in REQUIRED_HEADERS):
        raise ValueError(f"Asc file does not have all the required header. Headers: {list(headers.keys())}")

    return headers


class AsciiGenerator:
    def __init__(
        self,
        file_like=None,
        number_of_rows=None,
        number_of_columns=None,
        xll_corner=None,
        yll_corner=None,
        cellsize=None,
        nodata_value=None,
    ):
        if not file_like and not (
            number_of_rows and number_of_columns and xll_corner and yll_corner and nodata_value and cellsize
        ):
            raise ValueError("file_like or ascii grid headers must be specified")

        self._file_like = file_like

        self.asc_headers = self.get_asc_headers(
            file_like, number_of_rows, number_of_columns, xll_corner, yll_corner, cellsize, nodata_value
        )

    def get_asc_headers(
        self, file_like, number_of_rows, number_of_columns, xll_corner, yll_corner, cellsize, nodata_value
    ):
        if file_like and os.path.isfile(file_like):
            return read_ascii_grid_headers(file_like)

        return {
            "nrows": number_of_rows,
            "ncols": number_of_columns,
            "xllcorner": xll_corner,
            "yllcorner": yll_corner,
            "cellsize": cellsize,
            "nodata_value": nodata_value,
        }

    def generate_new_ascii_grid(
        self,
        new_filepath,
        default_element,
        function_order=None,
        every_element_function=None,
        every_row_function=None,
        every_column_function=None,
        single_run_function=None,
        fmt="%d",
        fillna=True,
    ):
        if not new_filepath or not default_element:
            raise Exception("Filepath or default_element for the new file missing")

        matrix = self.generate_initial_matrix(self._file_like, default_element)

        if function_order is None:
            function_order = set()

        if callable(every_row_function):
            function_order.add(every_row_function)

        if callable(every_column_function):
            function_order.add(every_column_function)

        if callable(every_element_function):
            function_order.add(every_element_function)

        if callable(single_run_function):
            function_order.add(single_run_function)

        for func in function_order:
            matrix = func(matrix, self.asc_headers)

        self.write_matrix(new_filepath, matrix, fmt=fmt, fillna=fillna)

    def generate_initial_matrix(self, file_like, default_element):
        rows = self.asc_headers["nrows"]
        cols = self.asc_headers["ncols"]

        if file_like is not None and os.path.isfile(file_like):
            matrix = self.read_matrix_from_ascii_grid_file(file_like)
        else:
            matrix = np.ones((rows, cols)) * default_element

        return matrix

    def read_matrix_from_ascii_grid_file(self, filepath):
        return np.loadtxt(filepath, skiprows=6)

    def write_matrix(self, filepath, data, fmt="%d", fillna=True):
        if fillna:
            data[np.isnan(data)] = 0
        np.savetxt(
            filepath,
            data,
            header="\n".join([f"{k}\t{v}" for k, v in self.asc_headers.items()]),
            fmt=fmt,
            comments="",
            delimiter="\t",
        )
