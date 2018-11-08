// This file is part of necsim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
/**
 * @author Samuel Thompson
 * @file LandscapeMetricsCalculator.h
 * @brief Contains the LandscapeMetricsCalculator class for calculating landscape metrics.
 *
 * @copyright <a href="https://opensource.org/licenses/MIT"> MIT Licence.</a>
 */
#include<algorithm>
#include <vector>
#include <numeric>
#include "necsim/Map.h"
#include "necsim/Cell.h"

#ifndef MEAN_DISTANCE_MEANDISTANCECALCULATOR_H
#define MEAN_DISTANCE_MEANDISTANCECALCULATOR_H

using namespace std;

/**
 * @brief Calculates a variety of landscape metrics from an imported tif file.
 */
class LandscapeMetricsCalculator : public Map<double>
{
	vector<Cell> all_cells;
public:

	LandscapeMetricsCalculator() : all_cells(){};

	virtual ~LandscapeMetricsCalculator(){};

	/**
	 * @brief Calculates the mean distance between nearest neighbours on a Map.
	 * @return the mean distance between every cell and its nearest neighbour
	 */
	double calculateMNN();

	/**
	 * @brief Checks if the minimum distance between cells is a new minimum.
	 * @param home_cell the cell to check the distance from
	 * @param x the x coordinate of the new location
	 * @param y the y coordinate of the new location
	 * @param min_distance the previous minimum distance
	 */
	void checkMinDistance(Cell &home_cell, const long &x, const long &y, double &min_distance);

	/**
	 * @brief Determines the distance to the nearest neighbour of a cell.
	 * @param row
	 * @param col
	 * @return
	 */
	double findNearestNeighbourDistance(const long &row, const long &col);

	/**
	 * @brief Creates a list containing all habitat cells in the landscape.
	 * List is stored in all_cells.
	 */
	void createCellList();

	/**
	 * @brief Calculates the clumpiness metric, which measures the degree to which the focal habitat is aggregated or
	 * clumped given its total area.
	 * @return the clumpiness metric
	 */
	double calculateClumpiness();

	/**
	 * @brief Calculates the number of adjacencies in the landscape.
	 *
	 * Adjacencies are habitat cells that are directly next to each other. Note that this uses the "double=count"
	 * method.
	 * @return the number of adjacent cells in the landscape.
	 */
	unsigned long calculateNoAdjacencies();

	/**
	 * @brief Calculates the minimum bounding perimeter for square cells on a landscape.
	 * @return the minimum bounding perimeter for cells on a landscape
	 */
	double calculateMinPerimeter();

};

#endif //MEAN_DISTANCE_MEANDISTANCECALCULATOR_H
