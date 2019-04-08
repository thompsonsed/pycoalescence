"""
Generate landscapes and check map file combinations. Child class for :class:`.Simulation` and
:class:`.DispersalSimulation`. Contains :class:`.Map` objects for each relevant map file internally.
"""
import copy
import logging

from .map import Map
from .system_operations import check_file_exists, create_logger


class Landscape:
    """
    Calculates offsets and dimensions of a selection of tif files making up a landscape.
    """

    def __init__(self):
        """
        Initialises the default variables for the Landscape object.
        """
        self.coarse_scale = 1
        self.is_setup_map = False
        self.setup_complete = False
        self.fine_map = Map()
        self.coarse_map = Map()
        self.sample_map = Map()
        # Historical map parameters
        # Rate of habitat change that occurs before historical state
        self.habitat_change_rate = 0
        self.gen_since_historical = 1  # The number of generations ago a habitat was historical
        self.historical_fine_map_file = None
        self.historical_coarse_map_file = None
        self.historical_fine_list = []
        self.historical_coarse_list = []
        self.times_list = []
        self.rates_list = []
        self.logging_level = 10
        self.logger = logging.Logger("pycoalescence.landscape")
        self.landscape_type = False

    def _create_logger(self, file=None, logging_level=None, **kwargs):
        """
        Creates the logger for use with NECSim simulation. Note you can supply your own logger by over-riding
        self.logger. This function should only be run during self.__init__()

        :param file: file to write output to. If None, outputs to terminal
        :param logging_level: the logging level to use (defaults to INFO)
        :param kwargs: additional keyword arguments to write out to

        :return: None
        """
        if logging_level is None:
            logging_level = self.logging_level
        self.logger = create_logger(self.logger, file, logging_level, **kwargs)

    def add_historical_map(self, fine_file, coarse_file, time, rate=0.0):
        """
        Adds an extra map to the list of historical maps.

        :param str fine_file: the historical fine map file to add
        :param str coarse_file: the historical coarse map file to add
        :param time: the time to add (when the map is accurate)
        :param rate: the rate to add (the rate of habitat change at this time)
        """
        if not self.historical_fine_map_file or self.historical_fine_map_file == "none":
            self.historical_fine_map_file = fine_file
            self.historical_coarse_map_file = coarse_file
            self.gen_since_historical = time
            self.habitat_change_rate = rate
        self.historical_fine_list.append(fine_file)
        self.historical_coarse_list.append(coarse_file)
        self.times_list.append(time)
        self.rates_list.append(rate)

    def sort_historical_maps(self):
        """
        Sorts the historical maps by time.
        """
        if len(self.historical_fine_list) > 0 or len(self.historical_coarse_list) > 0:
            if any(
                len(self.historical_fine_list) != len(x)
                for x in [self.historical_coarse_list, self.times_list, self.rates_list]
            ):
                raise ValueError("Discrepancy between historical file list, time list or rate list. Check inputs: {}")
            self.times_list, self.historical_fine_list, self.historical_coarse_list, self.rates_list = [
                list(x)
                for x in zip(
                    *sorted(
                        zip(self.times_list, self.historical_fine_list, self.historical_coarse_list, self.rates_list)
                    )
                )
            ]

    def set_map(self, map_file, x_size=None, y_size=None):
        """
        Quick function for setting a single map file for both the sample map and fine map, of dimensions x and y.
        Sets the sample file to "null" and coarse file and historical files to "none".

        :param str map_file: path to the map file
        :param int x_size: the x dimension, or None to detect automatically from the ".tif" file
        :param int y_size: the y dimension, or None to detect automatically from the ".tif" file
        """
        if (x_size is None or y_size is None) and (x_size is not None or y_size is not None):
            raise ValueError("Must specify both a map x and y dimension.")
        self.fine_map.set_dimensions(map_file, x_size=x_size, y_size=y_size)
        self.fine_map.zero_offsets()
        self.sample_map.set_dimensions("null", self.fine_map.x_size, self.fine_map.y_size)
        self.sample_map.zero_offsets()
        self.coarse_map.set_dimensions("none", self.fine_map.x_size, self.fine_map.y_size)
        self.coarse_map.zero_offsets()
        self.is_setup_map = True
        self.coarse_scale = 1.0

    def set_map_files(
        self, sample_file, fine_file=None, coarse_file=None, historical_fine_file=None, historical_coarse_file=None
    ):
        """
        Sets the map files (or to null, if none specified). It then calls detect_map_dimensions() to correctly read in
        the specified dimensions.

        If sample_file is "null", dimension values will remain at 0.
        If coarse_file is "null", it will default to the size of fine_file with zero offset.
        If the coarse file is "none", it will not be used.
        If the historical fine or coarse files are "none", they will not be used.

        :param str sample_file: the sample map file. Provide "null" if on samplemask is required
        :param str fine_file: the fine map file. Defaults to "null" if none provided
        :param str coarse_file: the coarse map file. Defaults to "none" if none provided
        :param str historical_fine_file: the historical fine map file. Defaults to "none" if none provided
        :param str historical_coarse_file: the historical coarse map file. Defaults to "none" if none provided

        :rtype: None

        :return: None
        """
        if fine_file in [None, "null", "none"]:
            raise ValueError(
                "Fine map file cannot be 'none' or 'null' for automatic parameter detection."
                "Use set_map_parameters() instead."
            )
        if coarse_file is None:
            coarse_file = "none"
        if historical_fine_file is None:
            historical_fine_file = "none"
        if historical_coarse_file is None:
            historical_coarse_file = "none"
        self.set_map_parameters(
            sample_file,
            0,
            0,
            fine_file,
            0,
            0,
            0,
            0,
            coarse_file,
            0,
            0,
            0,
            0,
            0,
            historical_fine_file,
            historical_coarse_file,
        )
        try:
            self.detect_map_dimensions()
        except Exception as e:
            self.is_setup_map = False
            raise e

    def set_map_parameters(
        self,
        sample_file,
        sample_x,
        sample_y,
        fine_file,
        fine_x,
        fine_y,
        fine_x_offset,
        fine_y_offset,
        coarse_file,
        coarse_x,
        coarse_y,
        coarse_x_offset,
        coarse_y_offset,
        coarse_scale,
        historical_fine_map,
        historical_coarse_map,
    ):
        """

        Set up the map objects with the required parameters. This is required for csv file usage.

        Note that this function is not recommended for tif file usage, as it is much simpler to call set_map_files() and
        which should automatically calculate map offsets, scaling and dimensions.

        :param sample_file: the sample file to use, which should contain a boolean mask of where to sample
        :param sample_x: the x dimension of the sample file
        :param sample_y: the y dimension of the sample file
        :param fine_file: the fine map file to use (must be equal to or larger than the sample file)
        :param fine_x: the x dimension of the fine map file
        :param fine_y: the y dimension of the fine map file
        :param fine_x_offset: the x offset of the fine map file
        :param fine_y_offset: the y offset of the fine map file
        :param coarse_file: the coarse map file to use (must be equal to or larger than fine map file)
        :param coarse_x: the x dimension of the coarse map file
        :param coarse_y: the y dimension of the coarse map file
        :param coarse_x_offset: the x offset of the coarse map file at the resolution of the fine map
        :param coarse_y_offset: the y offset of the coarse map file at the resoultion of the fine map
        :param coarse_scale: the relative scale of the coarse map compared to the fine map (must match x and y scaling)
        :param historical_fine_map: the historical fine map file to use (must have dimensions equal to fine map)
        :param historical_coarse_map: the historical coarse map file to use (must have dimensions equal to coarse map)
        """
        if not self.is_setup_map:
            self.sample_map.set_dimensions(sample_file, sample_x, sample_y)
            self.fine_map.set_dimensions(fine_file, fine_x, fine_y, fine_x_offset, fine_y_offset)
            self.coarse_map.set_dimensions(coarse_file, coarse_x, coarse_y, coarse_x_offset, coarse_y_offset)
            self.coarse_scale = coarse_scale
            self.historical_fine_map_file = historical_fine_map
            self.historical_coarse_map_file = historical_coarse_map
            self.is_setup_map = True
        else:  # pragma: no cover
            self.logger.warning("Map objects are already set up.")

    def detect_map_dimensions(self):
        """
        Detects all the map dimensions for the provided files (where possible) and sets the respective values.
        This is intended to be run after set_map_files()

        :raises TypeError: if a dispersal map or reproduction map is specified, we must have a fine map specified, but
                           not a coarse map.

        :raises IOError: if one of the required maps does not exist

        :raises ValueError: if the dimensions of the dispersal map do not make sense when used with the fine map
                            provided

        :return: None
        """
        self.fine_map.set_dimensions()
        if self.sample_map.file_name == "null":
            self.sample_map.set_dimensions(
                x_size=self.fine_map.x_size,
                y_size=self.fine_map.y_size,
                x_offset=self.fine_map.x_offset,
                y_offset=self.fine_map.y_offset,
            )
            self.sample_map.x_ul = self.fine_map.x_ul
            self.sample_map.y_ul = self.fine_map.y_ul
        else:
            self.sample_map.set_dimensions()
        x, y = self.fine_map.calculate_offset(self.sample_map)[0:2]
        self.fine_map.x_offset = -x
        self.fine_map.y_offset = -y
        if self.coarse_map.file_name in ["null", "none"]:
            tmpname = copy.deepcopy(self.coarse_map.file_name)
            self.coarse_map = copy.deepcopy(self.fine_map)
            self.coarse_scale = 1
            self.coarse_map.x_offset = 0
            self.coarse_map.y_offset = 0
            self.coarse_map.file_name = tmpname
        else:
            self.coarse_map.set_dimensions()
            self.coarse_map.x_offset = -self.coarse_map.calculate_offset(self.fine_map)[0]
            self.coarse_map.y_offset = -self.coarse_map.calculate_offset(self.fine_map)[1]
            self.coarse_scale = self.fine_map.calculate_scale(self.coarse_map)
        self.check_maps()

    def check_maps(self):
        """
        Checks that the maps all exist and that the file structure makes sense.

        :raises TypeError: if a dispersal map or reproduction map is specified, we must have a fine map specified, but
            not a coarse map.

        :raises IOError: if one of the required maps does not exist

        :return: None
        """
        # Now check that the rest of the map naming structures make sense.
        if self.historical_fine_map_file in {"none", None} and len(self.historical_fine_list) == 0:
            if self.historical_coarse_map_file not in {"none", None} or len(self.historical_coarse_list) > 1:
                raise ValueError("Historical fine map is none, but coarse map is not none.")
        if self.historical_coarse_map_file in {"none", None} and len(self.historical_coarse_list) == 0:
            if self.historical_fine_map_file not in {"none", None} or len(self.historical_fine_list) > 1:
                raise ValueError("Historical coarse map is none, but fine map is not none.")
        if self.fine_map.file_name == "none":
            raise ValueError("Fine map file cannot be none.")
        if self.coarse_map.file_name in {"none", None}:
            if self.historical_coarse_map_file not in {"none", None}:
                raise ValueError("Cannot have a historical coarse file with a coarse file of none.")
        else:
            if self.coarse_map.file_name != "null" and not self.fine_map.is_within(self.coarse_map):
                raise ValueError(
                    "Offsets mean that coarse map does not fully encompass fine map. Check that your"
                    " maps exist at the same spatial coordinates."
                )
        if self.sample_map.file_name != "null" and not self.sample_map.is_within(self.fine_map):
            raise ValueError(
                "Offsets mean that fine map does no	t fully encompass sample map. Check that your maps exist"
                " at the same spatial coordinates."
            )
        for map_file in [self.coarse_map, self.fine_map, self.sample_map]:
            map_file.check_map()
        for map_file in [self.historical_fine_map_file, self.historical_fine_map_file]:
            check_file_exists(map_file)
        if self.landscape_type == "tiled_fine":
            if self.coarse_map.file_name not in {None, "none"}:
                raise ValueError("Cannot use a coarse map with a tiled fine landscape.")
        if self.landscape_type == "tiled_coarse":
            if self.coarse_map.file_name in {None, "none"}:
                raise ValueError("Cannot use a tiled_coarse landscape without a coarse map.")
