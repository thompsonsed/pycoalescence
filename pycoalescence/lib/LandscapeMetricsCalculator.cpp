// This file is part of necsim project which is released under MIT license.
// See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
/**
 * @author Samuel Thompson
 * @file LandscapeMetricsCalculator.cpp
 * @brief Contains the LandscapeMetricsCalculator class for calculating landscape metrics.
 *
 * @copyright <a href="https://opensource.org/licenses/MIT"> MIT Licence.</a>
 */
#include "necsim/Matrix.h"
#include "necsim/Map.h"
#include "LandscapeMetricsCalculator.h"

double LandscapeMetricsCalculator::calculateMNN()
{
    vector<double> distances;
    for(unsigned long i = 0; i < getRows(); i++)
    {
        for(unsigned long j = 0; j < getCols(); j++)
        {
            if(get(i, j) != 0)
            {
                distances.push_back(findNearestNeighbourDistance(i, j));
            }
        }
    }
    if(distances.empty())
    {
        throw FatalException("No cells found on map. Cannot calculate distances.");
    }
    return accumulate(distances.begin(), distances.end(), 0.0) / distances.size();
}

void LandscapeMetricsCalculator::checkMinDistance(Cell &home_cell, const long &x, const long &y, double &min_distance)
{
    Cell this_cell{};
    this_cell.x = x;
    this_cell.y = y;
    if(this_cell != home_cell && get(y, x) > 0)
    {
        auto distance = distanceBetweenCells(home_cell, this_cell);
        if(distance >= 1.0)
        {
            min_distance = min(min_distance, distance);
        }
    }
}

double LandscapeMetricsCalculator::findNearestNeighbourDistance(const long &row, const long &col)
{
    long upper = min(static_cast<long>(getRows() - 1), row + 1);
    long lower = max(static_cast<long>(0), row - 1);
    long left = max(static_cast<long>(0), col - 1);
    long right = min(static_cast<long>(getCols() - 1), col + 1);
    long x = left;
    long y = lower;
    double min_distance = getRows() * getCols();
    Cell home_cell{};
    home_cell.x = col;
    home_cell.y = row;
    while(true)
    {
        x = left;
        y = lower;
        double min_distance_possible = min(right - left, upper - lower);
        // Four dimensions to check in
        while(x < right)
        {
            x++;
            checkMinDistance(home_cell, x, y, min_distance);
        }
        while(y < upper)
        {
            y++;
            checkMinDistance(home_cell, x, y, min_distance);
        }
        while(x > left)
        {
            x--;
            checkMinDistance(home_cell, x, y, min_distance);
        }
        while(y > lower)
        {
            y--;
            checkMinDistance(home_cell, x, y, min_distance);
        }
        // Expand the grid by 1 in all dimensions.
        if(lower > 0)
        {
            lower--;
        }
        if(upper < static_cast<long>(getRows()) - 1)
        {
            upper++;
        }
        if(left > 0)
        {
            left--;
        }
        if(right < static_cast<long>(getCols()) - 1)
        {
            right++;
        }
#ifdef DEBUG
        if(left < 0 || left >= getCols() ||
                right < 0 || right >= getCols() ||
                lower < 0 || lower >= getRows() ||
                upper < 0 || upper >= getRows())
        {
            stringstream ss;
            ss << "Bounds out of range. Please report this bug." << endl;
            ss << "t, b, l, r: " << upper << ", " << lower << ", " << left << ", " << right << endl;
            throw FatalException(ss.str());
        }
#endif
        if(min_distance < min_distance_possible)
        {
            break;
        }
    }
    return min_distance;
}

void LandscapeMetricsCalculator::createCellList()
{
    for(unsigned long i = 0; i < getRows(); i++)
    {
        for(unsigned long j = 0; j < getCols(); j++)
        {
            if(get(i, j) != 0)
            {
                Cell cell;
                cell.x = j;
                cell.y = i;
                all_cells.emplace_back(cell);
            }
        }
    }
    stringstream ss;
    ss << "Detected " << all_cells.size() << " cells" << endl;
    writeInfo(ss.str());
}

double LandscapeMetricsCalculator::calculateClumpiness()
{
    createCellList();
    double P = static_cast<double>(all_cells.size()) / static_cast<double>(getCols() * getRows());
    unsigned long totalAdj = calculateNoAdjacencies();
    unsigned long totalNonAdj = (all_cells.size() * 8) - totalAdj;
    double minPerimeter = calculateMinPerimeter();
    double G = totalAdj / (totalAdj + totalNonAdj - minPerimeter);
    if(G < P && P < 0.5)
    {
        return (G - P) / P;
    }
    else if(P == 1.0)
    {
        return 1.0;
    }
    else
    {
        return (G - P) / (1 - P);
    }
}

unsigned long LandscapeMetricsCalculator::calculateNoAdjacencies()
{
    unsigned long totalAdj = 0;
    for(const auto &home_cell : all_cells)
    {
        for(long x = -1; x <= 1; x++)
        {
            for(long y = -1; y <= 1; y++)
            {
                if(!(x == 0 && y == 0))
                {
                    Cell this_cell;
                    this_cell.x = x + home_cell.x;
                    this_cell.y = y + home_cell.y;
                    if(this_cell.x >= 0 && this_cell.x < static_cast<long>(getCols()) &&
                       this_cell.y >= 0 && this_cell.y < static_cast<long>(getRows()))
                    {
                        if(get(this_cell.y, this_cell.x) >= 1.0)
                        {
                            totalAdj++;
                        }
                    }
                }
            }
        }
    }
    return totalAdj;
}

double LandscapeMetricsCalculator::calculateMinPerimeter()
{
    // Based on http://www.umass.edu/landeco/research/fragstats/documents/Metrics/
    // Contagion%20-%20Interspersion%20Metrics/Metrics/C115%20-%20CLUMPY.htm
    double largestIntegerSquare = floor(pow(all_cells.size(), 0.5));
    double m = all_cells.size() - pow(largestIntegerSquare, 2);
    if(m == 0)
    {
        return 4 * largestIntegerSquare;
    }
    else if(pow(largestIntegerSquare, 2.0) < all_cells.size() &&
            all_cells.size() <= largestIntegerSquare * (1 + largestIntegerSquare))
    {
        return (4 * largestIntegerSquare) + 2;
    }
    else
    {
        return (4 * largestIntegerSquare) + 4;
    }
}




