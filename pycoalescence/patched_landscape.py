"""

Generate landscapes of interconnected patches for simulating within a spatially explicit neutral model.
Detailed :ref:`here <generate_landscapes>`.

Dispersal probabilities are defined between different patches, and each patch will be contain n individuals.
"""
from __future__ import division

import csv
import math
import os
import sys

import numpy as np

from .map import Map
from .system_operations import check_parent


class Patch(object):
    """
    Contains a single patch, to which the probability of dispersal to every other patch can be added.
    """

    def __init__(self, id, density):
        """
        Generates the patch object with a fixed density and id.

        :param id: the name for the fragment as a unique identifier.
        :param density: the number of individuals that exist (non-spatially) within this patch.
        """
        self.density = density
        self.id = id
        self.dispersal_probabilities = {}
        self.index = 0

    def __repr__(self):
        """
        Representation of the object.
        """
        return "Patch({}, {})".format(self.id, self.density)

    def __str__(self):
        """
        Prints the patch data to a string.
        :return: string containing the object data
        """
        str = "Patch class object with id: {}, density: {}," " index: {} and dispersal probabilities: {}".format(
            self.id, self.density, self.index, self.dispersal_probabilities
        )
        return str

    def add_patch(self, patch, probability):
        """
        Adds dispersal from this patch to another patch object with a set probability. The patch should not already
        have been added.

        .. note:: The probabilities can be relative, as they can be re-scaled to sum to 1 using
                  :func:`re_scale_probabilities`.

        :raises KeyError: if the patch already exists in the dispersal probabilities.

        :raises ValueError: if the dispersal probability is less than 0.

        :param patch: the patch id to disperse to
        :param probability: the probability of dispersal
        """
        if probability < 0:
            raise ValueError("Dispersal probability should be > 0")
        if patch in self.dispersal_probabilities.keys():
            raise KeyError("Patch {} already exists in dispersal probabilities.".format(patch))
        self.dispersal_probabilities[patch] = probability

    def re_scale_probabilities(self):
        """
        Re-scales the probabilities so that they sum to 1. Also checks to make sure dispersal from within this patch
        is defined.

        :raises ValueError: if the self dispersal probability has not been defined, or the dispersal probabilities do
                            not sum to > 0.
        """
        has_self = False
        total = 0
        for key, value in self.dispersal_probabilities.items():
            if key == self.id:
                has_self = True
            if value < 0:
                raise ValueError("Dispersal probabilities must be >= 0, currently {}.".format(value))
            total += value
        if total <= 0:
            raise ValueError("Dispersal probabilities must sum to > 0, currently {}.".format(total))
        if not has_self:
            raise ValueError("Self-dispersal probability has not been defined, please add first.")
        for key, value in self.dispersal_probabilities.items():
            self.dispersal_probabilities[key] = value / total


