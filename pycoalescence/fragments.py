"""
Generate fragmented landscapes with specific properties. Detailed :ref:`here <Simulate_landscapes>`.

Contains :class:`.FragmentedLandscape` for creating a fragmented landscape using hexagonal packing and an even spread of
individuals between fragments. Requires scipy and matplotlib.
"""

import copy
import math
import os
import numpy as np
import logging
import sys
try:
	from matplotlib.pyplot import figure
	from matplotlib import pyplot as plt
except (ImportError, RuntimeError) as ie:
	logging.warning(ie)
try:
	from osgeo import gdal
except ImportError as ie:
	try:
		import gdal
	except ImportError:
		raise ie
from .spatial_algorithms import lloyds_algorithm, archimedes_spiral
from .system_operations import check_parent
from .future_except import FileExistsError

class Fragment:
	"""
	Simple class containing the centres of fragments for a fragmented landscape
	"""
	def __init__(self, x=None, y=None):
		"""
		Default initiator

		:param x: the x position of the fragment centre
		:param y: the y position of the fragment centre

		:rtype: None
		"""
		self.x = 0
		self.y = 0
		self.size = 0
		self.counter = 0
		if x and y:
			self.setup(x, y)

	def setup(self, x, y):
		"""
		Sets up the fragment from the x and y position.

		:param x: the x position of the fragment centre
		:param y: the y position of the fragment centre

		:rtype: None
		"""
		self.x = copy.copy(x)
		self.y = copy.copy(y)

	def place_on_grid(self):
		"""
		Changes the x and y positions to integers (always rounds down).

		:rtype: None
		"""
		self.x = int(math.floor(self.x))
		self.y = int(math.floor(self.y))


