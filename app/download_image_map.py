#!/usr/bin/env python
""" config file parser """

import csv

class Parser():
    """ config file parser """
    def __init__(self, csv_file=None):
        self._parsed_data = None
        self.csv_file = csv_file
        # other useful things here

    @property
    def parsed_data(self):
        """ return the parsed data """
        if self._parsed_data is not None:
            return self._parsed_data
        self._parsed_data = self.get_data()
        return self._parsed_data

    def transform_csv_data(self, data):
        """ transform the parsed data """
        transformed = {}
        key = ""
        row_counter = 0
        for line in data:
            try:
                row_counter = row_counter + 1
                key = line[0]
                transformed[key] = line[1]
            except IndexError as error_message:
                # pylint: disable=line-too-long
                print(f"userdata.csv line {row_counter}: Malformed or Missing fields in data '{line}'. Error: '{error_message}'")
        return transformed

    def import_csv(self):
        """ import the csv file """
        with open(self.csv_file) as csv_file_handle:
            csvreader = csv.reader(csv_file_handle, delimiter='|')
            data = list(csvreader)
        return data

    def get_data(self):
        """ output the transformed data """
        data = self.import_csv()
        return self.transform_csv_data(data)

    def reload(self):
        """ reload the configuration """
        self._parsed_data = None
        self.get_data()
        return self.parsed_data