class PatchedLandscape:
    """
    Landscape made up of a list of patches with dispersal probabilities to each other.
    """

    def __init__(self, output_fine_map, output_dispersal_map):
        """
        Creates the patched landscape object, providing the paths to the fine map (for outputting the density) and
        dispersal map.

        :raises IOError: if either output_fine_map or output_dispersal_map exist.

        :param output_fine_map: path to the fine map to create, which will contain the densities
        :param output_dispersal_map: path to the dispersal map, which will contain dispersal probabilities
        """
        if os.path.exists(output_fine_map):
            raise IOError("Output fine map already exists at {}.".format(output_fine_map))
        if os.path.exists(output_dispersal_map):
            raise IOError("Output dispersal map already exists at {}.".format(output_dispersal_map))
        check_parent(output_fine_map)
        check_parent(output_dispersal_map)
        self.fine_map = Map()
        self.fine_map.file_name = output_fine_map
        self.dispersal_map = Map()
        self.dispersal_map.file_name = output_dispersal_map
        self.patches = {}

    def __repr__(self):
        """
        Representation of the object.

        :return: string containing the representation of the object.
        """
        return "PatchedLandscape({}, {})".format(self.fine_map.file_name, self.dispersal_map.file_name)

    def add_patch(self, id, density, self_dispersal=None, dispersal_probabilities=None):
        """
        Add a patch with the given parameters.

        :param id: the unique reference for the patch
        :param density: the number of individuals that exist in the patch
        :param self_dispersal: the relative probability of dispersal from within the same patch
        :param dispersal_probabilities: dictionary containing all other patches and their relative dispersal
               probabilities
        """
        if self.has_patch(id):
            raise KeyError("Patch with id of {} already in patch list.".format(id))
        if density <= 0:
            raise ValueError("Density cannot be less than 0.")
        if self_dispersal is None:
            if dispersal_probabilities is None:
                raise TypeError("Must provide self-dispersal value.")
        patch = Patch(id, density)
        patch.add_patch(id, self_dispersal if self_dispersal is not None else 0.0)
        if dispersal_probabilities:
            if not isinstance(dispersal_probabilities, dict):
                raise TypeError(
                    "Dispersal probabilities must be provided as a dictionary of " "ids->relative probabilities."
                )
            if self_dispersal is None:
                if id not in dispersal_probabilities.keys():
                    raise KeyError("Must provide self dispersal value either separately or within dictionary.")
                patch.dispersal_probabilities[id] = dispersal_probabilities[id]
            for key, value in dispersal_probabilities.items():
                if key != id:
                    patch.add_patch(key, value)
        self.patches[id] = patch

    def has_patch(self, id):
        """
        Checks if the patches object already contains a patch with the provided id.

        :param id: id to check for in patches

        :return: true if the patch already exists
        """
        return id in self.patches.keys()

    def add_dispersal(self, source_patch, target_patch, dispersal_probability):
        """
        Adds a dispersal probability from the source patch to the target patch.

        .. note:: Both the source and target patch should already have been added using :func:`add_patch`.

        :param source_patch: the id of the source patch
        :param target_patch: the id of the target patch
        :param dispersal_probability: the probability of dispersal from source to target
        """
        if source_patch not in self.patches.keys():
            raise ValueError("Source patch {} has not been added.".format(source_patch))
        if target_patch not in self.patches.keys():
            raise ValueError("Target patch {} has not been added.".format(target_patch))
        self.patches[source_patch].add_patch(target_patch, dispersal_probability)

    def generate_files(self):
        """
        Re-scales the dispersal probabilities and generates the patches landscape files. These include the fine map file
        containing the densities and the dispersal probability map.

        The fine map file will be dimensions 1xN where N is the number of patches in the landscape.
         The dispersal probability map will be dimensions NxN, where dispersal occurs from the y index cell to the x
         index cell.
        """
        map_size = len(self.patches)
        self.fine_map.data = np.zeros(shape=(1, map_size))
        self.dispersal_map.data = np.zeros(shape=(map_size, map_size))
        # Assign indices to each patch
        index = 0
        for key, value in self.patches.items():
            self.patches[key].index = index
            self.patches[key].re_scale_probabilities()
            index += 1
        for k1, src_patch in self.patches.items():
            src_index = src_patch.index
            self.fine_map.data[0, src_index] = src_patch.density
            if len(src_patch.dispersal_probabilities) == 0:  # pragma: no cover
                raise ValueError("No dispersal probabilities supplied in patch {}".format(src_patch.id))
            for k2, dst_patch in self.patches.items():
                dst_index = dst_patch.index
                if k2 not in src_patch.dispersal_probabilities.keys():
                    self.dispersal_map.data[src_index, dst_index] = 0.0
                else:
                    self.dispersal_map.data[src_index, dst_index] = src_patch.dispersal_probabilities[k2]
        self.fine_map.create(self.fine_map.file_name, datatype=5)
        self.dispersal_map.create(self.dispersal_map.file_name, datatype=6)

    def generate_fragment_csv(self, fragment_csv):
        """
        Generates a fragment csv for usage within a coalescence simulation, with each patch becomming one fragment on
        the landscape.

        :param fragment_csv: the path to the output csv to create

        :raises IOError: if the output fragment csv already exists
        """
        if os.path.exists(fragment_csv):
            raise IOError("Output file already exists at {}.".format(fragment_csv))
        check_parent(fragment_csv)
        if sys.version_info[0] < 3:  # pragma: no cover
            infile = open(fragment_csv, "wb")
        else:
            infile = open(fragment_csv, "w", newline="")
        with infile as csv_file:
            csv_writer = csv.writer(csv_file)
            for k1, patch in self.patches.items():
                csv_writer.writerow([k1, patch.index, 0, patch.index, 0, patch.density])

    def generate_from_matrix(self, density_matrix, dispersal_matrix):
        """
        Generates the patched landscape from the input matrix and writes out to the files.

        .. note:: Uses a slightly inefficient method of generating the full patched landscape, and then writing back out
                  to the map files so that full error-checking is included. A more efficient implementation is possible
                  by simply writing the matrix to file using the :class:`Map class <pycoalescence.map.Map>`.

        .. note:: The generated density map will have dimensions 1 by xy (where x, y are the dimensions of the original
                  density matrix. However, the dispersal matrix should still be compatible with the original density
                  matrix as a x by y tif file.

        :param density_matrix: a numpy matrix containing the density probabilities
        :param dispersal_matrix: a numpy matrix containing the dispersal probabilities
        """
        if not isinstance(density_matrix, np.ndarray) or not isinstance(dispersal_matrix, np.ndarray):
            raise TypeError("Supplied matrices must be numpy arrays.")
        x_dim, y_dim = dispersal_matrix.shape
        x_density, y_density = density_matrix.shape
        if not x_density * y_density == x_dim or x_dim != y_dim:
            raise ValueError("Density matrix should have dimensions x by y and dispersal matrix xy by xy.")
        # create the patches first
        for y in range(y_dim):
            src_x, src_y = convert_index_to_x_y(y, x_density)
            src_density = density_matrix[src_y, src_x]
            self.add_patch(y, src_density, dispersal_matrix[y, y])
        for y in range(y_dim):
            for x in range(x_dim):
                if x != y:
                    self.add_dispersal(y, x, dispersal_matrix[y, x])
        self.generate_files()


def convert_index_to_x_y(index, dim):
    """
    Converts an index to an x, y coordinate.

    Used when mapping from 1-D space to 2-D space.

    :param index: the index to convert from
    :param dim: the x dimension of the matrix

    :return: a tuple of integers containing the x and y coordinates
    :rtype: tuple
    """
    density_x = index % dim
    density_y = math.floor(index / dim)
    return int(density_x), int(density_y)