class FragmentedLandscape():
	"""
	Contains hexagonal packing algorithms for spacing clumps evenly on the landscape. Includes a LLoyd's smoothing
	algorithm for better spacing of fragments.

	.. note::

		Fragments will not be distinct units for unfragmented landscapes (with above around 50% habitat cover).

	"""

	def __init__(self, number_fragments=None, size=None, total=None, output_file=None):
		"""
		Initiates the FragmentLandscape object with the supplied parameters.

		:param number_fragments: the number of individual fragments to exist on the landscape
		:param size: the size of the x and y dimensions of the landscape
		:param total: the total number of individuals to place on the landscape
		:param output_file: the output tif file to write the output to

		:rtype: None
		"""
		self.number_fragments = 0
		self.size = 0
		self.output_file = None
		# upper bound for the number of x, y dimensions required
		self.number_rows = 0
		self.number_cols = 0
		self.is_shrunk = False  # this will be true if this height is less than the width
		self.total_added = 0
		self.remainder = 0  # if this number is 0, we have no more extra points to add
		self.needs_voronoi = False
		self.total = 0
		self.grid = None
		self.fragments = None
		if number_fragments and size and total and output_file:
			self.setup(number_fragments, size, total, output_file)

	def setup(self, number_fragments, size, total, output_file):
		"""
		Sets up the landscape by checking parameters and setting object sizes.

		:param number_fragments: the number of individual fragments to exist on the landscape
		:param size: the size of the x and y dimensions of the landscape
		:param total: the total number of individuals to place on the landscape
		:param output_file: the output tif file to write the output to

		:rtype: None
		"""
		self.number_fragments = number_fragments
		self.size = size
		self.total = total
		self.output_file = output_file
		self.grid = np.zeros(shape=[size, size], dtype=np.int)
		self.fragments = [None for _ in range(self.number_fragments)]
		self._precursory_validation(number_fragments, size, total)

	def generate(self, override_smoothing=None, n=10):
		"""
		Convenience function for creating fragments in one function. Generates the landscape and writes out to the
		output file.

		If smoothing is true, will run Lloyd's algorithm
		after the hexagonal packing algorithm to increase the equality of the spacing.

		.. note:: smoothing is recommended for any landscape that is doesn't contain a square number of fragments.

		:param override_smoothing: if true, overrides the default smoothing settings (enabled for landscapes with fewer
			than 100000 fragments.
		:param n: the number of iterations to run Lloyd's algorithm for

		:rtype: None
		"""
		self._check_file_and_path()
		self.create(override_smoothing=override_smoothing, n=n)
		self.write_to_raster()

	def create(self, override_smoothing=None, n=10):
		"""
		Creates the landscape, including running the hexagonal packing and smoothing algorithms (if required).

		.. note:: smoothing is recommended for any landscape that is doesn't contain a square number of fragments.

		:param override_smoothing: if true, overrides the default smoothing settings (enabled for landscapes with fewer
			than 100000 fragments.

		:param n: the number of iterations to run Lloyd's algorithm for

		:rtype: None
		"""
		smoothing = True
		if override_smoothing:
			smoothing = override_smoothing
		elif self.number_fragments > 10000:
			smoothing = False
		self.place_fragments(smoothing=smoothing, n=n)
		self.fill_grid()

	def _check_file_and_path(self):
		"""
		Checks that the file does not already exist and the file path exists.

		:raises FileExistsError if the file already exists.

		:param file: the file to check for

		:rtype: None
		"""
		if self.output_file is None:
			raise FileExistsError("File is None")
		if os.path.exists(self.output_file):
			raise FileExistsError("File already exists at {}.".format(self.output_file))
		check_parent(self.output_file)

	def place_fragments(self, smoothing=True, n=10):
		"""
		Places the fragments evenly on the landscape. If smoothing is true, will run Lloyd's algorithm after the
		hexagonal packing algorithm to increase the equality of the spacing.

		.. note:: smoothing is recommended for any landscape that is doesn't contain a square number of fragments.

		:param smoothing: if true, runs Lloyd's algorithm after the hexagonal packing
		:param n: the number of iterations to run Lloyd's algorithm for

		:rtype: None
		"""
		self._calculate_dimensions()
		self._place_initial_grid()
		self._add_remainders()
		self._scale_fragment_centres()
		if smoothing:
			self._smooth_points(n=n)

	def fill_grid(self):
		"""
		Distributes the sizes evenly between the fragments, generating the actual landscape.

		:rtype: None
		"""
		self._fill_fragments()
		for fragment in self.fragments:
			fragment.place_on_grid()
			self._fill_next_cell(fragment.x, fragment.y, 0.1, 0, fragment.size)
		self._final_validation()

	def _fill_fragments(self):
		"""
		Generates the sizes for the fragments, splitting the sizes as evenly across the landscape as possible

		:rtype: None
		"""
		lower_size = math.floor(self.total / self.number_fragments)
		running_total = 0
		for fragment in self.fragments:
			fragment.size = lower_size
			running_total += lower_size
		i = 0
		diff = self.total - running_total
		if diff != 0:
			increment = self.number_fragments / diff
			while running_total < self.total:
				self.fragments[int(math.floor(i))].size += 1
				i += increment
				if i >= self.number_fragments:
					i = i % self.number_fragments
				running_total += 1
		running_total = 0
		for frag in self.fragments:
			running_total += frag.size
		if running_total > self.total:
			raise ValueError("Generated total greater than expected total: {} > {}".format(running_total, self.total))

	def _fill_next_cell(self, cell_x, cell_y, radius, theta, size):
		"""
		Fills the next cell from the given point by spiralling outwards until it reaches a cell that is empty.

		This uses the archimedian spiral formula from the centre of fragments and calls itself recursively to generate
		the new points.

		:raises TypeError: if the grid is too small for the number of points to add.

		:param cell_x: the x coordinate of the centre of the spiral
		:param cell_y: the y coordinate of the centre of the spiral
		:param radius: the radius for the archimedian spiral. This is increased as cells are checked
		:param theta: the angle for the archimedian spiral. This is increased as cells are checked
		:param size: the number of individuals yet to place

		:rtype: None
		"""
		try:
			# Use the archimedian spiral formula
			while size > 0:
				check_x, check_y = archimedes_spiral(cell_x, cell_y, radius, theta)
				check_x = check_x % self.size
				check_y = check_y % self.size
				while self.grid[check_x, check_y] > 0:
					theta += 0.1 * math.pi / (2 * max(radius, 1))
					radius = theta / (2 * math.pi)
					check_x, check_y = archimedes_spiral(cell_x, cell_y, radius, theta)
					check_x = check_x % self.size
					check_y = check_y % self.size
					if radius > self.size:
						raise TypeError("Grid too small for adding fragment sizes!")
				self.grid[check_x, check_y] = 1
				size -= 1
		except IndexError as ie:
			errmsg = "Error placing points. Please report this bug: {}".format(ie)
			raise SystemError(errmsg)

	def _calculate_dimensions(self):
		"""
		Calculates the dimensions of the landscape in terms of columns and rows of fragments.

		:rtype: None
		"""
		if self.number_fragments == 2:
			self.number_rows = 1
			self.number_cols = 1
			self.remainder = 1
		else:
			self.number_rows = math.ceil(math.sqrt(self.number_fragments))
			if math.pow(self.number_rows, 2) == self.number_fragments:
				# Then the case is very basic. Yay!
				self.number_cols = self.number_rows
			else:
				# Should use Lloyd's algorthim with Voronoi diagrams
				self.number_cols = math.floor(math.sqrt(self.number_fragments))
				self.remainder = self.number_fragments - math.pow(self.number_cols, 2)

	def _place_initial_grid(self):
		"""
		Places the initial points on the grid, without worrying about the remainders.

		This is a very basic hexagonal packing algorithm.

		:rtype: None
		"""
		for x in range(int(self.number_cols)):
			for y in range(int(self.number_cols)):
				if y % 2 != 0:
					# offset the odd indices
					self.fragments[self.total_added] = Fragment(x + 1, y + 0.5)
				else:
					self.fragments[self.total_added] = Fragment(x + 0.5, y + 0.5)
				self.total_added += 1

	def _add_remainders(self):
		"""
		Adds the remainder points to the outside of the grid, adding to odd columns, from the inside out.

		:rtype: None
		"""
		if self.total_added + self.remainder != self.number_fragments:
			raise ValueError("Total added ({}) plus remainder ({}) != the number of fragments ({})."
							 " Please report this bug.".format(self.total_added, self.remainder, self.number_fragments))
		tot = 0
		if self.remainder > 0:
			iteration = self.number_cols / self.remainder
			while self.remainder > self.number_cols:
				self.fragments[self.total_added] = Fragment(self.number_cols + 0.5, tot)
				self.remainder -= 1
				self.total_added += 1
				tot += iteration
			while self.remainder > 0:
				self.fragments[self.total_added] = Fragment(self.remainder - 0.5, self.number_cols + 0.5)
				self.remainder -= 1
				self.total_added += 1

	def _scale_fragment_centres(self):
		"""
		Scales the fragment centres from their values so that they correctly cover the whole landscape.

		:rtype: None
		"""
		maximum_x = max([each.x for each in self.fragments]) + 0.5
		maximum_y = max([each.y for each in self.fragments]) + 0.5
		scaling_x = self.size / maximum_x
		scaling_y = self.size / maximum_y
		for fragment in self.fragments:
			fragment.x *= scaling_x
			fragment.y *= scaling_y

	def _smooth_points(self, n=10):
		"""
		Smooth the points using Lloyd's algorithm so that they are more evenly spaced. Increase n to increase the number
		of iterations of Lloyd's algorithm and increase the convergence.

		Note that LLoyd's algorithm only finds a local solution for equal distances between points.

		:param n: the number of iterations of Lloyd's algorithm (higher is more even spacing)

		:rtype: None
		"""
		points = [[fragment.x, fragment.y] for fragment in self.fragments]
		maxima = (self.size, self.size)
		new_points = lloyds_algorithm(points_list=points, maxima=maxima, n=n)
		for i, fragment in enumerate(self.fragments):
			fragment.x, fragment.y = new_points[i]

	def _precursory_validation(self, number_fragments, size, total):
		"""
		Checks that the dimensions and numbers make sense.

		:raises ValueError: if the combination of parameters does not make sense.
		"""
		if number_fragments > size * size:
			raise ValueError("Cannot add more fragments than cells on the grid.")
		if number_fragments > total:
			raise ValueError("Cannot add more fragments than total individuals.")
		if total > size * size:
			raise ValueError("Cannot add more individuals than cells on the grid.")

	def _final_validation(self):
		"""
		Checks that the number of fragments is correct, that each fragment exists within the plot and

		:raises ValueError: if any of the validation checks fail

		:rtype: None
		"""
		try:
			if len(self.fragments) != self.total_added:
				raise ValueError("Fragment number not correct. Please report this bug.")
			for fragment in self.fragments:
				if not 0 <= fragment.x <= self.size or not 0 <= fragment.y <= self.size:
					raise ValueError("Fragments not set up correctly. Please report this bug.")
			if self.remainder != 0:
				raise ValueError("Remainders not correct. Please report this bug.")
			if np.sum(self.grid) != float(self.total):
				raise ValueError("Total does not equal size: {} != {}.".format(np.sum(self.grid),
																			   float(self.total)))
		except ValueError as ve:
			raise ValueError("Validation failed: {}".format(ve))

	def write_to_raster(self):
		"""
		Writes the landscape to a tif file.

		:raises FileExistsError: if the output file already exists

		:param output_file: the path to the tif file to write out to.

		:rtype: None
		"""
		self._check_file_and_path()
		geotransform = (0, 1, 0, 0, 0, -1)
		# Stupid attempt to fix the no data issue for writing out numpy arrays
		for i in range(self.size):
			if self.grid[i, i] == 0:
				self.grid[i, i] == 0
		output_raster = gdal.GetDriverByName('GTiff').Create(self.output_file,
															 self.size, self.size, 1,
															 gdal.GDT_Byte)
		if not output_raster:
			raise IOError("Could not create tif file at {}.".format(self.output_file))
		output_raster.SetGeoTransform(geotransform)
		out_band = output_raster.GetRasterBand(1)
		out_band.WriteArray(self.grid)
		out_band.FlushCache()
		out_band.SetNoDataValue(-99)
		del output_raster

	def plot(self):
		"""
		Returns a matplotlib.pyplot.figure object containing an image of the fragmented landscape (with axes removed).

		Requires that the fragmented landscape has been created already using :meth:`~create`.

		:return: figure object containing the fragmented landscape.
		:rtype: matplotlib.pyplot.figure
		"""
		fig = plt.figure()
		fig.figimage(self.grid, cmap="Greys_r", resize=True)
		return fig