""" manage iterating through mirrors and return appropriate one based by region """

from download_image_map import Parser

class Mirror():
    """ implements the mirror selection functionality """
    def __init__(self, mode: str, mirror_list):
        self.mode = mode
        self.mirror_list = mirror_list
        self._list_position = dict()
        self._list_max = dict()
        self.mirror_list['default'] = list(mirror_list['NA'] + mirror_list['EU'])
        #pylint: disable=unnecessary-comprehension
        self.continents = [ continent for continent in mirror_list.keys() ]
        for region in list(mirror_list.keys()):
            self._list_position[region] = 0
            self._list_max[region] = len(mirror_list[region]) - 1

        if mode == "dl_map":
            parser = Parser('userdata.csv')
            self.dl_map = parser.parsed_data
        else:
            self.dl_map = None

    # set defaults to None in param list, then actually set inside
    # body to avoid scope change
    def increment(self, region=None):
        """ move to next element regions mirror list and return list position"""
        if region is None:
            region = 'default'
        if self._list_position[region] == self._list_max[region]:
            self._list_position[region] = 0
        else:
            self._list_position[region] = self._list_position[region] + 1

    def next(self, region=None):
        """ return next mirror in rotation """
        if region is None:
            region = 'default'
        self.increment(region)
        return self.mirror_list[region][self._list_position[region]]

    def all_mirrors(self):
        """ return all mirrrors configured """
        return self.mirror_list

    def all_regions(self):
        """ return list of regions configured """
        return self.continents
